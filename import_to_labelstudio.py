"""Convert YOLO auto-annotations to Label Studio JSON pre-annotation format.

Reads YOLO-format label files and corresponding images, then outputs a JSON
file importable into Label Studio with pre-filled bounding box annotations.
"""

import argparse
import json
import uuid
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


DATASET_ROOT = Path(__file__).parent / "dataset"
IMAGES_DIR = DATASET_ROOT / "images" / "architecttura"
LABELS_DIR = DATASET_ROOT / "labels" / "architecttura"

CLASSES: list[str] = [
    "bathtub",
    "corridor",
    "counter",
    "dimension_line",
    "door",
    "door_tag",
    "drinking_fountain",
    "elevator",
    "handrail",
    "ramp",
    "room_tag",
    "shower",
    "sink",
    "slope_arrow",
    "stairs",
    "toilet",
    "urinal",
]

IMAGE_EXTENSIONS: set[str] = {".png", ".jpg", ".jpeg"}


@dataclass
class YoloBox:
    class_id: int
    x_center: float
    y_center: float
    width: float
    height: float


def parse_yolo_line(line: str) -> YoloBox | None:
    """Parse a single YOLO label line into a YoloBox."""
    parts = line.strip().split()
    if len(parts) != 5:
        return None
    class_id = int(parts[0])
    x_center, y_center, width, height = (float(v) for v in parts[1:])
    return YoloBox(class_id, x_center, y_center, width, height)


def read_yolo_labels(label_path: Path) -> list[YoloBox]:
    """Read all bounding boxes from a YOLO label file."""
    boxes: list[YoloBox] = []
    for line in label_path.read_text().splitlines():
        box = parse_yolo_line(line)
        if box is not None:
            boxes.append(box)
    return boxes


def yolo_to_ls_annotation(
    box: YoloBox,
    image_width: int,
    image_height: int,
) -> dict:
    """Convert a YOLO box to a Label Studio rectangle annotation result.

    Label Studio uses percentages (0-100) for x, y, width, height,
    with origin at top-left corner.
    """
    ls_x = (box.x_center - box.width / 2) * 100
    ls_y = (box.y_center - box.height / 2) * 100
    ls_w = box.width * 100
    ls_h = box.height * 100

    label = CLASSES[box.class_id] if box.class_id < len(CLASSES) else "unknown"

    return {
        "id": uuid.uuid4().hex[:10],
        "type": "rectanglelabels",
        "from_name": "label",
        "to_name": "image",
        "original_width": image_width,
        "original_height": image_height,
        "image_rotation": 0,
        "value": {
            "rotation": 0,
            "x": ls_x,
            "y": ls_y,
            "width": ls_w,
            "height": ls_h,
            "rectanglelabels": [label],
        },
    }


def build_ls_task(
    image_path: Path,
    boxes: list[YoloBox],
    image_url_prefix: str,
) -> dict:
    """Build a single Label Studio task dict with pre-annotations."""
    img = Image.open(image_path)
    img_w, img_h = img.size
    img.close()

    results = [yolo_to_ls_annotation(b, img_w, img_h) for b in boxes]
    image_url = f"{image_url_prefix}{image_path.name}"

    task: dict = {
        "data": {"image": image_url},
        "predictions": [
            {
                "model_version": "grounding-dino-base",
                "result": results,
            }
        ],
    }
    return task


def collect_pairs(
    images_dir: Path, labels_dir: Path
) -> list[tuple[Path, Path]]:
    """Return (image, label) pairs where both files exist."""
    pairs: list[tuple[Path, Path]] = []
    for img_path in sorted(images_dir.iterdir()):
        if img_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        label_path = labels_dir / f"{img_path.stem}.txt"
        if label_path.exists():
            pairs.append((img_path, label_path))
    return pairs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert YOLO labels to Label Studio pre-annotation JSON",
    )
    parser.add_argument(
        "--images-dir",
        type=Path,
        default=IMAGES_DIR,
        help="Directory containing images",
    )
    parser.add_argument(
        "--labels-dir",
        type=Path,
        default=LABELS_DIR,
        help="Directory containing YOLO label files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent / "labelstudio_preannotations.json",
        help="Output JSON file path",
    )
    parser.add_argument(
        "--image-url-prefix",
        type=str,
        default="/data/local-files/?d=images/architecttura/",
        help="URL prefix for images in Label Studio (default: local file serving)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    pairs = collect_pairs(args.images_dir, args.labels_dir)
    if not pairs:
        print("No matching image/label pairs found.")
        print(f"  Images dir: {args.images_dir}")
        print(f"  Labels dir: {args.labels_dir}")
        return

    print(f"Found {len(pairs)} labeled images")

    tasks: list[dict] = []
    total_boxes = 0
    for img_path, label_path in pairs:
        boxes = read_yolo_labels(label_path)
        total_boxes += len(boxes)
        task = build_ls_task(img_path, boxes, args.image_url_prefix)
        tasks.append(task)

    args.output.write_text(json.dumps(tasks, indent=2) + "\n")
    print(f"Wrote {len(tasks)} tasks ({total_boxes} annotations) to {args.output}")


if __name__ == "__main__":
    main()
