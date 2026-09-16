"""
Script to create an ultra-resilient, professional Google Colab Notebook
with 100% Google Drive persistence (mount, auto-save checkpoints, resume support).
"""

import json

cells = []

def add_md(content):
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in content.strip().split("\n")]
    })

def add_code(content):
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in content.strip().split("\n")]
    })

# ==============================================================================
# Cell 1: Header & Architecture
# ==============================================================================
add_md("""# ᚱ Viking Rune Stones: Production-Grade YOLO Detection & Auto-Labeling
### Fully Persistent Google Drive Architecture (Zero-Data-Loss Pipeline)
---

**Features:**
- **Persistent Storage:** Everything (dataset, weights, logs, pseudo-labels) is directly saved to `MyDrive/Viking_Rune_Project/`.
- **Fault-Tolerant:** Automatic checkpointing (`last.pt` / `best.pt`) with seamless training resumption (`resume=True`).
- **Domain Geometry:** 17 Classes (16 Runes + Separator) with strict radial curvature on circular/oval bands.
- **Chirality Preserved:** `fliplr=0.0` prevents mirroring of asymmetric runes.
""")

# ==============================================================================
# Cell 2: Mount Google Drive
# ==============================================================================
add_md("""## 1. Mount Google Drive & Establish Directory Hierarchy
Connect your Google Drive so that all data, models, and outputs survive any runtime disconnections.
""")

add_code("""from google.colab import drive
import os
from pathlib import Path

# Mount Google Drive
drive.mount('/content/drive')

# Define Project Directory inside Google Drive
PROJECT_DIR = Path("/content/drive/MyDrive/Viking_Rune_Project")
DATASET_DIR = PROJECT_DIR / "dataset"
RUNS_DIR    = PROJECT_DIR / "training_runs"
REAL_DIR    = PROJECT_DIR / "real_stones"
LABELS_DIR  = PROJECT_DIR / "auto_labeled_stones"

for p in [PROJECT_DIR, DATASET_DIR, RUNS_DIR, REAL_DIR, LABELS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

print("✓ Google Drive Connected Successfully!")
print(f"  Project Root : {PROJECT_DIR}")
print(f"  Dataset Dir  : {DATASET_DIR}")
print(f"  Runs Dir     : {RUNS_DIR}")
print(f"  Real Stones  : {REAL_DIR}")
""")

# ==============================================================================
# Cell 3: GPU & Environment Setup
# ==============================================================================
add_md("""## 2. Environment Verification & Package Installation
Verify hardware accelerator (GPU) and install Ultralytics YOLO.
""")

add_code("""!nvidia-smi

!pip install -q ultralytics pyyaml opencv-python pillow matplotlib seaborn

import sys
import torch
import yaml
import shutil
import cv2
import numpy as np
import matplotlib.pyplot as plt
from ultralytics import YOLO

print(f"\\nPyTorch Version : {torch.__version__}")
print(f"CUDA Available  : {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Active GPU      : {torch.cuda.get_device_name(0)}")
""")

# ==============================================================================
# Cell 4: Synthetic Generator Code
# ==============================================================================
add_md("""## 3. High-Fidelity Synthetic Dataset Generator
Synthesizes stones with:
- Strict **Radial Normal Orientation** $\\vec{n}(\\theta)$ along circular/oval bands.
- **17 Classes:** 16 Younger Futhark Runes + Word Separator (`:`, `+`, `x`, `·`).
- Writes training & validation sets directly into Google Drive.
""")

