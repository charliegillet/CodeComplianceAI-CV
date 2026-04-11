# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Code Capture AI** is a product by **Geopogo** (Berkeley, CA — 3D geospatial visualization company, founded 2014, Unreal Engine-powered) in collaboration with **Architecttura**. The goal is an AI-powered platform where architects upload floor plan PDFs/PNGs and receive **ADA/AODA building code compliance analysis** via computer vision.

This repo contains the **Computer Vision pipeline** — annotation tooling, dataset preparation, and YOLOv12 model training for detecting accessibility-relevant objects in architectural floor plans.

## Architecture & Workflow

```
Raw PDF floor plans (Architecttura / Google Drive / website uploads)
  → PDF-to-image extraction (PyMuPDF/fitz)
  → Manual annotation in Label Studio (bounding boxes)
  → Export as YOLO format (.txt label files + images)
  → YOLOv12 training (ultralytics)
  → Trained model API → CodeCapture website for live analysis
```

### Key Directories

- `CodeComplianceAI-CV/` — Main CV pipeline code and datasets
  - `images/` — 117 source floor plan images (10800x7200 and 10800x9000)
  - `image_chunks/` — Images distributed across 6 team members for Label Studio annotation
  - `docs/` — Setup guides (Label Studio ML backend, etc.)
- `Floorplan_Dataset3_3_10_2026/` — 33 real-world architectural PDFs from Architecttura for annotation
- `reference0331/` — Meeting notes, Slack logs, team planning docs (not code)
- `pdftoimg.py` — Quick script to extract floor plan images from PDFs using PyMuPDF

## Tech Stack

- **Python 3.11+** with venv (`.venv/`)
- **YOLOv12** (ultralytics) — attention-centric object detection model
- **Label Studio** — annotation tool; export in YOLO format; supports ML backend for pre-labeling
- **OpenCV** — image processing
- **PyMuPDF (fitz)** — PDF to image extraction
- **PostgreSQL (Neon)** — production database for storing trained data and user projects
- **Replit** — current website hosting environment

## Object Detection Classes

### v1 Training Classes (active — 117 images, 6 annotators)

These 17 classes are being actively labeled and trained per `docs/annotation_guide_v1.md`. Chosen based on: frequency in Architecttura floor plans, visual distinguishability at model resolution, and ADA/AODA compliance value.

```
 0 = bathtub              (ADA 9/10 — grab bars, seat, 30"x60" clear floor space)
 1 = corridor             (ADA 10/10 — min 36" width, slope limits; NOTE: semantic class, low instance count)
 2 = counter              (ADA 10/10 — lowered section 36" max height, 36" min length required)
 3 = dimension_line       (ADA 10/10 — critical for verifying all ADA clearances via OCR)
 4 = door                 (ADA 10/10 — clear width 32", maneuvering clearance, hardware, closing force)
 5 = door_tag             (ADA 7/10 — links to door schedule for width, hardware, closer specs)
 6 = drinking_fountain    (ADA 10/10 — spout 36" max, knee clearance, 50% per floor must be accessible)
 7 = elevator             (ADA 10/10 — min 51"x68" car, Braille controls, audible signals)
 8 = handrail             (ADA 9/10 — 34-38" height, 1.25-2" diameter, extensions at top/bottom of stairs/ramps)
 9 = ramp                 (ADA 10/10 — max 1:12 slope, 36" width, handrails, landings; NOTE: rare in dataset)
10 = room_tag             (ADA 8/10 — identifies room function → determines applicable ADA requirements)
11 = shower               (ADA 10/10 — roll-in 30"x60" or transfer 36"x36", flush threshold, grab bars, seat)
12 = sink                 (ADA 10/10 — knee clearance 27", rim height 34" max, insulated pipes)
13 = slope_arrow          (ADA 9/10 — verifies ramp and walkway slope compliance)
14 = stairs               (ADA 9/10 — tread/riser dims, handrails 34-38"; flags need for accessible alternative)
15 = toilet               (ADA 10/10 — centerline 16-18" from wall, seat height 17-19", clear floor space)
16 = urinal               (ADA 9/10 — rim 17" max, flush controls 44" max, 30"x48" clear floor space)
```

