# Ultrasonic Hand Gesture Tracker & Classifier

Track hand gestures in mid-air and classify letters (`C, L, O, Z, S, U, V`) using 4 cheap ultrasonic sensors, an Arduino Nano, Python, and a Random Forest model.

No cameras, no gloves—just sound waves bouncing off your hand!

---

## How It Works

1. **The Frame**: 4 ultrasonic sensors (HC-SR04) sit on the edges of a 49 × 51 cm rectangle (Top, Bottom, Left, Right).
2. **Triangulation**: As you move your hand inside the frame, each sensor measures the distance. Using Pythagorean math (difference-of-squares), the math cancels out forward hand depth, giving clean 2D $(X, Y)$ coordinates.
3. **Live Web App**: An interactive web UI displays your hand's position in real time along with tracking crosshairs and 1D axis sliders.
4. **Gesture Recording**: Click a letter button (`C, L, O, Z, S, U, V`), wave your hand in the air to draw the letter, and click again to save the trajectory to a CSV dataset. A live red trail draws your stroke on screen as you move!
5. **AI Classification**: 
   - Converts each gesture into a simple **6×6 occupancy grid** (direction-independent: drawing a letter backwards or forwards produces the same shape).
   - Trains a **Random Forest classifier** on the recorded data.
   - Hit **Test Gesture** to draw any letter and see the model predict what letter you drew in real time with confidence scores.

---

## Hardware Setup

- **Microcontroller**: Arduino Nano (ATmega328P)
- **Sensors**: 4× HC-SR04 ultrasonic sensors
  - **S1 (Top)**: TRIG `D9`, ECHO `D10`
  - **S2 (Bottom)**: TRIG `D7`, ECHO `D8`
  - **S3 (Left)**: TRIG `D3`, ECHO `D4`
  - **S4 (Right)**: TRIG `D5`, ECHO `D6`
- **Baud Rate**: `115200`

---

## Quick Start

### 1. Flash the Arduino
```bash
pio run --target upload
```

### 2. Start the Backend Server
```bash
python server.py
```
Then open your browser to **`http://localhost:8000`**.

### 3. Record & Train
- **Record**: Click any letter button (`C`, `L`, `O`, etc.), draw it in the frame, and click the button again to save (or click `✕ Cancel` to discard).
- **Retrain**: Click **`🔄 Retrain Model`** right in the UI (or run `python train_classifier.py`).
- **Test**: Click **`⚡ Test Gesture`**, draw your letter in mid-air, and click **`Classify`** to see the prediction!

