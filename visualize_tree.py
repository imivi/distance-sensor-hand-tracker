"""
Visualize a single Decision Tree from the trained Random Forest model.

Generates:
1. An SVG diagram of the decision tree (standalone, clean vector graphic).
2. An optional ASCII/text representation printed to terminal or saved as .txt.
"""

from pathlib import Path
import argparse
import joblib
import numpy as np


def get_feature_names() -> list[str]:
    """Generates readable names for the 39 features."""
    names = []
    # 6x6 occupancy grid
    for r in range(6):
        for c in range(6):
            names.append(f"Grid[{r},{c}]")
    names.extend(["AspectRatio", "Width_cm", "Height_cm"])
    return names


def export_tree_to_svg(
    estimator,
    feature_names: list[str],
    class_names: list[str],
    output_path: Path,
    max_depth: int = 4,
):
    """
    Renders an estimator tree as a crisp SVG diagram up to max_depth.
    Uses Reingold-Tilford style layout calculation.
    """
    tree_ = estimator.tree_

    class Node:
        def __init__(self, node_id: int, depth: int):
            self.node_id = node_id
            self.depth = depth
            self.is_leaf = tree_.children_left[node_id] == tree_.children_right[node_id]
            self.left_child = None
            self.right_child = None
            self.x = 0.0
            self.y = 0.0
            self.width = 150
            self.height = 68

            # Decision info
            if not self.is_leaf and depth < max_depth:
                feat_idx = tree_.feature[node_id]
                self.feature = (
                    feature_names[feat_idx]
                    if feat_idx < len(feature_names)
                    else f"f_{feat_idx}"
                )
                self.threshold = tree_.threshold[node_id]
            else:
                self.feature = None
                self.threshold = None

            # Distribution and predicted class
            value = tree_.value[node_id][0]
            pred_idx = int(np.argmax(value))
            self.samples = int(tree_.n_node_samples[node_id])
            self.pred_class = (
                class_names[pred_idx] if pred_idx < len(class_names) else str(pred_idx)
            )

    def build_tree(node_id: int, depth: int):
        node = Node(node_id, depth)
        if depth < max_depth and not node.is_leaf:
            left_id = tree_.children_left[node_id]
            right_id = tree_.children_right[node_id]
            if left_id != -1:
                node.left_child = build_tree(left_id, depth + 1)
            if right_id != -1:
                node.right_child = build_tree(right_id, depth + 1)
        return node

    root = build_tree(0, 0)

    # Layout calculation: assign coordinates
    current_x = 20.0
    level_gap_y = 110.0
    node_margin_x = 25.0

    def assign_positions(node: Node):
        nonlocal current_x
        if node.left_child:
            assign_positions(node.left_child)

        if node.left_child and node.right_child:
            assign_positions(node.right_child)
            node.x = (node.left_child.x + node.right_child.x) / 2.0
        elif node.left_child:
            node.x = node.left_child.x
        else:
            node.x = current_x
            current_x += node.width + node_margin_x

        node.y = 30.0 + node.depth * level_gap_y

    assign_positions(root)

    # Compute bounding canvas size
    all_nodes = []

    def collect_nodes(node: Node):
        all_nodes.append(node)
        if node.left_child:
            collect_nodes(node.left_child)
        if node.right_child:
            collect_nodes(node.right_child)

    collect_nodes(root)

    min_x = min(n.x for n in all_nodes)
    max_x = max(n.x + n.width for n in all_nodes)
    max_y = max(n.y + n.height for n in all_nodes)

    offset_x = 30.0 - min_x
    for n in all_nodes:
        n.x += offset_x

    svg_width = int(max_x + offset_x + 30.0)
    svg_height = int(max_y + 40.0)

    # Render SVG lines and cards
    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="100%" height="100%">',
        f'  <rect width="{svg_width}" height="{svg_height}" fill="#f8fafc" />',
        "  <style>",
        "    .edge { stroke: #94a3b8; stroke-width: 2; fill: none; }",
        "    .edge-lbl { font-family: system-ui, sans-serif; font-size: 11px; fill: #64748b; font-weight: 600; }",
        "    .node-box { rx: 8; stroke-width: 1.5; }",
        "    .node-title { font-family: system-ui, sans-serif; font-weight: 700; font-size: 12px; }",
        "    .node-sub { font-family: system-ui, sans-serif; font-size: 11px; fill: #475569; }",
        "    .node-class { font-family: system-ui, sans-serif; font-weight: 700; font-size: 11px; }",
        "  </style>",
    ]

    # Draw edges first so they sit below nodes
    for n in all_nodes:
        start_x = n.x + n.width / 2.0
        start_y = n.y + n.height
        if n.left_child:
            end_x = n.left_child.x + n.left_child.width / 2.0
            end_y = n.left_child.y
            mid_y = (start_y + end_y) / 2.0
            svg_lines.append(
                f'  <path d="M {start_x} {start_y} C {start_x} {mid_y}, {end_x} {mid_y}, {end_x} {end_y}" class="edge" />'
            )
            svg_lines.append(
                f'  <text x="{(start_x + end_x) / 2 - 14}" y="{mid_y}" class="edge-lbl">True</text>'
            )
        if n.right_child:
            end_x = n.right_child.x + n.right_child.width / 2.0
            end_y = n.right_child.y
            mid_y = (start_y + end_y) / 2.0
            svg_lines.append(
                f'  <path d="M {start_x} {start_y} C {start_x} {mid_y}, {end_x} {mid_y}, {end_x} {end_y}" class="edge" />'
            )
            svg_lines.append(
                f'  <text x="{(start_x + end_x) / 2 + 6}" y="{mid_y}" class="edge-lbl">False</text>'
            )

    # Draw nodes
    for n in all_nodes:
        is_terminal = n.left_child is None and n.right_child is None
        fill_bg = "#ecfdf5" if is_terminal else "#ffffff"
        stroke_c = "#10b981" if is_terminal else "#0284c7"
        title_c = "#047857" if is_terminal else "#0369a1"

        svg_lines.append(f'  <g transform="translate({n.x:.1f}, {n.y:.1f})">')
        svg_lines.append(
            f'    <rect width="{n.width}" height="{n.height}" class="node-box" fill="{fill_bg}" stroke="{stroke_c}" />'
        )

        if not is_terminal and n.feature:
            svg_lines.append(
                f'    <text x="10" y="22" class="node-title" fill="{title_c}">{n.feature} &#8804; {n.threshold:.2f}</text>'
            )
        else:
            svg_lines.append(
                f'    <text x="10" y="22" class="node-title" fill="{title_c}">Foglia (Terminale)</text>'
            )

        svg_lines.append(
            f'    <text x="10" y="42" class="node-sub">Campioni: {n.samples}</text>'
        )
        svg_lines.append(
            f'    <text x="10" y="58" class="node-class" fill="{title_c}">Pred: &apos;{n.pred_class}&apos;</text>'
        )
        svg_lines.append("  </g>")

    svg_lines.append("</svg>")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(svg_lines), encoding="utf-8")
    print(f"Saved Decision Tree SVG to {output_path}")


