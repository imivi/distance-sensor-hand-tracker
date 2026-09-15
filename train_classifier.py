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
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import StratifiedKFold, cross_val_score

from features import extract_features

# Paths for dataset input and serialized model output
CSV_PATH = Path("recordings/gestures.csv")
MODEL_DIR = Path("models")
MODEL_PATH = MODEL_DIR / "gesture_rf.joblib"


def load_dataset():
    """
    Parses recordings/gestures.csv and extracts fixed-size feature vectors.

    Groups individual (x, y) coordinate rows by their unique `recording_id`,
    computes the 39-dimensional feature vector for each gesture, and pairs it
    with the target letter label.

    Returns:
        X (np.ndarray): 2D float array of shape (N_samples, 39)
        y (np.ndarray): 1D string array of shape (N_samples,) containing letter labels
    """
    if not CSV_PATH.exists():
        print(f"Error: {CSV_PATH} not found.")
        sys.exit(1)

    # Store letter target per recording ID and collect sequence of (x, y) coordinates
    rec_letters = {}
    rec_points = defaultdict(list)

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rid = row["recording_id"]
            rec_letters[rid] = row["letter"].strip().upper()
            rec_points[rid].append((float(row["x_cm"]), float(row["y_cm"])))

    X_list = []
    y_list = []
    skipped = 0

    # Extract 39 features for each gesture recording
    for rid, pts in rec_points.items():
        feat = extract_features(pts)
        if feat is not None:
            X_list.append(feat)
            y_list.append(rec_letters[rid])
        else:
            # Skip noise or accidental clicks with fewer than 4 valid points
            skipped += 1

    print(
        f"Loaded {len(X_list)} valid gesture samples ({skipped} skipped due to < 4 points)."
    )
    return np.array(X_list, dtype=np.float32), np.array(y_list)


def train_and_save():
    """
    Loads data, validates accuracy via Stratified K-Fold, fits a Random Forest,
    and saves the trained model artifact.
    """
    # 1. Load dataset & extract feature matrix X and label vector y
    X, y = load_dataset()
    if len(X) == 0:
        print("No valid samples found to train on.")
        return

    # 2. Inspect class distribution (samples per letter)
    classes, counts = np.unique(y, return_counts=True)
    print("Class distribution:")
    for c, cnt in zip(classes, counts):
        print(f"  '{c}': {cnt} samples")

    # 3. Configure Random Forest Classifier:
    # - n_estimators=100: Ensemble of 100 decision trees for stable variance reduction
    # - max_depth=12: Prevents individual trees from memorizing single noise points
    # - class_weight="balanced": Automatically adjusts weights inversely proportional to class frequencies
    rf = RandomForestClassifier(n_estimators=100, max_depth=12, class_weight="balanced")

    # 4. Stratified Cross-Validation (preserves percentage of samples for each class)
    min_count = min(counts)
    if min_count >= 2 and len(classes) > 1:
        n_splits = min(min_count, 3)
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True)
        scores = cross_val_score(rf, X, y, cv=skf, scoring="accuracy")
        print(
            f"\n{n_splits}-Fold Stratified Cross-Validation Accuracy: {scores.mean() * 100:.1f}% (+/- {scores.std() * 100:.1f}%)"
        )

    # 5. Fit model on the full dataset
    rf.fit(X, y)
    print("\nModel trained successfully on all data.")

    # 6. Save model and metadata to disk for server.py inference
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
