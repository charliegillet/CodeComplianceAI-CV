# Label Studio Setup Guide

## 1. Install Label Studio

Open your terminal and run:

```bash
pip install label-studio
```

## 2. Start Label Studio

```bash
label-studio start
```

This opens Label Studio in your browser at http://localhost:8080. Create an account (this is local, just pick any email/password).

## 3. Create a Project

1. Click **Create Project**
2. Name it something like "Floor Plan Annotation"
3. Skip the data import for now — click **Save**

## 4. Set Up the Labeling Config

1. Go to **Settings** (gear icon in top right of your project)
2. Click **Labeling Interface**
3. Click **Code** (top right of the interface editor)
4. Delete everything in the code box
5. Paste the contents of `labeling_config.xml` (in this same docs folder)
6. Click **Save**

You should see all 17 classes listed with colored labels.

## 5. Import Images

1. From your project page, click **Import**
2. Click **Upload Files**
3. Select the floor plan images you've been assigned (check your folder in `image_chunks/`)
4. Click **Import**

Your images will appear as tasks in the project.

## 6. Annotate

1. Click on any image to open it
2. Select a class from the label panel on the right
3. Click and drag on the image to draw a bounding box around the element
4. Repeat for every instance of every class on the image
5. Click **Submit** when the image is fully annotated

Tips:
- Zoom in with your scroll wheel — floor plans are large
- Use the number keys (1-9) to quickly switch between the first 9 classes
- If you make a mistake, click the box and press **Delete**
- Review the annotation guide for bounding box rules per class

## 7. Export

When you're done annotating (or want to checkpoint your progress):

1. Go to your project page (click the project name in the top bar)
2. Click **Export**
3. Select **YOLO** format
4. Click **Export**

This downloads a zip containing:
- `labels/` — one `.txt` file per image with bounding box annotations
- `classes.txt` — list of class names
- `notes.json` — metadata

Send Charlie the exported zip file.