def export_tree_to_ascii(
    estimator,
    feature_names: list[str],
    class_names: list[str],
    output_path: Path | None = None,
    max_depth: int = 5,
):
    """Exports tree decision logic as indented ASCII text."""
    tree_ = estimator.tree_

    lines = []

    def recurse(node_id: int, depth: int, prefix: str = ""):
        if depth > max_depth:
            return

        is_leaf = tree_.children_left[node_id] == tree_.children_right[node_id]
        samples = tree_.n_node_samples[node_id]
        value = tree_.value[node_id][0]
        pred_class = class_names[int(np.argmax(value))]

        if is_leaf or depth == max_depth:
            lines.append(
                f"{prefix}--> [LEAF] Pred: '{pred_class}' (samples: {samples})"
            )
            return

        feat_idx = tree_.feature[node_id]
        feat_name = feature_names[feat_idx]
        thresh = tree_.threshold[node_id]

        lines.append(
            f"{prefix}[NODE] if {feat_name} <= {thresh:.2f} (samples: {samples}, top: '{pred_class}'):"
        )
        recurse(tree_.children_left[node_id], depth + 1, prefix + "  |-- True:  ")
        recurse(tree_.children_right[node_id], depth + 1, prefix + "  \\-- False: ")

    recurse(0, 0)
    text_content = "\n".join(lines)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text_content, encoding="utf-8")
        print(f"Saved Decision Tree ASCII to {output_path}")

    return text_content


def main():
    parser = argparse.ArgumentParser(
        description="Visualize a decision tree from the trained Random Forest model."
    )
    parser.add_argument(
        "--model",
        type=str,
        default="models/gesture_rf.joblib",
        help="Path to gesture_rf.joblib",
    )
    parser.add_argument(
        "--tree-index",
        type=int,
        default=0,
        help="Index of the estimator tree in the forest (0 to n_estimators - 1)",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=3,
        help="Maximum depth to visualize (default: 3 for clean visual layout)",
    )
    parser.add_argument(
        "--output-svg",
        type=str,
        default="docs/assets/tree_visualization.svg",
        help="Destination SVG path",
    )
    parser.add_argument(
        "--output-txt",
        type=str,
        default="docs/assets/tree_rules.txt",
        help="Destination ASCII rules text file",
    )
    args = parser.parse_args()

    model_path = Path(args.model)
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found at {model_path}")

    payload = joblib.load(model_path)
    rf = payload["model"]
    class_names = [str(c) for c in payload["classes"]]
    feature_names = get_feature_names()

    n_trees = len(rf.estimators_)
    if not (0 <= args.tree_index < n_trees):
        raise ValueError(
            f"Tree index {args.tree_index} out of bounds (forest has {n_trees} trees)"
        )

    tree = rf.estimators_[args.tree_index]
    print(
        f"Visualizing Tree #{args.tree_index} (total depth: {tree.get_depth()}, leaves: {tree.get_n_leaves()}) up to depth {args.max_depth}"
    )

    # Export SVG
    if args.output_svg:
        export_tree_to_svg(
            tree,
            feature_names,
            class_names,
            Path(args.output_svg),
            max_depth=args.max_depth,
        )

    # Export ASCII
    if args.output_txt:
        ascii_text = export_tree_to_ascii(
            tree,
            feature_names,
            class_names,
            Path(args.output_txt),
            max_depth=args.max_depth,
        )
        print("\nASCII Tree Preview (first 15 lines):")
        print("\n".join(ascii_text.splitlines()[:15]))


if __name__ == "__main__":
    main()
