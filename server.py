import asyncio
from collections import deque
import glob
import json
import logging
import os
import statistics
import sys
from contextlib import asynccontextmanager

import serial
import serial.tools.list_ports
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("sensor_server")

TOTAL_HEIGHT_CM = 51.0
TOTAL_WIDTH_CM = 49.0
SERIAL_BAUD = 9600
SERIAL_PORT = None
WINDOW_SIZE = 5


def find_serial_port() -> str | None:
    if SERIAL_PORT:
        return SERIAL_PORT

    # 1. First check explicit USB/ACM serial ports (Linux / macOS)
    usb_ports = (
        glob.glob("/dev/ttyUSB*")
        + glob.glob("/dev/ttyACM*")
        + glob.glob("/dev/cu.usb*")
    )
    if usb_ports:
        return usb_ports[0]

    # 2. Check pyserial's enumerated ports (Windows COM ports, or genuine hardware devices)
    # Ignore unused Linux legacy serial ports (/dev/ttyS*)
    for p in serial.tools.list_ports.comports():
        if p.device.startswith("/dev/ttyS"):
            continue
        return p.device

    return None


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("Client connected. Total clients: %d", len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(
                "Client disconnected. Total clients: %d", len(self.active_connections)
            )

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                disconnected.append(connection)
        for dead in disconnected:
            self.disconnect(dead)


manager = ConnectionManager()
serial_task = None


MAX_STEP_JUMP_CM = 10.0
MAX_OUTLIER_STREAK = 3


class SensorFilter:
    def __init__(self, max_dist: float, window_size: int = WINDOW_SIZE):
        self.max_dist = max_dist
        self.window = deque(maxlen=window_size)
        self.outlier_streak = 0

    def update(self, raw: float) -> float | None:
        # 1. Physical boundary check
        if raw < 0 or raw > self.max_dist:
            # If target genuinely disappeared, decay window
            if self.window:
                self.outlier_streak += 1
                if self.outlier_streak >= MAX_OUTLIER_STREAK:
                    self.window.clear()
                    self.outlier_streak = 0
            return round(statistics.median(self.window), 1) if self.window else None

        # 2. Outlier rejection: if we have recent readings, check for unrealistic sudden jumps
        if self.window:
            current_median = statistics.median(self.window)
            delta = abs(raw - current_median)

            if delta > MAX_STEP_JUMP_CM:
                self.outlier_streak += 1
                # If reading stays at new position for multiple consecutive frames, it's a real movement
                if self.outlier_streak < MAX_OUTLIER_STREAK:
                    # Ignore this outlier spike, return stable median
                    return round(current_median, 1)
                else:
                    # New position confirmed, reset window to new reading
                    self.window.clear()
                    self.outlier_streak = 0

        # Normal reading or confirmed transition
        self.outlier_streak = 0
        self.window.append(raw)
        return round(statistics.median(self.window), 1)


async def read_serial_loop():
    while True:
        port = find_serial_port()
        if not port:
            logger.warning("No serial port found. Retrying in 2 seconds...")
            await manager.broadcast(
                {
                    "status": "disconnected",
                    "message": "Arduino port not found",
                    "s1": None,
                    "s2": None,
                    "s3": None,
                    "s4": None,
                    "total_height": TOTAL_HEIGHT_CM,
                    "total_width": TOTAL_WIDTH_CM,
                }
            )
            await asyncio.sleep(2)
            continue

        try:
            logger.info("Opening serial port: %s at %d baud", port, SERIAL_BAUD)
            ser = serial.Serial(port, SERIAL_BAUD, timeout=1)
            # Flush existing buffer
            ser.reset_input_buffer()

            filter_s1 = SensorFilter(TOTAL_HEIGHT_CM, WINDOW_SIZE)
            filter_s2 = SensorFilter(TOTAL_HEIGHT_CM, WINDOW_SIZE)
            filter_s3 = SensorFilter(TOTAL_WIDTH_CM, WINDOW_SIZE)
            filter_s4 = SensorFilter(TOTAL_WIDTH_CM, WINDOW_SIZE)

            while True:
                line = await asyncio.to_thread(ser.readline)
                if not line:
                    continue

                decoded = line.decode("utf-8", errors="ignore").strip()
                if not decoded:
                    continue

                parts = decoded.split()
                if len(parts) >= 4:
                    try:
                        raw_s1 = float(parts[0])
                        raw_s2 = float(parts[1])
                        raw_s3 = float(parts[2])
                        raw_s4 = float(parts[3])

                        s1 = filter_s1.update(raw_s1)
                        s2 = filter_s2.update(raw_s2)
                        s3 = filter_s3.update(raw_s3)
                        s4 = filter_s4.update(raw_s4)

                        # If one of the two values on an axis is null, nullify the other
                        if s1 is None or s2 is None:
                            s1 = None
                            s2 = None

                        if s3 is None or s4 is None:
                            s3 = None
                            s4 = None

                        payload = {
                            "status": "connected",
                            # Filtered values paired per axis
                            "s1": s1,
                            "s2": s2,
                            "s3": s3,
                            "s4": s4,
                            # Raw instantaneous values
                            "raw_s1": raw_s1 if raw_s1 >= 0 else None,
                            "raw_s2": raw_s2 if raw_s2 >= 0 else None,
                            "raw_s3": raw_s3 if raw_s3 >= 0 else None,
                            "raw_s4": raw_s4 if raw_s4 >= 0 else None,
                            "total_height": TOTAL_HEIGHT_CM,
                            "total_width": TOTAL_WIDTH_CM,
                        }
                        await manager.broadcast(payload)
                    except ValueError:
                        continue

        except (serial.SerialException, OSError) as e:
            logger.error("Serial error: %s. Reconnecting in 2 seconds...", e)
            await manager.broadcast(
                {
                    "status": "disconnected",
                    "message": f"Serial connection lost: {e}",
                    "s1": None,
                    "s2": None,
                    "s3": None,
                    "s4": None,
                    "total_height": TOTAL_HEIGHT_CM,
                    "total_width": TOTAL_WIDTH_CM,
                }
            )
            await asyncio.sleep(2)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(read_serial_loop())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>index.html not found</h1>"


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive; accept any incoming ping/messages from client
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