add_code("""import random
import math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

IMG_SIZE         = 640
SAMPLES_PER_RUNE = 150    # 150 targeted images per class
SCENE_SAMPLES    = 1500   # 1500 multi-rune geometric monuments
TRAIN_SPLIT      = 0.85

RUNES = [
    {"id": 0, "name": "fehu", "latin": "F", "variants": [
        [[(0.50,0.00),(0.50,1.00)],[(0.50,0.22),(0.88,0.42)],[(0.50,0.48),(0.88,0.68)]],
        [[(0.45,0.00),(0.45,1.00)],[(0.45,0.20),(0.80,0.38)],[(0.45,0.42),(0.80,0.60)]]]},
    {"id": 1, "name": "uruz", "latin": "U", "variants": [
        [[(0.22,0.00),(0.22,1.00)],[(0.78,0.00),(0.78,0.62)],[(0.22,1.00),(0.78,0.62)]],
        [[(0.25,0.00),(0.25,1.00)],[(0.75,0.10),(0.75,0.60)],[(0.25,1.00),(0.75,0.60)]]]},
    {"id": 2, "name": "thurisaz", "latin": "Th", "variants": [
        [[(0.42,0.00),(0.42,1.00)],[(0.42,0.25),(0.85,0.50)],[(0.85,0.50),(0.42,0.75)]],
        [[(0.38,0.00),(0.38,1.00)],[(0.38,0.30),(0.78,0.50)],[(0.78,0.50),(0.38,0.70)]]]},
    {"id": 3, "name": "ansuz", "latin": "A", "variants": [
        [[(0.50,0.00),(0.50,1.00)],[(0.50,0.25),(0.15,0.48)],[(0.50,0.50),(0.15,0.73)]],
        [[(0.50,0.00),(0.50,1.00)],[(0.50,0.20),(0.22,0.40)],[(0.50,0.42),(0.22,0.62)]]]},
    {"id": 4, "name": "raidho", "latin": "R", "variants": [
        [[(0.35,0.00),(0.35,1.00)],[(0.35,0.10),(0.80,0.32)],[(0.80,0.32),(0.35,0.52)],[(0.35,0.52),(0.80,0.92)]]]},
    {"id": 5, "name": "kaunan", "latin": "K", "variants": [
        [[(0.32,0.00),(0.32,1.00)],[(0.32,0.22),(0.75,0.05)],[(0.32,0.78),(0.75,0.95)]],
        [[(0.35,0.00),(0.35,1.00)],[(0.35,0.30),(0.75,0.15)],[(0.35,0.70),(0.75,0.85)]]]},
    {"id": 6, "name": "hagalaz", "latin": "H", "variants": [
        [[(0.50,0.00),(0.50,1.00)],[(0.20,0.35),(0.80,0.65)]],
        [[(0.25,0.00),(0.25,1.00)],[(0.75,0.00),(0.75,1.00)],[(0.25,0.30),(0.75,0.70)]]]},
    {"id": 7, "name": "naudiz", "latin": "N", "variants": [
        [[(0.50,0.00),(0.50,1.00)],[(0.20,0.40),(0.80,0.60)]],
        [[(0.50,0.00),(0.50,1.00)],[(0.25,0.35),(0.75,0.55)]]]},
    {"id": 8, "name": "isaz", "latin": "I", "variants": [
        [[(0.50,0.00),(0.50,1.00)]]]},
    {"id": 9, "name": "ar_jera", "latin": "A_J", "variants": [
        [[(0.50,0.00),(0.50,1.00)],[(0.50,0.40),(0.85,0.65)]],
        [[(0.50,0.00),(0.50,1.00)],[(0.20,0.35),(0.80,0.65)]]]},
    {"id": 10, "name": "sowilo", "latin": "S", "variants": [
        [[(0.70,0.08),(0.30,0.08)],[(0.30,0.08),(0.70,0.92)],[(0.70,0.92),(0.30,0.92)]],
        [[(0.70,0.20),(0.30,0.80)]]]},
    {"id": 11, "name": "tiwaz", "latin": "T", "variants": [
        [[(0.50,0.00),(0.50,1.00)],[(0.50,0.25),(0.15,0.55)],[(0.50,0.25),(0.85,0.55)]],
        [[(0.50,0.00),(0.50,1.00)],[(0.50,0.18),(0.25,0.42)],[(0.50,0.18),(0.75,0.42)]]]},
    {"id": 12, "name": "berkanan", "latin": "B", "variants": [
        [[(0.30,0.00),(0.30,1.00)],[(0.30,0.08),(0.72,0.28)],[(0.72,0.28),(0.30,0.50)],[(0.30,0.50),(0.75,0.70)],[(0.75,0.70),(0.30,0.92)]]]},
    {"id": 13, "name": "mannaz", "latin": "M", "variants": [
        [[(0.18,0.00),(0.18,1.00)],[(0.82,0.00),(0.82,1.00)],[(0.18,0.05),(0.50,0.40)],[(0.82,0.05),(0.50,0.40)]],
        [[(0.25,0.00),(0.25,1.00)],[(0.75,0.00),(0.75,1.00)],[(0.25,0.15),(0.75,0.15)],[(0.25,0.45),(0.75,0.45)]]]},
    {"id": 14, "name": "laguz", "latin": "L", "variants": [
        [[(0.45,0.00),(0.45,1.00)],[(0.45,0.35),(0.85,0.65)]],
        [[(0.40,0.00),(0.40,1.00)],[(0.40,0.25),(0.80,0.50)]]]},
    {"id": 15, "name": "yr", "latin": "Y", "variants": [
        [[(0.50,0.50),(0.50,1.00)],[(0.15,0.10),(0.50,0.50)],[(0.85,0.10),(0.50,0.50)]],
        [[(0.50,0.40),(0.50,1.00)],[(0.20,0.05),(0.50,0.40)],[(0.80,0.05),(0.50,0.40)]]]},
]

SEPARATOR_DEF = {"id": 16, "name": "separator", "types": ["colon", "cross", "x_mark", "single_dot"]}
CLASS_NAMES   = [r["name"] for r in RUNES] + [SEPARATOR_DEF["name"]]

def stone_texture(w, h):
    base = np.random.randint(120, 195, (h, w)).astype(np.float32)
    coarse = np.random.randn(h//6+1, w//6+1).astype(np.float32) * 22
    coarse_up = np.array(Image.fromarray(np.clip(coarse+160,0,255).astype(np.uint8)).resize((w,h), Image.BILINEAR), dtype=np.float32)
    base = base*0.6 + coarse_up*0.4 + np.random.randn(h,w).astype(np.float32)*7
    base = np.clip(base, 70, 225)
    r = np.clip(base + random.randint(-12, 8), 0, 255).astype(np.uint8)
    g = np.clip(base + random.randint(-8, 4),  0, 255).astype(np.uint8)
    b = np.clip(base + random.randint(-18,-4), 0, 255).astype(np.uint8)
    img = Image.fromarray(np.stack([r,g,b], axis=2))
    img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.8, 1.8)))
    draw = ImageDraw.Draw(img)
    for _ in range(random.randint(1, 4)):
        x0, y0 = random.randint(0, w), random.randint(0, h)
        x1, y1 = x0 + random.randint(-w//3, w//3), y0 + random.randint(-h//3, h//3)
        c = random.randint(80, 120)
        draw.line([(x0,y0),(x1,y1)], fill=(c, c-5, c-10), width=1)
    return img

def draw_rune(draw, rune_def, cx, cy, size, angle_deg, line_w, color):
    ca, sa = math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))
    def T(nx, ny):
        lx, ly = (nx-0.5)*size, (ny-0.5)*size
        return (cx + lx*ca - ly*sa, cy + lx*sa + ly*ca)
    strokes = random.choice(rune_def["variants"])
    for stroke in strokes:
        pts = [T(p[0], p[1]) for p in stroke]
        for i in range(len(pts)-1):
            draw.line([pts[i], pts[i+1]], fill=color, width=line_w)
            r = max(1, line_w // 2)
            for pt in [pts[i], pts[i+1]]:
                draw.ellipse([pt[0]-r, pt[1]-r, pt[0]+r, pt[1]+r], fill=color)

def draw_separator(draw, cx, cy, size, angle_deg, line_w, color, sep_type=None):
    if sep_type is None:
        sep_type = random.choice(SEPARATOR_DEF["types"])
    ca, sa = math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))
    def T(lx, ly):
        return (cx + lx*ca - ly*sa, cy + lx*sa + ly*ca)
    dot_r = max(2, line_w)
    if sep_type == "colon":
        p1, p2 = T(0, -size*0.22), T(0, size*0.22)
        draw.ellipse([p1[0]-dot_r, p1[1]-dot_r, p1[0]+dot_r, p1[1]+dot_r], fill=color)
        draw.ellipse([p2[0]-dot_r, p2[1]-dot_r, p2[0]+dot_r, p2[1]+dot_r], fill=color)
    elif sep_type == "single_dot":
        draw.ellipse([cx-dot_r, cy-dot_r, cx+dot_r, cy+dot_r], fill=color)
    elif sep_type == "cross":
        s = size * 0.24
        draw.line([T(0,-s), T(0,s)], fill=color, width=line_w)
        draw.line([T(-s,0), T(s,0)], fill=color, width=line_w)
    elif sep_type == "x_mark":
        s = size * 0.20
        draw.line([T(-s,-s), T(s,s)], fill=color, width=line_w)
        draw.line([T(-s,s), T(s,-s)], fill=color, width=line_w)

def apply_aug(img):
    img = ImageEnhance.Brightness(img).enhance(random.uniform(0.75, 1.25))
    img = ImageEnhance.Contrast(img).enhance(random.uniform(0.80, 1.20))
    if random.random() < 0.30:
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.3, 0.9)))
    if random.random() < 0.45:
        arr = np.array(img).astype(np.int16)
        arr = np.clip(arr + np.random.randint(-10, 10, arr.shape, dtype=np.int16), 0, 255).astype(np.uint8)
        img = Image.fromarray(arr)
    return img

def generate_stone(fixed_class_id=None, img_size=IMG_SIZE):
    img = stone_texture(img_size, img_size)
    draw = ImageDraw.Draw(img)
    labels = []
    cx = img_size // 2 + random.randint(-25, 25)
    cy = img_size // 2 + random.randint(-25, 25)
    shape_type = random.choice(["circle", "oval_vertical", "oval_horizontal", "arch"])
    band_w = random.randint(52, 75)
    half_bw = band_w / 2

    if shape_type == "circle":
        rx = ry = random.randint(img_size//3 - 20, img_size//2 - 50)
        theta_start, theta_end = 0.0, 2*math.pi
    elif shape_type == "oval_vertical":
        rx = random.randint(img_size//4 + 10, img_size//3 - 10)
        ry = random.randint(img_size//3 + 10, img_size//2 - 40)
        theta_start, theta_end = 0.0, 2*math.pi
    elif shape_type == "oval_horizontal":
        rx = random.randint(img_size//3 + 10, img_size//2 - 40)
        ry = random.randint(img_size//4 + 10, img_size//3 - 10)
        theta_start, theta_end = 0.0, 2*math.pi
    else:
        rx = ry = random.randint(img_size//3 - 15, img_size//2 - 45)
        theta_start, theta_end = random.uniform(0.15*math.pi, 0.25*math.pi), random.uniform(1.75*math.pi, 1.85*math.pi)

    thetas = np.linspace(theta_start, theta_end, 160)
    inner_pts, outer_pts = [], []
    for th in thetas:
        px = cx + rx * math.cos(th)
        py = cy + ry * math.sin(th)
        dx, dy = -rx * math.sin(th), ry * math.cos(th)
        ln = math.sqrt(dx**2 + dy**2) + 1e-9
        nx, ny = dy/ln, -dx/ln
        outer_pts.append((px + nx*half_bw, py + ny*half_bw))
        inner_pts.append((px - nx*half_bw, py - ny*half_bw))

    dark = random.randint(28, 60)
    c_main = (dark, dark-4, dark-8)
    c_shad = (max(0, dark-20), max(0, dark-24), max(0, dark-28))
    lw_band = random.randint(2, 4)
    lw_rune = random.randint(3, 5)

    for pts in [outer_pts, inner_pts]:
        shd = [(p[0]+1, p[1]+1) for p in pts]
        draw.line(shd, fill=c_shad, width=lw_band)
        draw.line(pts, fill=c_main, width=lw_band)

    if shape_type != "arch":
        draw.line([outer_pts[-1], outer_pts[0]], fill=c_main, width=lw_band)
        draw.line([inner_pts[-1], inner_pts[0]], fill=c_main, width=lw_band)

    r_size = band_w * random.uniform(0.85, 0.98)
    approx_perimeter = math.pi * (rx + ry) * ((theta_end - theta_start)/(2*math.pi))
    spacing = r_size * random.uniform(1.22, 1.45)
    n_elements = max(3, int(approx_perimeter / spacing))
    elem_thetas = np.linspace(theta_start + 0.08, theta_end - 0.08, n_elements)
    point_outward = random.choice([True, False])
    rune_count_since_sep = 0

    for th in elem_thetas:
        px = cx + rx * math.cos(th)
        py = cy + ry * math.sin(th)
        dx, dy = -rx * math.sin(th), ry * math.cos(th)
        tangent_deg = math.degrees(math.atan2(dy, dx))
        rune_ang = tangent_deg + 90 if point_outward else tangent_deg - 90

        if not (r_size*0.6 < px < img_size - r_size*0.6 and r_size*0.6 < py < img_size - r_size*0.6):
            continue

        if fixed_class_id == 16:
            draw_separator(draw, px+1, py+1, r_size, rune_ang, lw_rune, c_shad)
            draw_separator(draw, px,   py,   r_size, rune_ang, lw_rune, c_main)
            bw = bh = (r_size * 0.65) / img_size
            labels.append(f"16 {px/img_size:.6f} {py/img_size:.6f} {bw:.6f} {bh:.6f}")
            continue

        is_sep = (fixed_class_id is None) and (rune_count_since_sep >= random.randint(3, 6))
        if is_sep:
            draw_separator(draw, px+1, py+1, r_size, rune_ang, lw_rune, c_shad)
            draw_separator(draw, px,   py,   r_size, rune_ang, lw_rune, c_main)
            bw = bh = (r_size * 0.65) / img_size
            labels.append(f"16 {px/img_size:.6f} {py/img_size:.6f} {bw:.6f} {bh:.6f}")
            rune_count_since_sep = 0
        else:
            rune = RUNES[fixed_class_id] if fixed_class_id is not None else random.choice(RUNES)
            draw_rune(draw, rune, px+1.5, py+1.5, r_size, rune_ang, lw_rune, c_shad)
            draw_rune(draw, rune, px,     py,     r_size, rune_ang, lw_rune, c_main)
            mg = 0.12
            bw = bh = (r_size * (1 + 2*mg)) / img_size
            labels.append(f"{rune['id']} {px/img_size:.6f} {py/img_size:.6f} {bw:.6f} {bh:.6f}")
            rune_count_since_sep += 1

    return apply_aug(img), labels
""")