**Known data gaps:** ramp (0 instances in sample labels), slope_arrow (0 instances), elevator (4 instances), corridor (27 instances — from Charlie's 10 images). Classes with < 30 instances across all 117 images may need to be deferred to v2.

**v1 excludes (deferred to v2+):** window, grab_bar, accessible_parking, automatic_door, emergency_exit, wheelchair_turning_space. See annotation guide for rationale.

### Full ADA/AODA Element Taxonomy (reference for future phases)

Comprehensive list of all floor plan elements relevant to accessibility compliance, scored 1-10. Elements not in v1 training are candidates for future model expansion as dataset grows.

#### Doors & Openings
| Element | ADA Score | ADA/AODA Regulation |
|---------|:---------:|---------------------|
| Single swing door | 10 | ADA 404 — 32" clear width, 5 lbf max force, maneuvering clearance |
| Double swing door | 10 | At least one leaf must provide 32" clear opening |
| Sliding door | 9 | ADA 404.2 — one-hand operable hardware |
| Pocket door | 9 | Same as sliding; commonly used in accessible bathrooms |
| Revolving door | 10 | ADA 404.3.7 — CANNOT be on accessible route; adjacent door required |
| Automatic/power door | 10 | AODA OBC 3.8 requires at universal washrooms |
| Fire/smoke door | 8 | ADA 404.2.9 — closing force limits on accessible routes |
| Folding/accordion door | 7 | Same clear width and hardware requirements |
| Gate/turnstile | 9 | ADA 404.3.5 — accessible gate must accompany turnstiles |
| Vestibule (double-door entry) | 9 | ADA 404.2.6 — maneuvering clearance between doors in series |
| Cased opening (no door) | 7 | Must meet 32" clear width on accessible routes |

#### Vertical Circulation
| Element | ADA Score | ADA/AODA Regulation |
|---------|:---------:|---------------------|
| Stairs (all types) | 9 | ADA 504 — tread/riser dims, nosings, handrails 34-38" |
| Ramp (straight) | 10 | ADA 405 — max 1:12 slope, 36" width, handrails when rise > 6" |
| Ramp (switchback) | 10 | Same + landing requirements at turns |
| Curb ramp | 10 | ADA 406 — required at curb transitions, detectable warnings |
| Passenger elevator | 10 | ADA 407 — min 51"x68" car, Braille controls, audible signals |
| LULA elevator | 9 | ADA 408 — smaller elevators for limited vertical travel |
| Platform lift | 10 | ADA 410 — permitted only in specific conditions |
| Escalator | 7 | Not accessible; must have accessible alternative |
| Spiral/curved stairs | 8 | ADA 504.2 generally prohibits on accessible routes |

#### Plumbing Fixtures
| Element | ADA Score | ADA/AODA Regulation |
|---------|:---------:|---------------------|
| Toilet / water closet | 10 | ADA 604 — centerline 16-18" from wall, seat 17-19" height |
| Urinal | 9 | ADA 605 — rim 17" max, flush controls 44" max |
| Lavatory / sink | 10 | ADA 606 — 27" knee clearance, 34" max rim, insulated pipes |
| Kitchen sink | 8 | ADA 804 — 34" max counter in accessible kitchens |
| Roll-in shower | 10 | ADA 608.2.2 — 30"x60" min, flush threshold, grab bars, seat |
| Transfer shower | 10 | ADA 608.2.1 — exactly 36"x36", grab bars on 3 walls |
| Bathtub | 9 | ADA 607 — grab bars, seat, 30"x60" clear floor space |
| Drinking fountain | 10 | ADA 602 — spout 36" max, knee clearance, 50% per floor accessible |
| Grab bar (toilet) | 10 | ADA 604.5 — side wall 42" min, rear wall 36" min, at 33-36" height |
| Grab bar (shower/tub) | 10 | ADA 607.4/608.3 — specific locations per fixture type |

#### Accessibility-Specific Elements
| Element | ADA Score | ADA/AODA Regulation |
|---------|:---------:|---------------------|
| Wheelchair turning space | 10 | ADA 304 — 60" diameter circle or T-shaped |
| Clear floor space | 10 | ADA 305 — 30"x48" at every accessible element |
| Maneuvering clearance | 10 | ADA 404.2.4 — varies by door type and approach |
| Accessible parking space | 10 | ADA 502 — 96" min width, signage, connected to accessible route |
| Van-accessible parking | 10 | ADA 502 — 96" access aisle, 98" vertical clearance |
| Detectable warning surface | 9 | ADA 705 — truncated domes at transit/curb ramps |
| Accessible signage (Braille) | 9 | ADA 703 — required at all permanent rooms |
| ISA symbol (wheelchair icon) | 9 | ADA 703.7 — required at accessible entrances, parking, restrooms |
| Lowered counter section | 10 | ADA 904 — 36" max height, 36" min length |
| Area of refuge | 10 | ADA 207.1/IBC — accessible waiting area in stairwells |
| Power door operator button | 9 | AODA requires at universal washrooms |
| Knee/toe clearance zone | 9 | ADA 306 — under sinks, counters, tables |

#### Annotations & Dimensions
| Element | ADA Score | ADA/AODA Regulation |
|---------|:---------:|---------------------|
| Dimension line | 10 | Critical for verifying all ADA clearances |
| Room label / tag | 8 | Identifies function → determines ADA requirements |
| Scale bar | 8 | Enables measurement when explicit dimensions absent |
| Slope indicator arrow | 9 | Verifies ramp and walkway slope compliance |
| Level change symbol | 9 | ADA requires ramp/lift for changes > 1/2" |
| Elevation marker | 7 | Identifies floor levels and height changes |
| Door number/tag | 7 | Links to door schedule (width, hardware, closer specs) |
| Threshold detail marker | 8 | ADA 404.2.5 — max 1/2" threshold at accessible doors |

#### Structural Elements
| Element | ADA Score | Notes |
|---------|:---------:|-------|
| Exterior wall | 6 | Defines building envelope, entry locations |
| Interior wall | 6 | Defines corridor widths, room boundaries |
| Column | 6 | Can obstruct accessible routes |
| Handrail/railing | 9 | ADA 505 — 34-38" height, extensions at top/bottom |
| Floor level change | 8 | ADA 303 — changes > 1/4" must be beveled, > 1/2" ramped |

#### Safety & Egress
| Element | ADA Score | Notes |
|---------|:---------:|-------|
| Emergency exit door | 10 | Must have accessible hardware, on accessible egress route |
| Exit sign (tactile) | 8 | ADA 216.4 — tactile required at exit doors |
| Fire alarm pull station | 8 | ADA 309 — one-hand operable, 48" max height |
| Visual alarm/strobe | 8 | ADA 702 — required in accessible spaces for hearing-impaired |

#### Furniture & Fixed Elements
| Element | ADA Score | Notes |
|---------|:---------:|-------|
| Service/reception counter | 10 | ADA 904 — lowered section required |
| Kitchen counter | 8 | ADA 804 — 34" max in accessible kitchens |
| Desk/workstation | 7 | ADA 902 — 5% must be accessible, knee clearance |
| Toilet paper dispenser | 8 | ADA 604.7 — 7-9" in front of toilet, 15-48" height |
| Mirror | 7 | ADA 603.3 — bottom edge 40" max |

#### Site & Outdoor
| Element | ADA Score | Notes |
|---------|:---------:|-------|
| Curb cut / curb ramp | 10 | ADA 406 — required at all curb transitions |
| Sidewalk / path | 9 | ADA 402 — 36" wide, max 1:20 slope |
| Accessible entrance | 10 | ADA 206.4 — 60% of public entrances must be accessible |
| Drop-off / loading zone | 9 | ADA 503 — 60" access aisle, 20' min length |
| Parking access aisle | 10 | ADA 502.3 — 60" min, level, marked |

### Training Strategy Notes

- **Dataset reality:** 117 images, ~10800x7200 resolution. Ultralytics recommends 1,500+ images/class. Transfer learning from COCO pretrained weights helps but cannot close a 10x gap.
- **Consider increasing `imgsz`** from 1024 to 1280+ — small fixtures (toilet, sink) are only ~8-15px at 1024.
- **Measurement pipeline:** Many ADA checks (corridor width >= 36", door clearance >= 32", turning radius >= 60") are spatial relationships, not objects. Detect walls/doors/fixtures with YOLO, extract measurements via OCR on dimension lines, compute compliance in code.
- **Two-stage approach for subtypes:** If door type or fixture subtype matters, use YOLO for coarse detection ("door") then a classifier on cropped regions for fine-grained classification ("swing" vs "sliding" vs "pocket").
- **Inter-annotator agreement:** Before adding new classes, have 2 annotators independently label the same 5 images and measure per-class IoU agreement. Only keep classes with > 80% agreement.


## Commands

```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Batch PDF to image extraction (all Architecttura floor plans)
python pdftoimg.py

# Label Studio (local annotation server)
pip install label-studio
label-studio start

# YOLOv12 training (once dataset is ready)
pip install ultralytics
yolo detect train data=dataset.yaml model=yolov12n.pt epochs=100 imgsz=1024

# Run tests
cd CodeComplianceAI-CV
pytest
```

## Core Principles

- **Simplicity First**: Make every change as simple as possible. Minimal code impact.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary.
- **Demand Elegance**: For non-trivial changes, pause and ask "is there a more elegant way?"
- Keep pipelines modular and testable
- Prefer deterministic processing over heuristics when possible
- Use type hints and pathlib (not os.path)
- Prefer dataclasses for structured objects
- Keep functions under ~50 lines
- Prefer minimal diffs — do not rewrite large modules unless necessary
- Ask before introducing new libraries

## Label Studio Best Practices

- Draw **tight bounding boxes** around each object
- Label **consistently** across all annotators — follow the class taxonomy above
- Ignore clutter; focus only on accessibility-relevant architectural elements
- Export as **YOLO format** (produces `images/` + `labels/` + `classes.txt`)
- Use Label Studio's ML backend to connect a trained YOLO model for **pre-annotation** to speed up labeling
- Label Studio + HuggingFace SDK integration supports importing HF datasets and connecting HF models for active learning

## Auto-Commit and Push Rule

**MANDATORY**: After every change you make to any file in this repository, you MUST:

1. Stage the changed files: `git add <specific files you changed>`
2. Commit with a clear message describing what changed: `git commit -m "description of change"`
3. Push to your feature branch: `git push origin <current-branch>`

This applies to EVERY change — no exceptions. Do not batch changes. Commit and push immediately after each logical change.

- Always push to the current feature branch
- Never force push
- Use descriptive commit messages that explain the "why"
- If a pre-commit hook fails, fix the issue and create a NEW commit (never amend)

## Workflow Orchestration

This project involves coordination between multiple teams:
- **CV Team** (Charlie, Noor, Amogh, Gowri): annotation, model training, dataset curation
- **Web Team** (Dylan, Jonah): website, Label Studio integration, file upload/download
- **Data Team** (Anna, Nick): Neon database, data storage architecture
- **Testing** (Silvio, Zachary): upload drawings, provide feedback on AI results
- **Leadership** (Dave, Mike, Dino): direction, stakeholder outreach, architecture guidance

When making changes, consider how they affect the pipeline end-to-end: annotation → export → training → API → website.

### Workflow Rules

- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately
- Use subagents to keep main context window clean
- Never mark a task complete without proving it works
- When given a bug: just fix it. Point at logs, errors, failing tests — then resolve them.

## Agent Team Strategy

Use agent teams for any task that benefits from parallel work across independent modules. Teams are enabled via `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in settings.

### When to Use Teams

- Multi-file features spanning frontend, backend, and tests
- Research + implementation in parallel
- Debugging with competing hypotheses
- Any task with 3+ independent subtasks that don't touch the same files

### When NOT to Use Teams

- Sequential tasks with heavy dependencies between steps
- Changes to a single file or tightly coupled files
- Simple bug fixes or small tweaks

### Team Configuration

- Start with 3-5 teammates for most workflows
- Use delegate mode (`Shift+Tab`) when the lead should only coordinate
- Use `SendMessage` (type: "message") for direct teammate communication
- Use `TaskCreate`/`TaskUpdate`/`TaskList` for work coordination
- Mark tasks `completed` only after verification passes

## Workflow Orchestration

### 1. Plan Mode Default

- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately
- Write detailed specs upfront to reduce ambiguity

### 2. Subagent Strategy

- Use subagents to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- One task per subagent for focused execution

### 3. Verification Before Done

- Never mark a task complete without proving it works
- Run tests, check logs, demonstrate correctness
- Ask: "Would a staff engineer approve this?"

### 4. Autonomous Bug Fixing

- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests — then resolve them
- Go fix failing CI tests without being told how