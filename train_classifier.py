"""
Training script for Gesture Recognition Random Forest model.

Workflow:
1. Reads all recorded gesture trajectories from recordings/gestures.csv.
2. Extracts direction-independent features using a 6x6 spatial occupancy grid
   and global shape dimensions (aspect ratio, width, height) via features.py.
3. Evaluates model generalization using Stratified K-Fold Cross-Validation.
4. Trains a RandomForestClassifier on all samples and serializes the model
   along with class labels to models/gesture_rf.joblib for real-time inference.
"""

from collections import defaultdict
import csv
from pathlib import Path
import sys

import joblib
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_score, cross_val_predict

from features import extract_features

# Paths for dataset input, serialized model output, and training matrix dump
CSV_PATH = Path("recordings/gestures.csv")
TRAINING_MATRIX_PATH = Path("recordings/training_matrix.csv")
METRICS_REPORT_PATH = Path("recordings/classification_report.csv")
CONFUSION_MATRIX_PATH = Path("recordings/confusion_matrix.csv")
METRICS_IMAGE_PATH = Path("recordings/classification_report.png")
CONFUSION_MATRIX_IMAGE_PATH = Path("recordings/confusion_matrix.png")
MODEL_DIR = Path("models")
MODEL_PATH = MODEL_DIR / "gesture_rf.joblib"


# Maximum distance (cm) allowed between two consecutive gesture points.
# Jumps >= this value are sensor spikes and are discarded before feature extraction.
MAX_RECORD_JUMP_CM = 10.0
# If this many consecutive points are rejected, the reference itself was the spike.
MAX_RECORD_SKIP_RESET = 5


def save_metrics_image(report_dict: dict, output_path: Path):
    """
    Renders classification report (precision, recall, f1-score, support) as a PNG table image.
    """
    rows = []
    # Class rows (exclude summary keys)
    summary_keys = {"accuracy", "macro avg", "weighted avg"}
    for label, m in report_dict.items():
        if label not in summary_keys and isinstance(m, dict):
            rows.append([
                label,
                f"{m.get('precision', 0.0) * 100:.1f}%",
                f"{m.get('recall', 0.0) * 100:.1f}%",
                f"{m.get('f1-score', 0.0) * 100:.1f}%",
                str(int(m.get('support', 0))),
            ])

    # Summary rows
    if "accuracy" in report_dict:
        acc_val = report_dict["accuracy"]
        total_supp = sum(int(m.get("support", 0)) for k, m in report_dict.items() if k not in summary_keys and isinstance(m, dict))
        rows.append(["accuracy", "", "", f"{float(acc_val) * 100:.1f}%", str(total_supp)])

    for k in ["macro avg", "weighted avg"]:
        if k in report_dict and isinstance(report_dict[k], dict):
            m = report_dict[k]
            rows.append([
                k,
                f"{m.get('precision', 0.0) * 100:.1f}%",
                f"{m.get('recall', 0.0) * 100:.1f}%",
                f"{m.get('f1-score', 0.0) * 100:.1f}%",
                str(int(m.get('support', 0))),
            ])

    headers = ["Class", "Precision", "Recall", "F1-Score", "Support"]
    col_widths = [130, 110, 110, 110, 100]
    row_height = 36
    margin = 30
    title_height = 50

    img_w = margin * 2 + sum(col_widths)
    img_h = margin * 2 + title_height + (len(rows) + 1) * row_height

    img = Image.new("RGB", (img_w, img_h), (248, 250, 252))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    # Title
    draw.text((margin, margin), "Classification Metrics (Precision & Recall)", fill=(15, 23, 42), font=font)

    y_top = margin + title_height

    # Header background
    draw.rectangle([margin, y_top, margin + sum(col_widths), y_top + row_height], fill=(226, 232, 240), outline=(203, 213, 225))
    x_curr = margin
    for col_idx, (h, w) in enumerate(zip(headers, col_widths)):
        draw.text((x_curr + 12, y_top + 10), h, fill=(15, 23, 42), font=font)
        x_curr += w

    # Data rows
    y_curr = y_top + row_height
    for r_idx, row in enumerate(rows):
        is_summary = row[0] in ["accuracy", "macro avg", "weighted avg"]
        bg = (241, 245, 249) if is_summary else ((255, 255, 255) if r_idx % 2 == 0 else (248, 250, 252))
        draw.rectangle([margin, y_curr, margin + sum(col_widths), y_curr + row_height], fill=bg, outline=(226, 232, 240))

        x_curr = margin
        for col_idx, (val, w) in enumerate(zip(row, col_widths)):
            text_color = (15, 23, 42) if not is_summary else (30, 41, 59)
            draw.text((x_curr + 12, y_curr + 10), val, fill=text_color, font=font)
            x_curr += w
        y_curr += row_height

    img.save(output_path, "PNG")


