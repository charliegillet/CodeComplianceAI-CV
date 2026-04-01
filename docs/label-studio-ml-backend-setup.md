# Label Studio ML Backend Setup for YOLO Pre-Annotation

This guide walks through connecting a YOLO model to Label Studio as an ML backend, enabling pre-annotation of Architecttura floor plans. Annotators review and correct model predictions instead of drawing every bounding box from scratch.

## Prerequisites

- Docker and Docker Compose installed ([get Docker](https://docs.docker.com/get-docker/))
- Label Studio running locally (default: `http://localhost:8080`)
- A Label Studio API key (see [Get Your API Key](#1-get-your-label-studio-api-key))
- Git installed

## Overview

```
Label Studio (localhost:8080)
    ↕ REST API
YOLO ML Backend (localhost:9090, Docker)
    ↕ loads
Custom YOLO model (.pt file)
```

The ML backend runs as a Docker container. When you open a labeling task, Label Studio asks the backend for predictions. The backend runs YOLO inference and returns bounding boxes as pre-annotations.

---

## Step 1: Get Your Label Studio API Key

1. Open Label Studio at `http://localhost:8080`
2. Click your profile icon (top right) → **Account & Settings**
3. Copy the **Access Token** — you will need this for the Docker config

If Label Studio is not running yet:

```bash
pip install label-studio
label-studio start
```

This starts Label Studio on port 8080. Create an account on first launch.

---

## Step 2: Clone the ML Backend Repository

```bash
cd /Users/charlie/geopogo/CodeComplianceAI-CV
git clone https://github.com/HumanSignal/label-studio-ml-backend.git
cd label-studio-ml-backend/label_studio_ml/examples/yolo
```

This is the official HumanSignal YOLO ML backend example with Docker support.

---

## Step 3: Add Your YOLO Model

Create a `models` directory and place your trained model file inside it:

```bash
# From inside the yolo example directory
mkdir -p models

# Option A: Use a pretrained YOLOv12 model (downloads automatically on first run)
# No file needed — set model_path="yolov12n.pt" in the labeling config (Step 5)

# Option B: Use our custom-trained model (once we have one)
cp /path/to/our/best.pt models/codecapture_floorplan.pt
```

Directory structure should look like:

```
label_studio_ml/examples/yolo/
├── docker-compose.yml
├── Dockerfile
├── models/
│   └── codecapture_floorplan.pt   ← your custom model (optional)
├── model.py
└── requirements.txt
```

---

## Step 4: Configure docker-compose.yml

Open `docker-compose.yml` and update the environment variables:

```bash
# From the yolo example directory
nano docker-compose.yml
```

Set these values:

```yaml
services:
  yolo:
    container_name: yolo-ml-backend
    build: .
    environment:
      # REQUIRED: Point to your Label Studio instance
      # Use host.docker.internal because Docker can't reach "localhost"
      - LABEL_STUDIO_URL=http://host.docker.internal:8080
      # REQUIRED: Paste your API key from Step 1
      - LABEL_STUDIO_API_KEY=<your-api-key-here>
      # Allow loading custom model files from the mounted volume
      - ALLOW_CUSTOM_MODEL_PATH=true
      # Optional: set log level for debugging
      - LOG_LEVEL=DEBUG
    ports:
      - "9090:9090"
    volumes:
      # Mount our models directory into the container
      - ./models:/app/models
```

**Important**: Replace `<your-api-key-here>` with the actual token from Step 1.

---

## Step 5: Create a Label Studio Project with Our 10 Classes

### 5a. Create a New Project

1. In Label Studio, click **Create Project**
2. Name it: `CodeCapture Floor Plans`
3. Go to the **Labeling Setup** tab
4. Choose **Custom template**
5. Paste the following XML config:

```xml
<View>
  <Image name="image" value="$image"/>
  <RectangleLabels name="label" toName="image"
                   model_score_threshold="0.25"
                   model_path="yolov12n.pt">
    <Label value="door"            background="#FF0000"/>
    <Label value="window"          background="#0000FF"/>
    <Label value="corridor"        background="#00FF00"/>
    <Label value="toilet"          background="#FF00FF"/>
    <Label value="stairs"          background="#FFA500"/>
    <Label value="ramp"            background="#00FFFF"/>
    <Label value="elevator"        background="#FFFF00"/>
    <Label value="dimensions"      background="#800080"/>
    <Label value="room_tag"        background="#808080"/>
    <Label value="sink"            background="#008080"/>
  </RectangleLabels>
</View>
```

**Notes on the config:**
- `model_score_threshold="0.25"` filters out low-confidence predictions (adjust as needed; lower = more boxes, higher = fewer but more confident)
- `model_path="yolov12n.pt"` tells the backend which model to load. Change this to `"codecapture_floorplan.pt"` once we have a custom-trained model
- Each `<Label>` has a distinct `background` color for visual clarity during annotation

### 5b. Upload Floor Plan Images

1. Go to your project, click **Import**
2. Upload the extracted floor plan PNGs from the Architecttura dataset
3. Images should be pre-extracted from PDFs using `pdftoimg.py` at 300 DPI

---

## Step 6: Start the ML Backend

```bash
# From the yolo example directory
cd /Users/charlie/geopogo/CodeComplianceAI-CV/label-studio-ml-backend/label_studio_ml/examples/yolo

docker-compose up --build
```

Wait for the container to start. You should see logs like:

```
yolo-ml-backend  | Starting ML backend server...
yolo-ml-backend  | Listening on port 9090
```

To run in the background:

```bash
docker-compose up --build -d
```

To check logs when running in background:

```bash
docker-compose logs -f
```

To stop the backend:

```bash
docker-compose down
```

---

## Step 7: Connect the ML Backend to Your Project

1. In Label Studio, open your **CodeCapture Floor Plans** project
2. Go to **Settings** → **Machine Learning**
3. Click **Add Model**
4. Enter the URL: `http://localhost:9090`
5. Click **Validate and Save**
6. Toggle **Use for interactive preannotations** to ON

You should see a green checkmark indicating the backend is connected.

### Verify It Works

1. Open any labeling task (click on an image)
2. You should see pre-annotated bounding boxes appear on the image
3. If no boxes appear, check:
   - The ML backend container is running (`docker-compose logs -f`)
   - The API key is correct
   - The Label Studio URL uses `host.docker.internal` (not `localhost`) in docker-compose.yml

---

## Step 8: Annotate Floor Plans

### Annotation Workflow

1. Open a task — pre-annotations appear as bounding boxes
2. **Review** each box: is the class correct? Is the box tight around the object?
3. **Correct** any wrong predictions:
   - Drag box edges to resize
   - Click a box and change its label from the sidebar
   - Delete false positives (select box → press Delete/Backspace)
4. **Add** missed objects: draw new bounding boxes for anything the model missed
5. Click **Submit** when done

### Annotation Quality Guidelines

- Draw **tight bounding boxes** — edges should touch the object boundary
- Label **consistently** — follow the 10-class taxonomy exactly
- Ignore clutter — only label accessibility-relevant architectural elements
- When in doubt about a class, check with the team before guessing

---

## Step 9: Export Annotations in YOLO Format

### Manual Export

1. Go to your project in Label Studio
2. Click **Export**
3. Select **YOLO** format
4. Click **Export** — downloads a ZIP file

The ZIP contains:

```
export/
├── images/
│   ├── image1.png
│   ├── image2.png
│   └── ...
├── labels/
│   ├── image1.txt      ← one line per object: class_id x_center y_center width height
│   ├── image2.txt
│   └── ...
├── classes.txt          ← class names (one per line, in order)
└── notes.json
```

Each `.txt` label file contains lines in YOLO format:

```
0 0.5123 0.3456 0.0890 0.1234
1 0.2345 0.6789 0.0456 0.0678
```

Where: `class_id x_center y_center box_width box_height` (all normalized 0-1).

### Organize for Training

After exporting, split the data into train/val/test:

```bash
# From the CodeComplianceAI-CV directory
mkdir -p dataset/images/{train,val,test}
mkdir -p dataset/labels/{train,val,test}

# Move ~80% to train, ~10% to val, ~10% to test
# (Use a script for this — do not do it manually for large datasets)
```

---

## Step 10: The Active Learning Loop

Active learning is the iterative cycle that makes annotating faster over time:

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  1. ANNOTATE                                        │
│     Upload images → Model pre-annotates →           │
│     Annotators review & correct                     │
│                                                     │
│  2. EXPORT                                          │
│     Export corrected annotations in YOLO format      │
│                                                     │
│  3. TRAIN                                           │
│     Train/fine-tune YOLO on the corrected data      │
│     yolo detect train data=dataset.yaml \           │
│       model=yolov12n.pt epochs=100 imgsz=1024       │
│                                                     │
│  4. UPDATE BACKEND                                  │
│     Copy new best.pt to models/ directory           │
│     Update model_path in labeling config             │
│     Restart ML backend                              │
│                                                     │
│  5. PREDICT                                         │
│     New images get better pre-annotations            │
│     Annotators spend less time correcting            │
│                                                     │
│  6. REPEAT                                          │
│     Each cycle improves the model                   │
│     → fewer corrections needed                      │
│     → faster annotation                             │
│     → more training data                            │
│     → better model                                  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Running the Loop in Practice

**Cycle 1 (bootstrap):**
- Use pretrained `yolov12n.pt` (COCO classes, not floor-plan-specific)
- Pre-annotations will be noisy — annotators do most of the work manually
- Export ~50-100 corrected floor plan annotations
- Train first custom model

**Cycle 2+:**
- Load custom model as the ML backend
- Pre-annotations improve with each cycle
- Focus annotation effort on images where the model is least confident

### Updating the Model After Training

```bash
# After training completes, copy the best model
cp runs/detect/train/weights/best.pt \
   /Users/charlie/geopogo/CodeComplianceAI-CV/label-studio-ml-backend/label_studio_ml/examples/yolo/models/codecapture_floorplan.pt

# Restart the ML backend to load the new model
cd /Users/charlie/geopogo/CodeComplianceAI-CV/label-studio-ml-backend/label_studio_ml/examples/yolo
docker-compose restart
```

Then update the labeling config to point to the new model:

```xml
<RectangleLabels name="label" toName="image"
                 model_score_threshold="0.25"
                 model_path="codecapture_floorplan.pt">
```

### Prioritizing Uncertain Samples

To maximize the value of each annotation cycle:

1. In Label Studio project **Settings** → **Machine Learning**
2. Under **Task Sampling**, select **Uncertainty Sampling**
3. This shows annotators the images where the model is least confident first
4. These are the most valuable images to correct — they teach the model the most

---

## Troubleshooting

### ML backend won't connect

- Verify the container is running: `docker ps | grep yolo`
- Check logs: `docker-compose logs -f`
- Ensure `LABEL_STUDIO_URL` uses `http://host.docker.internal:8080` (not `localhost`)
- Verify the API key is correct (re-copy from Label Studio Account Settings)

### No pre-annotations appear

- Check that **Use for interactive preannotations** is toggled ON in project Settings → Machine Learning
- Check `model_score_threshold` — if set too high, low-confidence predictions are filtered out. Try lowering to `0.1`
- Check the ML backend logs for errors during prediction

### Pre-annotations have wrong class names

- The pretrained `yolov12n.pt` uses COCO class names (person, car, etc.), not our floor plan classes
- This is expected for Cycle 1 — the pre-annotations from a COCO model will not be useful for floor plans
- Once we train on our own annotated data, class names will match

### Docker build fails

```bash
# Ensure Docker daemon is running
docker info

# Try rebuilding from scratch
docker-compose build --no-cache
docker-compose up
```

### Port 9090 already in use

```bash
# Find what's using port 9090
lsof -i :9090

# Either stop that process or change the port in docker-compose.yml:
# ports:
#   - "9091:9090"
# Then connect Label Studio to http://localhost:9091
```

---

## Quick Reference

| Action | Command |
|--------|---------|
| Start Label Studio | `label-studio start` |
| Start ML backend | `cd .../examples/yolo && docker-compose up --build` |
| Stop ML backend | `docker-compose down` |
| View ML backend logs | `docker-compose logs -f` |
| Restart after model update | `docker-compose restart` |
| Export annotations | Label Studio → Project → Export → YOLO |
| Train YOLO | `yolo detect train data=dataset.yaml model=yolov12n.pt epochs=100 imgsz=1024` |

## References

- [Label Studio YOLO ML Backend Docs](https://labelstud.io/guide/ml_tutorials/yolo)
- [HumanSignal ML Backend GitHub](https://github.com/HumanSignal/label-studio-ml-backend)
- [YOLO ML Backend README](https://github.com/HumanSignal/label-studio-ml-backend/blob/master/label_studio_ml/examples/yolo/README.md)
- [Label Studio Export Docs](https://labelstud.io/guide/export)
- [Label Studio Active Learning](https://docs.humansignal.com/guide/active_learning)
- [YOLO + Label Studio Blog Post](https://labelstud.io/blog/use-yolo26-with-label-studio-for-fast-bounding-box-pre-annotations/)