# ==============================================================================
# Cell 5: Generate Directly to Google Drive (with Cache Check)
# ==============================================================================
add_md("""### 3.1 Synthesis Execution with Smart Persistence Check
If the dataset was already generated in a previous session, it instantly detects it and avoids redundant synthesis!
""")

add_code("""dirs = {
    "train_img": DATASET_DIR / "images" / "train",
    "val_img":   DATASET_DIR / "images" / "val",
    "train_lbl": DATASET_DIR / "labels" / "train",
    "val_lbl":   DATASET_DIR / "labels" / "val"
}
for d in dirs.values():
    d.mkdir(parents=True, exist_ok=True)

data_yaml_path = DATASET_DIR / "data.yaml"
with open(data_yaml_path, "w") as f:
    yaml.dump({
        "path": str(DATASET_DIR.resolve()),
        "train": "images/train",
        "val": "images/val",
        "nc": len(CLASS_NAMES),
        "names": CLASS_NAMES
    }, f, default_flow_style=False)

existing_train = len(list(dirs["train_img"].glob("*.jpg")))

if existing_train >= 3000:
    print(f"✓ Found existing dataset in Google Drive with {existing_train} train images!")
    print("  Skipping synthesis step to save time.")
else:
    print(">>> Generating new synthetic dataset directly to Google Drive...")
    counter = 0
    val_step = int(1 / (1 - TRAIN_SPLIT))

    for cid in range(len(CLASS_NAMES)):
        for i in range(SAMPLES_PER_RUNE):
            img, labels = generate_stone(fixed_class_id=cid)
            is_train = (i % val_step != 0)
            si = dirs["train_img"] if is_train else dirs["val_img"]
            sl = dirs["train_lbl"] if is_train else dirs["val_lbl"]
            name = f"stone_{counter:06d}"
            img.save(si / f"{name}.jpg", quality=92)
            with open(sl / f"{name}.txt", "w") as lf:
                lf.write("\\n".join(labels))
            counter += 1

    for i in range(SCENE_SAMPLES):
        img, labels = generate_stone(fixed_class_id=None)
        is_train = (i % val_step != 0)
        si = dirs["train_img"] if is_train else dirs["val_img"]
        sl = dirs["train_lbl"] if is_train else dirs["val_lbl"]
        name = f"stone_{counter:06d}"
        img.save(si / f"{name}.jpg", quality=92)
        with open(sl / f"{name}.txt", "w") as lf:
            lf.write("\\n".join(labels))
        counter += 1

    print("✓ Dataset generated and securely stored in Google Drive!")

train_count = len(list(dirs["train_img"].glob("*.jpg")))
val_count   = len(list(dirs["val_img"].glob("*.jpg")))
print(f"  Training Set   : {train_count} images")
print(f"  Validation Set : {val_count} images")
print(f"  Total Samples  : {train_count + val_count} images")
""")