def save_confusion_matrix_image(cm: np.ndarray, classes: list, output_path: Path):
    """
    Renders the confusion matrix as an image heatmap with numerical cell labels.
    """
    n = len(classes)
    cell_size = 46
    margin_left = 80
    margin_top = 80
    margin_right = 40
    margin_bottom = 50

    img_w = margin_left + margin_right + n * cell_size
    img_h = margin_top + margin_bottom + n * cell_size

    img = Image.new("RGB", (img_w, img_h), (248, 250, 252))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    # Title
    draw.text((margin_left, 20), "Confusion Matrix (Rows: True, Columns: Predicted)", fill=(15, 23, 42), font=font)

    max_val = max(int(np.max(cm)), 1)

    # Draw column labels (Predicted)
    for c_idx, c_label in enumerate(classes):
        x = margin_left + c_idx * cell_size + cell_size // 2 - 4
        y = margin_top - 24
        draw.text((x, y), str(c_label), fill=(37, 99, 235), font=font)

    # Draw rows and cells
    for r_idx, r_label in enumerate(classes):
        # Row label (True)
        y = margin_top + r_idx * cell_size + cell_size // 2 - 6
        draw.text((margin_left - 30, y), str(r_label), fill=(37, 99, 235), font=font)

        for c_idx in range(n):
            count = int(cm[r_idx, c_idx])
            x0 = margin_left + c_idx * cell_size
            y0 = margin_top + r_idx * cell_size
            x1 = x0 + cell_size
            y1 = y0 + cell_size

            # Color cell: Diagonal is green intensity, errors are red/orange tint, 0 is white
            if r_idx == c_idx:
                intensity = min(count / max_val, 1.0)
                # Green gradient
                r = int(240 - intensity * (240 - 22))
                g = int(253 - intensity * (253 - 163))
                b = int(244 - intensity * (244 - 74))
                cell_color = (r, g, b)
            elif count > 0:
                # Error cell: light red tint
                cell_color = (254, 226, 226)
            else:
                cell_color = (255, 255, 255)

            draw.rectangle([x0, y0, x1, y1], fill=cell_color, outline=(203, 213, 225))

            # Number in cell
            num_str = str(count)
            tx = x0 + cell_size // 2 - 4 * len(num_str)
            ty = y0 + cell_size // 2 - 6
            text_color = (255, 255, 255) if (r_idx == c_idx and count > max_val * 0.6) else (15, 23, 42)
            draw.text((tx, ty), num_str, fill=text_color, font=font)

    img.save(output_path, "PNG")


def filter_outlier_points(
    points: list[tuple[float, float]],
    max_jump: float = MAX_RECORD_JUMP_CM,
    max_skip_reset: int = MAX_RECORD_SKIP_RESET,
) -> list[tuple[float, float]]:
    """
    Removes sensor spike points from a recorded gesture trajectory.

    A point is discarded if its Euclidean distance from the previous accepted
    point is >= max_jump cm.  If max_skip_reset consecutive points are rejected,
    the reference was likely the spike — discard accepted points so far and
    restart from the current point.

    Args:
        points:          List of (x_cm, y_cm) coordinates in recording order.
        max_jump:        Maximum allowed distance between consecutive points (cm).
        max_skip_reset:  After this many consecutive rejections, reset the reference.

    Returns:
        Cleaned list of (x, y) points with spikes removed.
    """
    if not points:
        return []

    accepted: list[tuple[float, float]] = [points[0]]
    last_x, last_y = points[0]
    skip_streak = 0

    for x, y in points[1:]:
        dist = ((x - last_x) ** 2 + (y - last_y) ** 2) ** 0.5
        if dist >= max_jump:
            skip_streak += 1
            if skip_streak >= max_skip_reset:
                # Reference was the spike — wipe and restart from here
                accepted.clear()
                accepted.append((x, y))
                last_x, last_y = x, y
                skip_streak = 0
            continue  # discard this point (or already reset above)
        skip_streak = 0
        accepted.append((x, y))
        last_x, last_y = x, y

    return accepted


