"""Split dataset images and labels into train/val sets (80/20).

Moves files from a flat source directory (e.g. architecttura/)
into dataset/images/{train,val}/ and dataset/labels/{train,val}/
with matching filenames.
"""

import random
from pathlib import Path


DATASET_ROOT = Path(__file__).parent / "dataset"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
TRAIN_RATIO = 0.8
SEED = 42


def collect_labeled_images(
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


def ensure_split_dirs(dataset_root: Path) -> dict[str, dict[str, Path]]:
    """Create train/val directories for images and labels."""
    dirs: dict[str, dict[str, Path]] = {}
    for split in ("train", "val"):
        dirs[split] = {
            "images": dataset_root / "images" / split,
            "labels": dataset_root / "labels" / split,
        }
        dirs[split]["images"].mkdir(parents=True, exist_ok=True)
        dirs[split]["labels"].mkdir(parents=True, exist_ok=True)
    return dirs


def split_and_move(
    pairs: list[tuple[Path, Path]], dirs: dict[str, dict[str, Path]]
) -> None:
    """Shuffle pairs and move into train/val splits."""
    random.seed(SEED)
    random.shuffle(pairs)

    split_idx = int(len(pairs) * TRAIN_RATIO)
    splits = {"train": pairs[:split_idx], "val": pairs[split_idx:]}

    for split_name, split_pairs in splits.items():
        for img_path, label_path in split_pairs:
            img_path.rename(dirs[split_name]["images"] / img_path.name)
            label_path.rename(dirs[split_name]["labels"] / label_path.name)
        print(f"  {split_name}: {len(split_pairs)} images")


def main() -> None:
    images_dir = DATASET_ROOT / "images" / "architecttura"
    labels_dir = DATASET_ROOT / "labels" / "architecttura"

    if not images_dir.exists():
        print(f"Source image directory not found: {images_dir}")
        print("Run pdftoimg.py first, then annotate in Label Studio.")
        return

    if not labels_dir.exists():
        print(f"Source label directory not found: {labels_dir}")
        print("Export YOLO labels from Label Studio first.")
        return

    pairs = collect_labeled_images(images_dir, labels_dir)
    if not pairs:
        print("No matching image/label pairs found.")
        return

    print(f"Found {len(pairs)} labeled images")
    dirs = ensure_split_dirs(DATASET_ROOT)
    split_and_move(pairs, dirs)
    print("Split complete.")


if __name__ == "__main__":
    main()