# ==============================================================================
# Cell 6: Visual Sanity Check
# ==============================================================================
add_md("""### 3.2 Visual Sanity Check
Inspect 4 random synthesized stones directly from Google Drive with their ground truth boxes.
""")

add_code("""def plot_sample_with_boxes(img_path, lbl_path):
    img = cv2.imread(str(img_path))
    h, w = img.shape[:2]
    if lbl_path.exists():
        with open(lbl_path) as f:
            for line in f.readlines():
                parts = line.strip().split()
                if len(parts) == 5:
                    cid = int(parts[0])
                    bx, by, bw, bh = map(float, parts[1:])
                    x1 = int((bx - bw/2) * w)
                    y1 = int((by - bh/2) * h)
                    x2 = int((bx + bw/2) * w)
                    y2 = int((by + bh/2) * h)
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cname = CLASS_NAMES[cid]
                    cv2.putText(img, cname, (x1, max(15, y1 - 4)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

samples = list(dirs["train_img"].glob("*.jpg"))[-4:]
plt.figure(figsize=(16, 16))
for i, s_path in enumerate(samples):
    l_path = dirs["train_lbl"] / f"{s_path.stem}.txt"
    rendered = plot_sample_with_boxes(s_path, l_path)
    plt.subplot(2, 2, i + 1)
    plt.imshow(rendered)
    plt.axis("off")
    plt.title(f"Sample: {s_path.name}")
plt.tight_layout()
plt.show()
""")