def load_dataset():
    """
    Parses recordings/gestures.csv and extracts fixed-size feature vectors.

    Groups individual (x, y) coordinate rows by their unique `recording_id`,
    computes the 39-dimensional feature vector for each gesture, and pairs it
    with the target letter label.

    Returns:
        X (np.ndarray): 2D float array of shape (N_samples, 39)
        y (np.ndarray): 1D string array of shape (N_samples,) containing letter labels
        recording_ids (list[str]): List of recording IDs corresponding to rows in X
    """
    if not CSV_PATH.exists():
        print(f"Error: {CSV_PATH} not found.")
        sys.exit(1)

    # Store letter target per recording ID and collect sequence of (x, y) coordinates
    rec_letters = {}
    rec_points = defaultdict(list)  # list of (x, y)

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rid = row["recording_id"]
                letter = row["letter"].strip().upper()
                x = float(row["x_cm"])
                y = float(row["y_cm"])
                rec_letters[rid] = letter
                rec_points[rid].append((x, y))
            except (ValueError, KeyError, TypeError):
                continue

    X_list = []
    y_list = []
    rids_list = []
    skipped = 0
    total_raw = 0
    total_kept = 0

    # Extract 39 features for each gesture recording
    for rid, pts in rec_points.items():
        total_raw += len(pts)
        # Apply distance-based outlier filter before feature extraction
        clean_pts = filter_outlier_points(pts)
        total_kept += len(clean_pts)
        feat = extract_features(clean_pts)
        if feat is not None:
            X_list.append(feat)
            y_list.append(rec_letters[rid])
            rids_list.append(rid)
        else:
            # Skip noise or accidental clicks with fewer than 4 valid points
            skipped += 1

    discarded = total_raw - total_kept
    print(
        f"Loaded {len(X_list)} valid gesture samples ({skipped} skipped due to < 4 points).\n"
        f"Outlier filter: removed {discarded}/{total_raw} spike points "
        f"({discarded / total_raw * 100:.1f}% of dataset)."
        if total_raw > 0 else
        f"Loaded {len(X_list)} valid gesture samples ({skipped} skipped due to < 4 points)."
    )
    return np.array(X_list, dtype=np.float32), np.array(y_list), rids_list




