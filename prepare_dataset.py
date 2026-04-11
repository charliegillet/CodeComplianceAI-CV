"""Prepare a YOLO dataset from Label Studio exports for training.

Unzips a Label Studio YOLO export, matches label files to source images
(handling UUID prefixes and filename character substitutions), and splits
into train/val sets ready for YOLOv12 training.

Usage:
    python prepare_dataset.py path/to/export.zip
    python prepare_dataset.py path/to/export.zip --train-ratio 0.9
"""

import argparse
import random
import shutil
import tempfile
import zipfile
from pathlib import Path


IMAGES_DIR = Path(__file__).parent / "images"
DATASET_ROOT = Path(__file__).parent / "dataset"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
SEED = 42


def strip_uuid_prefix(name: str) -> str:
    """Remove the UUID prefix Label Studio adds to filenames.

    Example: '231bec4f-2114_Farzat_Dental_p2' -> '2114_Farzat_Dental_p2'
    """
    parts = name.split("-", 1)
    if len(parts) == 2 and len(parts[0]) == 8 and all(c in "0123456789abcdef" for c in parts[0]):
        return parts[1]
    return name


def find_source_image(label_stem: str, images_dir: Path) -> Path | None:
    """Find the source image matching a label file stem.

    Handles Label Studio replacing '&' with '_' in filenames during export.
    For example, 'A701_Custodial_Plans_&_Elevations_p1' exports as
    'A701_Custodial_Plans__Elevations_p1' (the '&' is dropped, leaving '__').
    """
    clean_stem = strip_uuid_prefix(label_stem)

    for ext in IMAGE_EXTENSIONS:
        # Direct match
        candidate = images_dir / f"{clean_stem}{ext}"
        if candidate.exists():
            return candidate

        # Try restoring '&' where '__' appears (Label Studio drops '&' from '_&_')
        if "__" in clean_stem:
            restored = clean_stem.replace("__", "_&_")
            candidate = images_dir / f"{restored}{ext}"
            if candidate.exists():
                return candidate

    return None


def extract_and_match(
    zip_path: Path, images_dir: Path
) -> list[tuple[Path, Path]]:
    """Extract zip and return (label_file, source_image) pairs."""
    tmp_dir = Path(tempfile.mkdtemp(prefix="ls_export_"))
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(tmp_dir)

    labels_dir = tmp_dir / "labels"
    if not labels_dir.exists():
        print(f"No 'labels/' directory found in {zip_path.name}")
        return []

    pairs: list[tuple[Path, Path]] = []
    missing: list[str] = []

    for label_path in sorted(labels_dir.glob("*.txt")):
        source_img = find_source_image(label_path.stem, images_dir)
        if source_img is None:
            missing.append(label_path.stem)
        else:
            pairs.append((label_path, source_img))

    if missing:
        print(f"Warning: {len(missing)} labels could not be matched to source images:")
        for name in missing:
            print(f"  {name}")

    return pairs


def prepare_split_dirs(dataset_root: Path) -> None:
    """Create clean train/val directory structure."""
    for split in ("train", "val"):
        (dataset_root / "images" / split).mkdir(parents=True, exist_ok=True)
        (dataset_root / "labels" / split).mkdir(parents=True, exist_ok=True)


def split_and_copy(
    pairs: list[tuple[Path, Path]],
    dataset_root: Path,
    train_ratio: float,
) -> None:
    """Shuffle pairs and copy into train/val splits."""
    random.seed(SEED)
    shuffled = list(pairs)
    random.shuffle(shuffled)

    split_idx = max(1, int(len(shuffled) * train_ratio))
    # Ensure at least 1 image in val
    if split_idx == len(shuffled):
        split_idx = len(shuffled) - 1

    splits = {"train": shuffled[:split_idx], "val": shuffled[split_idx:]}

    for split_name, split_pairs in splits.items():
        img_dir = dataset_root / "images" / split_name
        lbl_dir = dataset_root / "labels" / split_name
        for label_path, source_img in split_pairs:
            # Use the source image stem (no UUID) for consistent naming
            stem = source_img.stem
            shutil.copy2(source_img, img_dir / source_img.name)
            shutil.copy2(label_path, lbl_dir / f"{stem}.txt")
        print(f"  {split_name}: {len(split_pairs)} images")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare YOLO dataset from Label Studio export zip(s)",
    )
    parser.add_argument(
        "zip_paths",
        nargs="+",
        type=Path,
        help="Path(s) to Label Studio YOLO export zip file(s)",
    )
    parser.add_argument(
        "--images-dir",
        type=Path,
        default=IMAGES_DIR,
        help=f"Directory containing source images (default: {IMAGES_DIR})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DATASET_ROOT,
        help=f"Output dataset directory (default: {DATASET_ROOT})",
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.8,
        help="Fraction of images for training (default: 0.8)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    all_pairs: list[tuple[Path, Path]] = []
    for zip_path in args.zip_paths:
        if not zip_path.exists():
            print(f"Zip file not found: {zip_path}")
            continue
        print(f"Processing {zip_path.name}...")
        pairs = extract_and_match(zip_path, args.images_dir)
        print(f"  Matched {len(pairs)} label/image pairs")
        all_pairs.extend(pairs)

    if not all_pairs:
        print("No label/image pairs found. Nothing to do.")
        return

    # Deduplicate by source image path (in case multiple zips contain the same image)
    seen: set[Path] = set()
    unique_pairs: list[tuple[Path, Path]] = []
    for label_path, source_img in all_pairs:
        if source_img not in seen:
            seen.add(source_img)
            unique_pairs.append((label_path, source_img))

    print(f"\nTotal: {len(unique_pairs)} unique labeled images")
    prepare_split_dirs(args.output)
    split_and_copy(unique_pairs, args.output, args.train_ratio)
    print(f"\nDataset ready at {args.output}/")
    print("Run 'python train.py' to start training.")


if __name__ == "__main__":
    main()
