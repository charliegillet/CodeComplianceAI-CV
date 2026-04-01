"""YOLOv12 training wrapper for floor plan object detection.

Configures augmentation for B&W architectural line drawings:
- Disables color jitter (hsv_h, hsv_s, hsv_v = 0)
- Enables 90-degree rotation and flips
- Sets close_mosaic=10 for late-training refinement
"""

from pathlib import Path

from ultralytics import YOLO


DATASET_YAML = Path(__file__).parent / "dataset.yaml"

# Training defaults
DEFAULTS: dict = {
    "data": str(DATASET_YAML),
    "model": "yolov12n.pt",
    "imgsz": 1024,
    "epochs": 100,
    "batch": 16,
    "project": "runs/detect",
    "name": "floor_plan",
    # Disable color jitter — floor plans are B&W line drawings
    "hsv_h": 0.0,
    "hsv_s": 0.0,
    "hsv_v": 0.0,
    # Geometric augmentation suited for architectural drawings
    "degrees": 90.0,
    "flipud": 0.5,
    "fliplr": 0.5,
    # Disable mosaic in final 10 epochs for fine-tuning
    "close_mosaic": 10,
}


def main() -> None:
    model = YOLO(DEFAULTS["model"])
    results = model.train(**DEFAULTS)
    print(f"\nTraining complete. Results: {results.save_dir}")


if __name__ == "__main__":
    main()