def train_and_save():
    """
    Loads data, validates accuracy via Stratified K-Fold, fits a Random Forest,
    and saves the trained model artifact.
    """
    # 1. Load dataset & extract feature matrix X, label vector y, and recording IDs
    X, y, rids = load_dataset()
    if len(X) == 0:
        print("No valid samples found to train on.")
        return

    # 2. Export training feature matrix X and target y to CSV for debugging and docs
    try:
        TRAINING_MATRIX_PATH.parent.mkdir(parents=True, exist_ok=True)
        # Feature column names: grid_0_0 to grid_5_5 + shape dimensions
        feature_cols = [f"grid_{r}_{c}" for r in range(6) for c in range(6)]
        feature_cols.extend(["aspect_ratio", "bbox_width_cm", "bbox_height_cm"])
        header = ["recording_id", "target_letter"] + feature_cols

        with open(TRAINING_MATRIX_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for rid, letter, row_features in zip(rids, y, X):
                writer.writerow(
                    [rid, letter] + [round(float(v), 4) for v in row_features]
                )

        print(
            f"Saved training matrix ({X.shape[0]} rows × {X.shape[1]} features) to {TRAINING_MATRIX_PATH}"
        )
    except Exception as e:
        print(f"Warning: Failed to save training matrix to {TRAINING_MATRIX_PATH}: {e}")

    # 3. Inspect class distribution (samples per letter)
    classes, counts = np.unique(y, return_counts=True)
    print("Class distribution:")
    for c, cnt in zip(classes, counts):
        print(f"  '{c}': {cnt} samples")

    # 4. Configure Random Forest Classifier:
    # - n_estimators=100: Ensemble of 100 decision trees for stable variance reduction
    # - max_depth=12: Prevents individual trees from memorizing single noise points
    # - class_weight="balanced": Automatically adjusts weights inversely proportional to class frequencies
    rf = RandomForestClassifier(n_estimators=100, max_depth=12, class_weight="balanced")

    # 5. Stratified Cross-Validation (preserves percentage of samples for each class)
    min_count = min(counts)
    if min_count >= 2 and len(classes) > 1:
        n_splits = min(min_count, 3)
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
        scores = cross_val_score(rf, X, y, cv=skf, scoring="accuracy")
        print(
            f"\n{n_splits}-Fold Stratified Cross-Validation Accuracy: {scores.mean() * 100:.1f}% (+/- {scores.std() * 100:.1f}%)"
        )

        # Cross-validated out-of-fold predictions for precision, recall, and confusion matrix
        y_pred = cross_val_predict(rf, X, y, cv=skf)

        print("\nClassification Report (Precision, Recall, F1-Score):")
        report_text = classification_report(y, y_pred, digits=3, zero_division=0)
        print(report_text)

        # Save classification report to CSV
        try:
            report_dict = classification_report(y, y_pred, digits=4, zero_division=0, output_dict=True)
            with open(METRICS_REPORT_PATH, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["class", "precision", "recall", "f1-score", "support"])
                for label, m in report_dict.items():
                    if isinstance(m, dict):
                        writer.writerow([
                            label,
                            round(m.get("precision", 0.0), 4),
                            round(m.get("recall", 0.0), 4),
                            round(m.get("f1-score", 0.0), 4),
                            int(m.get("support", 0)),
                        ])
                    else:
                        writer.writerow(["accuracy", "", "", round(float(m), 4), len(y)])
            print(f"Saved classification metrics to {METRICS_REPORT_PATH}")

            # Save classification metrics image
            save_metrics_image(report_dict, METRICS_IMAGE_PATH)
            print(f"Saved classification metrics image to {METRICS_IMAGE_PATH}")
        except Exception as e:
            print(f"Warning: Failed to save classification report: {e}")

        # Confusion Matrix
        cm = confusion_matrix(y, y_pred, labels=classes)
        print("\nConfusion Matrix (Rows: True, Columns: Predicted):")
        header_row = "      " + "".join([f"{c:>5}" for c in classes])
        print(header_row)
        print("    " + "-" * len(header_row))
        for idx, true_class in enumerate(classes):
            row_str = f" {true_class:>3} |" + "".join([f"{val:>5}" for val in cm[idx]])
            print(row_str)

        # Save confusion matrix to CSV and Image
        try:
            with open(CONFUSION_MATRIX_PATH, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["true_label"] + [f"pred_{c}" for c in classes])
                for idx, true_class in enumerate(classes):
                    writer.writerow([true_class] + [int(val) for val in cm[idx]])
            print(f"Saved confusion matrix to {CONFUSION_MATRIX_PATH}")

            # Save confusion matrix image
            save_confusion_matrix_image(cm, list(classes), CONFUSION_MATRIX_IMAGE_PATH)
            print(f"Saved confusion matrix image to {CONFUSION_MATRIX_IMAGE_PATH}")
        except Exception as e:
            print(f"Warning: Failed to save confusion matrix: {e}")

    # 6. Fit model on the full dataset
    rf.fit(X, y)
    print("\nModel trained successfully on all data.")

    # 7. Save model and metadata to disk for server.py inference
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "model": rf,
        "classes": rf.classes_.tolist(),
        "n_features": X.shape[1],
        "feature_type": "occupancy_grid_6x6",
    }
    joblib.dump(payload, MODEL_PATH)
    print(f"Saved model artifact to {MODEL_PATH}")


if __name__ == "__main__":
    train_and_save()
