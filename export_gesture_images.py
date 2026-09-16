"""
Script to visualize all recorded gestures from recordings/gestures.csv as 600x600 images
representing the 6x6 spatial occupancy grid of points.
"""

from collections import defaultdict
import csv
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from train_classifier import filter_outlier_points
from features import GRID_SIZE

CSV_PATH = Path("recordings/gestures.csv")
OUTPUT_DIR = Path("recordings/gesture_images")


def compute_occupancy_grid(points: list[tuple[float, float]]) -> tuple[np.ndarray | None, list[tuple[float, float]]]:
    """
    Computes 6x6 occupancy grid and normalized trajectory coordinates in [0, GRID_SIZE - 1].
    Matches features.py logic.
    """
    if not points or len(points) < 4:
        return None, []

    xs = np.array([p[0] for p in points], dtype=np.float32)
    ys = np.array([p[1] for p in points], dtype=np.float32)

    min_x, max_x = float(np.min(xs)), float(np.max(xs))
    min_y, max_y = float(np.min(ys)), float(np.max(ys))

    width = max_x - min_x
    height = max_y - min_y

    denom_x = width if width > 0.5 else 0.5
    denom_y = height if height > 0.5 else 0.5

    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float32)

    norm_x = np.clip((xs - min_x) / denom_x * (GRID_SIZE - 1), 0, GRID_SIZE - 1)
    norm_y = np.clip((ys - min_y) / denom_y * (GRID_SIZE - 1), 0, GRID_SIZE - 1)

    norm_points = list(zip(norm_x, norm_y))

    for i in range(len(points)):
        gx = int(round(norm_x[i]))
        gy = int(round(norm_y[i]))
        grid[gy, gx] = 1.0

        if i > 0:
            steps = max(
                int(abs(norm_x[i] - norm_x[i - 1]) + abs(norm_y[i] - norm_y[i - 1])) * 2,
                1,
            )
            for s in range(1, steps):
                frac = s / steps
                inter_x = int(round(norm_x[i - 1] + frac * (norm_x[i] - norm_x[i - 1])))
                inter_y = int(round(norm_y[i - 1] + frac * (norm_y[i] - norm_y[i - 1])))
                grid[inter_y, inter_x] = 1.0

    return grid, norm_points


def render_gesture_image(
    recording_id: str,
    letter: str,
    grid: np.ndarray,
    norm_points: list[tuple[float, float]],
    output_path: Path,
    img_size: int = 600,
):
    """
    Renders a 600x600 image displaying the 6x6 grid with occupied cells,
    grid lines, trajectory, and metadata.
    """
    # Create white canvas
    img = Image.new("RGB", (img_size, img_size), (248, 250, 252))  # soft light slate background
    draw = ImageDraw.Draw(img)

    margin = 48
    grid_area_size = img_size - (2 * margin)  # e.g., 600 - 96 = 504 px
    cell_size = grid_area_size / GRID_SIZE     # 504 / 6 = 84 px

    # Note: In Cartesian coordinates y=0 is at the bottom, but in images row 0 is at the top.
    # We display y pointing upwards so the drawn gesture appears right-side up.
    def cell_to_pixel_rect(col: int, row: int):
        # row: 0 is bottom, 5 is top
        screen_row = (GRID_SIZE - 1) - row
        x0 = margin + col * cell_size
        y0 = margin + screen_row * cell_size
        x1 = x0 + cell_size
        y1 = y0 + cell_size
        return x0, y0, x1, y1

    # 1. Fill cells based on grid occupancy
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x0, y0, x1, y1 = cell_to_pixel_rect(col, row)
            is_active = grid[row, col] > 0.5
            if is_active:
                fill_color = (219, 234, 254)       # soft blue #dbeafe
                outline_color = (147, 197, 253)    # border #93c5fd
            else:
                fill_color = (255, 255, 255)       # white
                outline_color = (226, 232, 240)    # subtle light gray #e2e8f0

            draw.rectangle([x0, y0, x1, y1], fill=fill_color, outline=outline_color, width=1)

    # 2. Draw outer grid border
    draw.rectangle(
        [margin, margin, margin + grid_area_size, margin + grid_area_size],
        outline=(100, 116, 139),
        width=2,
    )

    # 3. Draw connecting trajectory path
    def norm_to_pixel(nx: float, ny: float):
        # Cell center mapping: coordinate 0 -> 0.5 cell, coordinate 5 -> 5.5 cell
        px = margin + (nx + 0.5) * cell_size
        py = margin + ((GRID_SIZE - 1 - ny) + 0.5) * cell_size
        return px, py

    if len(norm_points) > 1:
        pixel_points = [norm_to_pixel(nx, ny) for nx, ny in norm_points]
        for i in range(len(pixel_points) - 1):
            draw.line([pixel_points[i], pixel_points[i + 1]], fill=(37, 99, 235), width=3)

    # 4. Draw trajectory point dots
    for i, (nx, ny) in enumerate(norm_points):
        px, py = norm_to_pixel(nx, ny)
        if i == 0:
            # Start point: green
            r = 7
            draw.ellipse([px - r, py - r, px + r, py + r], fill=(16, 185, 129), outline=(255, 255, 255), width=2)
        elif i == len(norm_points) - 1:
            # End point: red
            r = 7
            draw.ellipse([px - r, py - r, px + r, py + r], fill=(239, 68, 68), outline=(255, 255, 255), width=2)
        else:
            # Intermediate points: blue dot
            r = 4
            draw.ellipse([px - r, py - r, px + r, py + r], fill=(30, 64, 175))

    # 5. Header / Footer text metadata
    header_text = f"Letter '{letter}'  |  ID: {recording_id}"
    footer_text = f"6x6 Grid  |  {len(norm_points)} points"

    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    draw.text((margin, 16), header_text, fill=(15, 23, 42), font=font)
    draw.text((margin, img_size - 32), footer_text, fill=(100, 116, 139), font=font)

    img.save(output_path, "PNG")


def main():
    if not CSV_PATH.exists():
        print(f"Error: {CSV_PATH} not found.")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Parse gestures from CSV
    rec_letters = {}
    rec_points = defaultdict(list)

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

    total_gestures = len(rec_points)
    print(f"Found {total_gestures} gestures in {CSV_PATH}.")

    generated_count = 0
    skipped_count = 0

    for rid, raw_pts in rec_points.items():
        letter = rec_letters.get(rid, "UNKNOWN")

        # Clean outliers using the project's standard filter
        clean_pts = filter_outlier_points(raw_pts)
        if len(clean_pts) < 4:
            skipped_count += 1
            continue

        grid, norm_points = compute_occupancy_grid(clean_pts)
        if grid is None:
            skipped_count += 1
            continue

        # Filename includes recording ID and letter
        out_filename = f"{letter}_{rid}.png"
        out_path = OUTPUT_DIR / out_filename

        render_gesture_image(
            recording_id=rid,
            letter=letter,
            grid=grid,
            norm_points=norm_points,
            output_path=out_path,
            img_size=600,
        )
        generated_count += 1

    print(f"Done! Successfully generated {generated_count} images in '{OUTPUT_DIR}'.")
    if skipped_count > 0:
        print(f"Skipped {skipped_count} gestures with fewer than 4 valid points.")


if __name__ == "__main__":
    main()
