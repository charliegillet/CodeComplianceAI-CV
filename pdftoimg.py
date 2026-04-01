"""Batch extract floor plan images from PDFs at 300 DPI.

Iterates over all PDFs in the input directory, extracts every page,
and saves as PNG with structured naming: {pdf_stem}_p{page}.png
"""

from pathlib import Path

import fitz  # pymupdf


INPUT_DIR = Path("Floorplan_Dataset3_3_10_2026")
OUTPUT_DIR = Path("CodeComplianceAI-CV/dataset/images/architecttura")
DPI = 300


def sanitize_stem(stem: str) -> str:
    """Convert a PDF filename stem into a clean, filesystem-safe name.

    Example: '1603 - Collins Barrow' -> '1603_Collins_Barrow'
    """
    return stem.replace(" - ", "_").replace(" ", "_").replace("__", "_")


def extract_pdf(pdf_path: Path, output_dir: Path) -> list[Path]:
    """Extract all pages from a single PDF as PNG images at 300 DPI."""
    doc = fitz.open(pdf_path)
    stem = sanitize_stem(pdf_path.stem)
    saved: list[Path] = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(dpi=DPI)
        out_path = output_dir / f"{stem}_p{page_num + 1}.png"
        pix.save(str(out_path))
        saved.append(out_path)

    doc.close()
    return saved


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(INPUT_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {INPUT_DIR}")
        return

    print(f"Found {len(pdfs)} PDFs in {INPUT_DIR}")
    total_pages = 0

    for pdf_path in pdfs:
        saved = extract_pdf(pdf_path, OUTPUT_DIR)
        total_pages += len(saved)
        print(f"  {pdf_path.name} -> {len(saved)} page(s)")

    print(f"\nDone: {total_pages} images saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
