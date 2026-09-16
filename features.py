"""
Feature extraction for 2D Hand Gesture Classification.
Extracts a direction-independent 6x6 spatial occupancy grid + global shape dimensions.
Total feature vector length: 39.
"""

from typing import List, Tuple, Optional
import numpy as np

GRID_SIZE = 6  # 6x6 occupancy grid = 36 cells


def extract_features(points: List[Tuple[float, float]]) -> Optional[np.ndarray]:
    """
    Extracts a direction-independent feature vector of length 39:
      - 36 binary cell occupancy indicators (6x6 grid)
      - 1 aspect ratio (height / width)
      - 1 bounding box width (cm)
      - 1 bounding box height (cm)

    points: list of (x, y) coordinates in cm.
    """
    if not points or len(points) < 4:
        return None

    xs = np.array([p[0] for p in points], dtype=np.float32)
    ys = np.array([p[1] for p in points], dtype=np.float32)

    min_x, max_x = float(np.min(xs)), float(np.max(xs))
    min_y, max_y = float(np.min(ys)), float(np.max(ys))

    width = max_x - min_x
    height = max_y - min_y

    # Prevent division by zero for point clusters or straight lines
    denom_x = width if width > 0.5 else 0.5
    denom_y = height if height > 0.5 else 0.5
    aspect_ratio = height / denom_x

    # 6x6 Occupancy grid
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float32)

    # Uniform scaling: use the LONGER side to scale both axes equally,
    # preserving aspect ratio. Then center the gesture in the grid.
    # This avoids distortion for narrow gestures (e.g., "I" stays thin).
    scale = max(denom_x, denom_y)
    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0
    half_grid = (GRID_SIZE - 1) / 2.0

    norm_x = np.clip((xs - center_x) / scale * (GRID_SIZE - 1) + half_grid, 0, GRID_SIZE - 1)
    norm_y = np.clip((ys - center_y) / scale * (GRID_SIZE - 1) + half_grid, 0, GRID_SIZE - 1)

    # Mark cells through which points or connecting segments pass
    for i in range(len(points)):
        gx = int(round(norm_x[i]))
        gy = int(round(norm_y[i]))
        grid[gy, gx] = 1.0

        # Fill intermediate points along consecutive trajectory steps
        if i > 0:
            steps = max(
                int(abs(norm_x[i] - norm_x[i - 1]) + abs(norm_y[i] - norm_y[i - 1]))
                * 2,
                1,
            )
            for s in range(1, steps):
                frac = s / steps
                inter_x = int(round(norm_x[i - 1] + frac * (norm_x[i] - norm_x[i - 1])))
                inter_y = int(round(norm_y[i - 1] + frac * (norm_y[i] - norm_y[i - 1])))
                grid[inter_y, inter_x] = 1.0

    features = np.concatenate(
        [
            grid.flatten(),  # 36 features
            np.array([aspect_ratio, width, height], dtype=np.float32),  # 3 features
        ]
    )
    return features
