# Code Capture AI — Computer Vision Pipeline

AI-powered ADA/AODA building code compliance analysis for architectural floor plans. Upload a floor plan PDF, get back accessibility violations detected by computer vision.

Built by [Geopogo](https://geopogo.com) (Berkeley, CA) in collaboration with Architecttura.

## How It Works

```
PDF floor plans
  → Image extraction (PyMuPDF @ 300 DPI)
  → Auto-annotation (Grounding DINO / Gemini 2.5 Flash)
  → Manual review & correction (Label Studio)
  → Train/val split (80/20)
  → YOLOv12 training (ultralytics)
  → Trained model serves predictions via API
```

## Detection Classes

The model detects 10 accessibility-relevant architectural elements:

| ID | Class | ADA Relevance |
|----|-------|---------------|
| 0 | door | Clear width 32", maneuvering clearance, hardware |
| 1 | window | Operable hardware in accessible units |
| 2 | corridor | Min 36" width, slope limits |
| 3 | toilet | Centerline 16-18" from wall, clear floor space |
| 4 | stairs | Tread/riser dims, handrails; flags need for accessible alternative |
| 5 | ramp | Max 1:12 slope, 36" width, handrails, landings |
| 6 | elevator | Min 51"x68" car, Braille controls |
| 7 | dimensions | Dimension lines — critical for verifying all ADA clearances |
| 8 | room_tag | Identifies room function → applicable ADA requirements |
| 9 | sink | Knee clearance 27", rim height 34" max |

## Quick Start

```bash
# 1. Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Extract floor plan images from PDFs
python pdftoimg.py

# 3. Auto-annotate images (choose a backend)
python auto_annotate.py --model grounding-dino       # local, zero-shot
python auto_annotate.py --model gemini --dry-run      # requires GOOGLE_API_KEY

# 4. Import pre-annotations into Label Studio for review
python import_to_labelstudio.py

# 5. Run the full pipeline end-to-end
python run_pipeline.py

# 6. Or run individual steps
python run_pipeline.py --skip-extract --skip-annotate  # resume from split
python run_pipeline.py --review                        # pause after annotation
```

## Pipeline Scripts

| Script | Purpose |
|--------|---------|
| `pdftoimg.py` | Extract all pages from PDFs as PNGs at 300 DPI |
| `auto_annotate.py` | Zero-shot annotation via Grounding DINO or Gemini 2.5 Flash |
| `import_to_labelstudio.py` | Convert YOLO labels to Label Studio JSON for manual review |
| `split_dataset.py` | Shuffle and split labeled data into train/val (80/20, seed=42) |
| `train.py` | YOLOv12 training with augmentation tuned for B&W line drawings |
| `run_pipeline.py` | Orchestrate all steps with skip flags and a review gate |

## Project Structure

```
CodeComplianceAI-CV/
├── auto_annotate.py          # Auto-labeling (Grounding DINO / Gemini)
├── import_to_labelstudio.py  # YOLO → Label Studio JSON converter
├── pdftoimg.py               # PDF page extraction
├── split_dataset.py          # Train/val split
├── train.py                  # YOLOv12 training config
├── run_pipeline.py           # End-to-end orchestrator
├── test_auto_annotate.py     # Tests
├── dataset.yaml              # YOLO dataset config (10 classes)
├── requirements.txt          # Python dependencies
├── images/                   # 117 source floor plan images
├── image_chunks/             # Images split across 6 annotators
├── docs/                     # Setup guides (Label Studio ML backend)
└── dataset/                  # Generated train/val splits (gitignored)
    ├── images/{train,val}/
    └── labels/{train,val}/
```

## Training Configuration

The training script (`train.py`) is configured for architectural line drawings:

- **Model:** YOLOv12n (nano) with COCO pretrained weights
- **Image size:** 1024px (source images are 10800x7200)
- **Color augmentation:** Disabled (hsv_h/s/v = 0) — floor plans are B&W
- **Geometric augmentation:** 90° rotation, horizontal/vertical flips
- **Mosaic:** Disabled in final 10 epochs for fine-tuning

## Auto-Annotation Backends

### Grounding DINO (default)
Zero-shot object detection via HuggingFace Transformers. Runs locally, no API key needed. Supports MPS (Apple Silicon), CUDA, and CPU.

```bash
python auto_annotate.py --model grounding-dino --threshold 0.25
```

### Gemini 2.5 Flash
Google's multimodal model with structured JSON output. Requires `GOOGLE_API_KEY` env var.

```bash
export GOOGLE_API_KEY=your_key_here
python auto_annotate.py --model gemini
```

## Dataset

- **117 floor plan images** (10800x7200 and 10800x9000 resolution)
- **33 real-world architectural PDFs** from Architecttura (`Floorplan_Dataset3_3_10_2026/`)
- **6 annotators** labeling in parallel via Label Studio
- Export format: YOLO (`.txt` label files with normalized bounding boxes)

## Tech Stack

- **Python 3.11+**
- **YOLOv12** (ultralytics) — attention-centric object detection
- **Label Studio** — annotation and review
- **Grounding DINO** — zero-shot pre-annotation
- **Gemini 2.5 Flash** — multimodal pre-annotation
- **PyMuPDF (fitz)** — PDF to image extraction
- **Pillow / OpenCV** — image processing

## Tests

```bash
pytest
```

## License

Proprietary — Geopogo, Inc.
