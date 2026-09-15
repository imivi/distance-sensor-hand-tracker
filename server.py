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
SERIAL_BAUD = 115200
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


import csv
from datetime import datetime
from pathlib import Path
import uuid

RECORDINGS_DIR = Path(__file__).parent / "recordings"
RECORDINGS_DIR.mkdir(exist_ok=True)
CSV_FILE_PATH = RECORDINGS_DIR / "gestures.csv"


class GestureRecorder:
    def __init__(self):
        self.target_letter: str | None = None
        self.state: str = "idle"  # "idle", "waiting_for_hand", "recording"
        self.samples: list[dict] = []
        self.start_time: float | None = None
        self.last_x: float | None = None
        self.last_y: float | None = None
        self.current_recording_id: str | None = None

    def start(self, letter: str):
        self.target_letter = letter.upper()
        self.state = "waiting_for_hand"
        self.samples = []
        self.start_time = None
        self.last_x = None
        self.last_y = None
        self.current_recording_id = str(uuid.uuid4())[:8]  # Unique 8-character ID
        logger.info(
            "Recording requested for letter '%s' (ID: %s, waiting for hand)",
            self.target_letter,
            self.current_recording_id,
        )

    def stop(self) -> dict | None:
        """Stops recording immediately and appends to the unified CSV file."""
        if self.state == "idle":
            return None

        saved_letter = self.target_letter
        recording_id = self.current_recording_id
        sample_count = len(self.samples)
        saved_filename = self._save_csv() if sample_count > 0 else None

        self.state = "idle"
        self.target_letter = None
        self.samples = []
        self.start_time = None
        self.last_x = None
        self.last_y = None
        self.current_recording_id = None

        if saved_filename:
            logger.info(
                "Recording stopped! Saved %d points for letter '%s' (ID: %s) to %s",
                sample_count,
                saved_letter,
                recording_id,
                saved_filename,
            )
            return {
                "recording_status": "finished",
                "letter": saved_letter,
                "recording_id": recording_id,
                "filename": saved_filename,
                "samples": sample_count,
            }
        else:
            logger.info("Recording stopped by user with 0 samples. Discarded.")
            return {
                "recording_status": "cancelled",
                "letter": saved_letter,
            }

    def cancel(self) -> dict | None:
        """Aborts recording immediately without saving any samples to CSV."""
        if self.state == "idle":
            return None

        saved_letter = self.target_letter
        sample_count = len(self.samples)

        self.state = "idle"
        self.target_letter = None
        self.samples = []
        self.start_time = None
        self.last_x = None
        self.last_y = None
        self.current_recording_id = None

        logger.info(
            "Recording cancelled by user for letter '%s' (discarded %d samples)",
            saved_letter,
            sample_count,
        )
        return {
            "recording_status": "cancelled",
            "letter": saved_letter,
            "samples": sample_count,
        }

    def process_point(
        self, target_x: float | None, target_y: float | None
    ) -> dict | None:
        """Processes current hand position and logs points while recording.
        Only saves full pairs of (X, Y) coordinates; skips if any axis is inactive."""
        if self.state == "idle":
            return None

        has_full_pair = target_x is not None and target_y is not None

        if self.state == "waiting_for_hand":
            if has_full_pair:
                self.state = "recording"
                self.start_time = asyncio.get_event_loop().time()
                self.samples.append(
                    {
                        "timestamp": 0.0,
                        "x": round(target_x, 2),
                        "y": round(target_y, 2),
                    }
                )
                logger.info(
                    "Hand detected with full XY pair! Recording started for letter '%s' (ID: %s)",
                    self.target_letter,
                    self.current_recording_id,
                )
                return {
                    "recording_status": "recording",
                    "letter": self.target_letter,
                    "recording_id": self.current_recording_id,
                }
            return None

        if self.state == "recording":
            # Only save full pairs of (X, Y) values
            if has_full_pair:
                t_rel = asyncio.get_event_loop().time() - self.start_time
                self.samples.append(
                    {
                        "timestamp": round(t_rel, 3),
                        "x": round(target_x, 2),
                        "y": round(target_y, 2),
                    }
                )
            return None

    def _save_csv(self) -> str:
        file_exists = CSV_FILE_PATH.exists()
        timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(CSV_FILE_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(
                    ["recording_id", "created_at", "letter", "time_s", "x_cm", "y_cm"]
                )
            for s in self.samples:
                writer.writerow(
                    [
                        self.current_recording_id,
                        timestamp_now,
                        self.target_letter,
                        s["timestamp"],
                        s["x"],
                        s["y"],
                    ]
                )

        return CSV_FILE_PATH.name


import joblib
from features import extract_features

MODEL_PATH = Path(__file__).parent / "models" / "gesture_rf.joblib"


class GestureClassifier:
    def __init__(self):
        self.model = None
        self.classes = []
        self.points: list[tuple[float, float]] = []
        self.is_active = False  # active when user starts gesture test mode
        self.load_model()

    def load_model(self) -> bool:
        if MODEL_PATH.exists():
            try:
                data = joblib.load(MODEL_PATH)
                self.model = data["model"]
                self.classes = data["classes"]
                logger.info(
                    "GestureClassifier loaded model with classes: %s", self.classes
                )
                return True
            except Exception as e:
                logger.error("Failed to load model from %s: %s", MODEL_PATH, e)
                self.model = None
                return False
        logger.warning("No trained model found at %s", MODEL_PATH)
        return False

    def start_inference(self):
        self.is_active = True
        self.points = []
        logger.info("Gesture test / inference mode activated.")

    def stop_inference(self):
        self.is_active = False
        self.points = []
        logger.info("Gesture test / inference mode deactivated.")

    def add_point(self, x: float | None, y: float | None):
        if self.is_active and x is not None and y is not None:
            self.points.append((round(x, 2), round(y, 2)))

    def classify(self) -> dict | None:
        """Classifies accumulated gesture points and returns top predictions."""
        if not self.model:
            self.load_model()
            if not self.model:
                return {
                    "inference_error": "No trained model found. Please train the model first."
                }

        if len(self.points) < 4:
            return {"inference_error": "Gesture too short (less than 4 valid points)."}

        feats = extract_features(self.points)
        if feats is None:
            return {"inference_error": "Unable to extract features from points."}

        # Predict probabilities
        X = np.array([feats], dtype=np.float32)
        probs = self.model.predict_proba(X)[0]
        top_indices = np.argsort(probs)[::-1]

        predictions = []
        for idx in top_indices:
            predictions.append(
                {
                    "letter": self.classes[idx],
                    "confidence": round(float(probs[idx]), 3),
                }
            )

        best = predictions[0]
        logger.info(
            "Gesture classified as '%s' (%0.1f%% confidence, %d points)",
            best["letter"],
            best["confidence"] * 100,
            len(self.points),
        )
        return {
            "predicted_letter": best["letter"],
            "confidence": best["confidence"],
            "predictions": predictions[:4],
            "points_count": len(self.points),
        }


recorder = GestureRecorder()
classifier = GestureClassifier()


def resolve_pythagorean_axis(
    d_start: float | None, d_end: float | None, total_dist: float
) -> float | None:
    if d_start is not None and d_end is not None:
        p = (d_start**2 - d_end**2 + total_dist**2) / (2.0 * total_dist)
        return max(0.0, min(p, total_dist))
    return None


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

                        # Compute Pythagorean position for recording
                        meas_y = resolve_pythagorean_axis(s2, s1, TOTAL_HEIGHT_CM)
                        meas_x = resolve_pythagorean_axis(s3, s4, TOTAL_WIDTH_CM)

                        rec_event = recorder.process_point(meas_x, meas_y)
                        if rec_event:
                            await manager.broadcast(rec_event)

                        # Feed valid points to classifier if test/inference mode is active
                        classifier.add_point(meas_x, meas_y)

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
                            "recording_state": recorder.state,
                            "recording_letter": recorder.target_letter,
                            "inference_active": classifier.is_active,
                            "inference_points": len(classifier.points),
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
            text = await websocket.receive_text()
            try:
                msg = json.loads(text)
                action = msg.get("action")
                if action == "start_recording":
                    letter = str(msg.get("letter", "")).upper()
                    if letter in "CLOZSUV" and len(letter) == 1:
                        # If already recording or waiting on this exact letter, stop it
                        if (
                            recorder.state != "idle"
                            and recorder.target_letter == letter
                        ):
                            stop_event = recorder.stop()
                            if stop_event:
                                await manager.broadcast(stop_event)
                        else:
                            recorder.start(letter)
                            await manager.broadcast(
                                {
                                    "recording_status": "waiting_for_hand",
                                    "letter": letter,
                                }
                            )
                elif action == "stop_recording":
                    stop_event = recorder.stop()
                    if stop_event:
                        await manager.broadcast(stop_event)
                elif action == "cancel_recording":
                    cancel_event = recorder.cancel()
                    if cancel_event:
                        await manager.broadcast(cancel_event)
                elif action == "start_inference":
                    # If recording was on, stop it
                    if recorder.state != "idle":
                        recorder.cancel()
                    classifier.start_inference()
                    await manager.broadcast(
                        {
                            "inference_status": "active",
                            "message": "Draw gesture now. Click 'Classify' or finish movement.",
                        }
                    )
                elif action == "classify_gesture":
                    res = classifier.classify()
                    classifier.stop_inference()
                    if res:
                        await manager.broadcast({"inference_result": res})
                elif action == "stop_inference":
                    classifier.stop_inference()
                    await manager.broadcast({"inference_status": "idle"})
                elif action == "train_model":
                    # Run training in background thread
                    from train_classifier import train_and_save

                    await asyncio.to_thread(train_and_save)
                    reloaded = classifier.load_model()
                    await manager.broadcast(
                        {
                            "train_status": "completed" if reloaded else "failed",
                            "classes": classifier.classes,
                        }
                    )
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
