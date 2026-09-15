# Ultrasonic Hand Gesture Tracker & Classifier

Track hand gestures in mid-air and classify letters (`C, L, O, Z, S, U, V`) using 4 cheap ultrasonic sensors, an Arduino Nano, Python, and a Random Forest model.

No cameras, no gloves—just sound waves bouncing off your hand!

---

## How It Works

1. **The Frame**: 4 ultrasonic sensors (HC-SR04) sit on the edges of a 49 × 51 cm rectangle (Top, Bottom, Left, Right).
2. **Triangulation**: As you move your hand inside the frame, each sensor measures the distance. Using Pythagorean math (difference-of-squares), forward hand depth cancels out completely, giving clean 2D $(X, Y)$ coordinates in centimeters.
3. **Live Web App**: An interactive web UI displays your hand's position in real time along with tracking crosshairs and 1D axis sliders.
4. **Gesture Recording**: Click a letter button (`C, D, G, J, L, M, N, O, P, S, U, V, W, Z`), wave your hand in the air to draw the letter, and click again to save the trajectory to a CSV dataset. A live red trail draws your stroke on screen as you move!
5. **AI Classification**: 
   - Converts each gesture into a normalized **6×6 occupancy grid** + shape dimensions (39 total features).
   - Trains a **Random Forest classifier** on the recorded data.
   - Hit **Test Gesture** to draw any letter and see the model predict what letter you drew in real time with confidence scores.

<p align="center">
  <img src="docs/assets/hardware_triangulation.svg" alt="Ultrasonic 2D Triangulation Frame" width="700"/>
</p>

---

## Data Processing Pipeline

Raw gesture data is a sequence of $(X, Y)$ points recorded over time. To make classification fast, robust, and **stroke-direction independent** (drawing a letter backwards or forwards produces the same representation), the data is processed through the following pipeline:

<p align="center">
  <img src="docs/assets/feature_pipeline.svg" alt="Gesture Feature Extraction Pipeline" width="850"/>
</p>

### 1. Bounding Box Normalization
* Finds the gesture's bounding box: `min_x`, `max_x`, `min_y`, `max_y`.
* Translates and scales the coordinates into a normalized `[0, 5]` range:
  $$\text{norm\_x} = \frac{x - \text{min\_x}}{\text{width}} \times 5, \quad \text{norm\_y} = \frac{y - \text{min\_y}}{\text{height}} \times 5$$
* **Why?** Makes the model **position-invariant**—it doesn't matter if you draw the letter in the top-left corner or the center of the frame.

### 2. 6×6 Occupancy Grid Rasterization (36 features)
* A $6 \times 6$ binary matrix (36 cells) represents spatial occupancy.
* Each cell is set to `1.0` if the hand passed through it, or `0.0` if empty.
* **Trajectory Interpolation**: When the hand moves quickly between sensor samples, linear interpolation fills intermediate cells along the stroke so fast lines don't leave gaps in the grid.
* **Why?** This removes stroke order and speed dependencies. An `O` drawn clockwise looks identical to an `O` drawn counterclockwise.

### 3. Global Shape Geometry (3 features)
* **Aspect Ratio**: $\frac{\text{height}}{\text{width}}$ (e.g., tall skinny letters like `I` vs square/wide letters like `O` or `M`).
* **Bounding Box Width & Height**: Absolute physical size in centimeters.

**Total Feature Vector**: $36 \text{ (grid cells)} + 3 \text{ (shape metrics)} = \mathbf{39 \text{ features}}$. Both offline training (`train_classifier.py`) and live inference (`server.py`) execute this identical pipeline via `features.py`.

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