# ==============================================================================
# Cell 7: Training with Drive Checkpointing & Resume
# ==============================================================================
add_md("""## 4. YOLO Training with Zero Data Loss (Direct Drive Checkpoints)
All model checkpoints (`best.pt`, `last.pt`) are written **directly into your Google Drive**.
If Colab disconnects, simply re-run this cell and it will automatically continue from the last checkpoint!
""")

add_code('''from ultralytics.nn.tasks import torch_safe_load

EXPERIMENT_NAME = "viking_yolo_run"
checkpoint_dir  = RUNS_DIR / EXPERIMENT_NAME / "weights"
last_checkpoint = checkpoint_dir / "last.pt"

# Check for existing checkpoint
if last_checkpoint.exists():
    try:
        ckpt_data, _ = torch_safe_load(str(last_checkpoint))
    except Exception:
        ckpt_data = torch.load(str(last_checkpoint), map_location="cpu", weights_only=False)
        
    stopped_epoch = ckpt_data.get("epoch", -1) + 1
    total_target_epochs = ckpt_data.get("train_args", {}).get("epochs", 50)
    
    print("=" * 60)
    print(f"🔄 Found previous checkpoint in Google Drive!")
    print(f"📍 Training stopped at Epoch: {stopped_epoch} / {total_target_epochs}")
    print("=" * 60)
    
    if stopped_epoch < total_target_epochs:
        print(f"▶️ Seamlessly resuming training from Epoch {stopped_epoch} to {total_target_epochs}...")
        model = YOLO(str(last_checkpoint))
        # When resuming in YOLO, only pass resume=True so it reads exact state & resumes the epoch counter
        results = model.train(resume=True)
    else:
        print(f"✅ Training already completed for all {total_target_epochs} Epochs!")
        model = YOLO(str(checkpoint_dir / "best.pt"))
else:
    print("=" * 60)
    print("🚀 Initializing new training session from pre-trained weights...")
    print("=" * 60)
    model = YOLO("yolov8m.pt")
    
    results = model.train(
        data=str(data_yaml_path),
        epochs=50,
        imgsz=640,
        batch=16,
        device=0,
        patience=15,
        save=True,
        project=str(RUNS_DIR),
        name=EXPERIMENT_NAME,
        exist_ok=True,
        fliplr=0.0,      # STRICTLY DISABLED: protects directional rune semantics
        flipud=0.0,
        degrees=25.0,
        scale=0.35,
        mosaic=1.0,
        mixup=0.15,
        optimizer="AdamW",
        lr0=0.0015,
        weight_decay=0.0005,
        verbose=True
    )

print(f"\\n✓ Model weights are safe at:")
print(f"  {checkpoint_dir / 'best.pt'}")
''')

# ==============================================================================
# Cell 8: Validation & Quantitative Metrics
# ==============================================================================
add_md("""## 5. Model Evaluation & Quantitative Metrics
Review metrics directly from the Google Drive experiment directory.
""")

add_code("""best_model_path = RUNS_DIR / EXPERIMENT_NAME / "weights" / "best.pt"
eval_model = YOLO(str(best_model_path))
metrics = eval_model.val(data=str(data_yaml_path))

print("\\n--- Quantitative Metrics ---")
print(f"mAP@50    : {metrics.box.map50:.4f}")
print(f"mAP@50-95 : {metrics.box.map:.4f}")

# Plot and display saved curves from Google Drive
eval_plots = list((RUNS_DIR / EXPERIMENT_NAME).glob("*.png"))
for p in eval_plots:
    if any(k in p.name for k in ["results", "confusion_matrix", "PR_curve"]):
        plt.figure(figsize=(10, 8))
        im = Image.open(p)
        plt.imshow(im)
        plt.axis("off")
        plt.title(p.stem)
        plt.show()
""")

# ==============================================================================
# Cell 9: Unpack Real Stone Images
# ==============================================================================
add_md("""## 6. Upload Real Stone Monuments
Copy your `images.zip` archive to Google Drive or directly upload it here.
""")

add_code("""# If images.zip is uploaded in Colab root (/content/images.zip):
if Path("/content/images.zip").exists():
    !unzip -q -o /content/images.zip -d "{REAL_DIR}"
    print(f"✓ Extracted images into Google Drive: {REAL_DIR}")

# Or list images already in Google Drive
real_images = list(REAL_DIR.glob("*.*"))
valid_exts  = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]
real_images = [img for img in real_images if img.suffix.lower() in valid_exts]

print(f"Found {len(real_images)} real stone images ready in Google Drive.")
""")

# ==============================================================================
# Cell 10: Auto-Annotation Engine (Pseudo-Labeling)
# ==============================================================================
add_md("""## 7. Semi-Supervised Auto-Annotation Engine
Infers bounding boxes on all real stones and outputs standard YOLO `.txt` labels directly into `MyDrive/Viking_Rune_Project/auto_labeled_stones/`.
""")

add_code("""CONFIDENCE_THRESHOLD = 0.35

print(f"Running auto-annotation on {len(real_images)} real monuments...")

for img_path in real_images:
    results = eval_model.predict(
        source=str(img_path),
        conf=CONFIDENCE_THRESHOLD,
        imgsz=640,
        device=0,
        verbose=False
    )[0]

    h, w = results.orig_shape
    label_lines = []

    for box in results.boxes:
        cid = int(box.cls[0].item())
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        bx = ((x1 + x2) / 2) / w
        by = ((y1 + y2) / 2) / h
        bw = (x2 - x1) / w
        bh = (y2 - y1) / h
        label_lines.append(f"{cid} {bx:.6f} {by:.6f} {bw:.6f} {bh:.6f}")

    out_lbl_path = LABELS_DIR / f"{img_path.stem}.txt"
    with open(out_lbl_path, "w") as f:
        f.write("\\n".join(label_lines))

print(f"✓ All pseudo-labels generated and saved to Google Drive!")
print(f"  Location: {LABELS_DIR}")
""")

# ==============================================================================
# Cell 11: Transliteration
# ==============================================================================
add_md("""## 8. Linguistic Transliteration & Stone Inscription Reading
Demonstration of translating detected runic glyphs into transcribed Latin phonetic strings.
""")

add_code("""RUNES_TO_CHAR = {
    0: "f",  1: "u",  2: "th", 3: "a",
    4: "r",  5: "k",  6: "h",  7: "n",
    8: "i",  9: "a",  10: "s", 11: "t",
    12: "b", 13: "m", 14: "l", 15: "y",
    16: " : "  # Separator
}

def read_stone_inscription(image_path, model, conf=0.35):
    res = model.predict(source=str(image_path), conf=conf, imgsz=640, device=0, verbose=False)[0]
    detections = []

    for box in res.boxes:
        cid = int(box.cls[0].item())
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        detections.append({"cid": cid, "cx": cx, "cy": cy, "char": RUNES_TO_CHAR[cid]})

    detections = sorted(detections, key=lambda d: (d["cy"], d["cx"]))
    text = "".join([d["char"] for d in detections])
    return text, res.plot()

if real_images:
    sample_img = real_images[0]
    inscription, vis_img = read_stone_inscription(sample_img, eval_model)

    plt.figure(figsize=(12, 12))
    plt.imshow(cv2.cvtColor(vis_img, cv2.COLOR_BGR2RGB))
    plt.axis("off")
    plt.title(f"Reading: {inscription}", fontsize=15, color="darkred")
    plt.show()
    print("Transcription Output:", inscription)
""")

# ==============================================================================
# Cell 12: Summary
# ==============================================================================
add_md("""## 9. Summary & Next Steps
Your entire pipeline is preserved on Google Drive:
- Checkpoints: `MyDrive/Viking_Rune_Project/training_runs/viking_yolo_run/weights/best.pt`
- Real Stone Labels: `MyDrive/Viking_Rune_Project/auto_labeled_stones/`

You can now:
1. Open any annotation tool (Label Studio, Roboflow, LabelImg) pointing to `auto_labeled_stones` to do rapid 5-minute manual verification.
2. Fine-tune this model directly on the verified real stones!
""")

notebook = {
    "cells": cells,
    "metadata": {
        "accelerator": "GPU",
        "colab": {
            "name": "Viking_Rune_YOLO_Colab.ipynb",
            "provenance": []
        },
        "language_info": {
            "name": "python"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 0
}

target_path = r"c:\Users\ZBook 4K\Desktop\Lab 5\Viking_Rune_YOLO_Colab.ipynb"
with open(target_path, "w", encoding="utf-8") as f:
    json.dump(notebook, f, ensure_ascii=False, indent=2)

print(f"Successfully updated notebook with Google Drive integration: {target_path}")
