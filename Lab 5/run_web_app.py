import os
import sys
import io
import time
import base64
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, request, jsonify, send_file, render_template_string

# Ensure UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "LASTMODEL" / "best(1).pt"
if not MODEL_PATH.exists():
    MODEL_PATH = BASE_DIR / "best.pt"

import torch
num_threads = os.cpu_count() or 4
torch.set_num_threads(num_threads)
device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"Loading Full-Precision Original YOLO Model from: {MODEL_PATH} on {device} ({num_threads} threads)...")
from ultralytics import YOLO
model = YOLO(str(MODEL_PATH))
print(f"Full-Precision YOLO Model loaded successfully on {device} (Classes: {len(model.names)})!")

RUNES_INFO = {
    0:  {"rune": "ᚠ", "latin": "f",   "name": "fehu",      "meaning": "Wealth / Cattle"},
    1:  {"rune": "ᚢ", "latin": "u",   "name": "uruz",      "meaning": "Aurochs / Strength"},
    2:  {"rune": "ᚦ", "latin": "th",  "name": "thurisaz",  "meaning": "Giant / Thorn"},
    3:  {"rune": "ᚬ", "latin": "a",   "name": "ansuz",     "meaning": "God / Odin"},
    4:  {"rune": "ᚱ", "latin": "r",   "name": "raidho",    "meaning": "Ride / Journey"},
    5:  {"rune": "ᚴ", "latin": "k",   "name": "kaunan",    "meaning": "Ulcer / Torch"},
    6:  {"rune": "ᚼ", "latin": "h",   "name": "hagalaz",   "meaning": "Hail / Disruption"},
    7:  {"rune": "ᚾ", "latin": "n",   "name": "naudiz",    "meaning": "Need / Distress"},
    8:  {"rune": "ᛁ", "latin": "i",   "name": "isaz",      "meaning": "Ice / Stillness"},
    9:  {"rune": "ᛅ", "latin": "a",   "name": "ar_jera",   "meaning": "Year / Harvest"},
    10: {"rune": "ᛋ", "latin": "s",   "name": "sowilo",    "meaning": "Sun / Victory"},
    11: {"rune": "ᛏ", "latin": "t",   "name": "tiwaz",     "meaning": "Tyr / Justice"},
    12: {"rune": "ᛒ", "latin": "b",   "name": "berkanan",  "meaning": "Birch / Rebirth"},
    13: {"rune": "ᛉ", "latin": "m",   "name": "mannaz",    "meaning": "Human / Man"},
    14: {"rune": "ᛚ", "latin": "l",   "name": "laguz",     "meaning": "Water / Flow"},
    15: {"rune": "ᛦ", "latin": "R",   "name": "yr",        "meaning": "Yew bow / Tree"},
    16: {"rune": ":", "latin": ":",   "name": "separator", "meaning": "Word Divider"},
}

FONT_PATH = r"C:\Windows\Fonts\seguihis.ttf"
try:
    font_rune = ImageFont.truetype(FONT_PATH, 20)
except Exception:
    font_rune = ImageFont.load_default()

def calculate_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    if interArea == 0:
        return 0.0

    boxAArea = max(1e-5, (boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    boxBArea = max(1e-5, (boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))

    return interArea / float(boxAArea + boxBArea - interArea)

def is_point_inside(px, py, box):
    return (box[0] <= px <= box[2]) and (box[1] <= py <= box[3])

def mask_detected_regions(img, boxes):
    masked = img.copy()
    h, w = img.shape[:2]
    for box in boxes:
        x1, y1, x2, y2 = [int(v) for v in box]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w - 1, x2), min(h - 1, y2)
        if x2 > x1 and y2 > y1:
            pad = 6
            bx1, by1 = max(0, x1 - pad), max(0, y1 - pad)
            bx2, by2 = min(w, x2 + pad), min(h, y2 + pad)
            border_patch = img[by1:by2, bx1:bx2]
            median_col = np.median(border_patch.reshape(-1, 3), axis=0).astype(np.uint8)
            masked[y1:y2, x1:x2] = median_col
    return masked

def transform_box_to_original(box, angle, orig_w, orig_h):
    rx1, ry1, rx2, ry1_max = box[0], box[1], box[2], box[3]
    if angle == 0:
        return [rx1, ry1, rx2, ry1_max]
    elif angle == 180:
        ox1 = orig_w - 1 - rx2
        ox2 = orig_w - 1 - rx1
        oy1 = orig_h - 1 - ry1_max
        oy2 = orig_h - 1 - ry1
        return [min(ox1, ox2), min(oy1, oy2), max(ox1, ox2), max(oy1, oy2)]
    elif angle == 90:
        ox1 = ry1
        ox2 = ry1_max
        oy1 = orig_h - 1 - rx2
        oy2 = orig_h - 1 - rx1
        return [min(ox1, ox2), min(oy1, oy2), max(ox1, ox2), max(oy1, oy2)]
    elif angle == 270:
        ox1 = orig_w - 1 - ry1_max
        ox2 = orig_w - 1 - ry1
        oy1 = rx1
        oy2 = rx2
        return [min(ox1, ox2), min(oy1, oy2), max(ox1, ox2), max(oy1, oy2)]
    return box

def process_viking_image(cv_img, conf_thresh=0.18, imgsz=1024, enable_4way=True):
    t_start = time.time()
    orig_h, orig_w = cv_img.shape[:2]
    working_img = cv_img.copy()

    rotations = [(0, None, "0°")]
    if enable_4way:
        rotations.extend([
            (180, cv2.ROTATE_180, "180°"),
            (90, cv2.ROTATE_90_CLOCKWISE, "90°"),
            (270, cv2.ROTATE_90_COUNTERCLOCKWISE, "270°")
        ])

    all_accepted = []
    stats = {0: 0, 90: 0, 180: 0, 270: 0}

    for angle, cv_rot, _ in rotations:
        if all_accepted and angle != 0:
            prev_boxes = [d["box"] for d in all_accepted]
            masked_img = mask_detected_regions(working_img, prev_boxes)
        else:
            masked_img = working_img

        scan_img = cv2.rotate(masked_img, cv_rot) if cv_rot is not None else masked_img
        results = model.predict(source=scan_img, conf=conf_thresh, imgsz=imgsz, device=device, verbose=False)[0]
        boxes = results.boxes

        if boxes is not None and len(boxes) > 0:
            for b in boxes:
                cls_id = int(b.cls[0].item())
                conf = float(b.conf[0].item())
                r_box = b.xyxy[0].tolist()

                orig_box = transform_box_to_original(r_box, angle, orig_w, orig_h)
                cx = (orig_box[0] + orig_box[2]) / 2.0
                cy = (orig_box[1] + orig_box[3]) / 2.0

                overlap = False
                for accepted in all_accepted:
                    iou = calculate_iou(orig_box, accepted["box"])
                    if iou > 0.15 or is_point_inside(cx, cy, accepted["box"]):
                        overlap = True
                        break

                if overlap:
                    continue

                info = RUNES_INFO.get(cls_id, {"rune": "?", "latin": "?", "name": model.names.get(cls_id, "unknown"), "meaning": ""})
                all_accepted.append({
                    "id": len(all_accepted) + 1,
                    "cls_id": cls_id,
                    "name": info["name"],
                    "rune": info["rune"],
                    "latin": info["latin"],
                    "meaning": info.get("meaning", ""),
                    "conf": round(conf, 4),
                    "angle": angle,
                    "box": [round(x, 1) for x in orig_box],
                    "cx": round(cx, 1),
                    "cy": round(cy, 1)
                })
                stats[angle] += 1

    # Sort reading order: primary by Y ribbon, then by X
    all_accepted.sort(key=lambda d: (round(d["cy"] / 60), d["cx"]))
    for i, d in enumerate(all_accepted):
        d["reading_idx"] = i + 1

    runic_text = "".join([d["rune"] for d in all_accepted])
    latin_translit = "".join([d["latin"] for d in all_accepted])

    # Color map matching angles
    COLOR_MAP = {
        0:   (0, 230, 80),    # Vibrant Green (0°)
        180: (30, 180, 255),  # Sky Blue (180°)
        90:  (255, 140, 0),   # Bright Orange (90°)
        270: (230, 0, 230)    # Magenta (270°)
    }

    pil_img = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)

    for d in all_accepted:
        box = [int(v) for v in d["box"]]
        angle = d["angle"]
        color = COLOR_MAP.get(angle, (0, 230, 80))
        draw.rectangle(box, outline=color, width=2)

        # Only the rune symbol itself (بدون أرقام أو نصوص إضافية)
        label_text = str(d["rune"])
        bw = box[2] - box[0]
        bh = box[3] - box[1]
        bbox = draw.textbbox((0, 0), label_text, font=font_rune)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]

        pad_x = 4
        pad_y = 2

        # موضع الليبل حسب طلب المستخدم:
        # الزاوية 0° و 180°: إلى الأعلى
        # الزاوية 90° و 270°: إلى الجانب الأيمن
        if angle in (0, 180):
            tx = box[0] + (bw - tw) // 2
            ty = box[1] - th - pad_y * 2 - 2
            if ty < 0:
                ty = box[1] + 2
        else:
            # 90° و 270° إلى الجانب الأيمن
            tx = box[2] + 4
            ty = box[1] + (bh - th) // 2
            if tx + tw + pad_x > orig_w:
                tx = box[2] - tw - pad_x - 2

        # ضمان بقاء الليبل داخل أبعاد الصورة
        tx = max(pad_x, min(orig_w - tw - pad_x - 1, tx))
        ty = max(pad_y, min(orig_h - th - pad_y - 1, ty))

        draw.rectangle([tx - pad_x, ty - pad_y, tx + tw + pad_x, ty + th + pad_y], fill=(10, 14, 22), outline=color, width=1)
        draw.text((tx, ty), label_text, fill=(255, 255, 255), font=font_rune)

    buffer = io.BytesIO()
    pil_img.save(buffer, format="JPEG", quality=90)
    b64_img = base64.b64encode(buffer.getvalue()).decode("utf-8")
    t_elapsed = round(time.time() - t_start, 2)

    return {
        "success": True,
        "width": orig_w,
        "height": orig_h,
        "elapsed_seconds": t_elapsed,
        "total_runes": len(all_accepted),
        "stats": {
            "angle_0": stats[0],
            "angle_90": stats[90],
            "angle_180": stats[180],
            "angle_270": stats[270],
            "total": len(all_accepted)
        },
        "runic_text": runic_text,
        "transliteration": latin_translit,
        "detections": all_accepted,
        "annotated_image": f"data:image/jpeg;base64,{b64_img}"
    }

SAMPLES = [
    {"id": "aasum", "title": "Åsum Vikingstone (DR 347)", "desc": "Famous Skåne serpent inscription with 60+ runes", "path": BASE_DIR / "images" / "1.jpg"},
    {"id": "viggeby", "title": "Viggeby Stone (U 1165)", "desc": "Curved arch memorial inscription", "path": BASE_DIR / "images" / "181.jpg"},
    {"id": "glemminge", "title": "Glemminge Stone (DR 338)", "desc": "Vertical rib with inverted lettering", "path": BASE_DIR / "images" / "2.jpg"},
    {"id": "haellestad", "title": "Hällestad Monument (DR 295)", "desc": "Tóki warrior memorial pillar", "path": BASE_DIR / "images" / "3.jpg"},
    {"id": "stone_1", "title": "Viking Stone #1 (Museum Archive)", "desc": "High-contrast epigraphic specimen", "path": BASE_DIR / "imagesfintune" / "1.png"},
    {"id": "stone_10", "title": "Viking Stone #10 (Museum Archive)", "desc": "Weathered granite inscription", "path": BASE_DIR / "imagesfintune" / "10.png"},
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>منصة فحص وترجمة النقوش الفايكنج | Viking Epigraphy AI</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Outfit:wght@400;500;600;700&family=Noto+Sans+Runic&family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-dark: #0A0D14;
      --card-bg: rgba(18, 24, 38, 0.85);
      --card-border: rgba(255, 255, 255, 0.08);
      --gold: #F59E0B;
      --gold-glow: rgba(245, 158, 11, 0.35);
      --accent-0: #10B981;
      --accent-180: #0EA5E9;
      --accent-90: #F97316;
      --accent-270: #D946EF;
      --text-main: #F1F5F9;
      --text-muted: #94A3B8;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background-color: var(--bg-dark);
      background-image: 
        radial-gradient(circle at 15% 15%, rgba(245, 158, 11, 0.05) 0%, transparent 40%),
        radial-gradient(circle at 85% 85%, rgba(14, 165, 233, 0.05) 0%, transparent 40%),
        linear-gradient(180deg, #07090E 0%, #0D121D 100%);
      color: var(--text-main);
      font-family: 'Tajawal', 'Outfit', sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    header {
      background: rgba(10, 14, 23, 0.8);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--card-border);
      padding: 16px 32px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 50;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .brand-icon {
      width: 44px;
      height: 44px;
      background: linear-gradient(135deg, #F59E0B, #B45309);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'Noto Sans Runic', sans-serif;
      font-size: 26px;
      color: #000;
      font-weight: bold;
      box-shadow: 0 0 20px var(--gold-glow);
    }

    .brand-title {
      font-size: 20px;
      font-weight: 800;
      color: #FFF;
      letter-spacing: -0.5px;
    }

    .brand-subtitle {
      font-size: 12px;
      color: var(--gold);
      font-weight: 600;
    }

    .badges-row {
      display: flex;
      gap: 10px;
      align-items: center;
    }

    .status-badge {
      background: rgba(245, 158, 11, 0.12);
      border: 1px solid rgba(245, 158, 11, 0.3);
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 700;
      color: #FBBF24;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .spec-badge {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--card-border);
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 12px;
      color: var(--text-muted);
    }

    .main-container {
      max-width: 1400px;
      margin: 0 auto;
      padding: 28px 24px;
      width: 100%;
      display: grid;
      grid-template-columns: 380px 1fr;
      gap: 24px;
      flex: 1;
    }

    @media (max-width: 1080px) {
      .main-container { grid-template-columns: 1fr; }
    }

    .panel {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 18px;
      padding: 22px;
      backdrop-filter: blur(10px);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }

    .panel-title {
      font-size: 16px;
      font-weight: 700;
      color: #FFF;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 8px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      padding-bottom: 10px;
    }

    /* Upload Box */
    .upload-zone {
      border: 2px dashed rgba(245, 158, 11, 0.3);
      border-radius: 14px;
      padding: 32px 18px;
      text-align: center;
      cursor: pointer;
      background: rgba(245, 158, 11, 0.02);
      transition: all 0.25s ease;
      position: relative;
    }

    .upload-zone:hover, .upload-zone.dragover {
      border-color: var(--gold);
      background: rgba(245, 158, 11, 0.08);
      transform: translateY(-2px);
    }

    .upload-icon {
      font-size: 40px;
      color: var(--gold);
      margin-bottom: 10px;
    }

    .upload-text {
      font-size: 14px;
      font-weight: 600;
      color: #FFF;
      margin-bottom: 4px;
    }

    .upload-hint {
      font-size: 11px;
      color: var(--text-muted);
    }

    #fileInput { display: none; }

    /* Controls */
    .control-group {
      margin-top: 18px;
    }

    .control-label {
      display: flex;
      justify-content: space-between;
      font-size: 13px;
      font-weight: 600;
      margin-bottom: 8px;
      color: var(--text-main);
    }

    .range-slider {
      width: 100%;
      accent-color: var(--gold);
      height: 6px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 3px;
      cursor: pointer;
    }

    .toggle-card {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 12px 14px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: 14px;
    }

    .toggle-info h4 {
      font-size: 13px;
      font-weight: 700;
      color: #FFF;
    }

    .toggle-info p {
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 2px;
    }

    .switch {
      position: relative;
      display: inline-block;
      width: 48px;
      height: 26px;
    }

    .switch input { opacity: 0; width: 0; height: 0; }

    .slider {
      position: absolute;
      cursor: pointer;
      top: 0; left: 0; right: 0; bottom: 0;
      background-color: rgba(255, 255, 255, 0.15);
      transition: .3s;
      border-radius: 26px;
    }

    .slider:before {
      position: absolute;
      content: "";
      height: 20px;
      width: 20px;
      left: 3px;
      bottom: 3px;
      background-color: white;
      transition: .3s;
      border-radius: 50%;
    }

    input:checked + .slider { background-color: var(--gold); }
    input:checked + .slider:before { transform: translateX(22px); }

    .btn-scan {
      width: 100%;
      padding: 14px;
      background: linear-gradient(135deg, #F59E0B, #D97706);
      border: none;
      border-radius: 12px;
      color: #000;
      font-weight: 800;
      font-size: 15px;
      cursor: pointer;
      margin-top: 18px;
      transition: all 0.2s ease;
      box-shadow: 0 4px 20px var(--gold-glow);
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }

    .btn-scan:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 25px rgba(245, 158, 11, 0.5);
    }

    .btn-scan:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
    }

    /* Samples Grid */
    .samples-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
      margin-top: 12px;
    }

    .sample-item {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 8px;
      cursor: pointer;
      transition: all 0.2s ease;
      text-align: right;
    }

    .sample-item:hover, .sample-item.active {
      border-color: var(--gold);
      background: rgba(245, 158, 11, 0.08);
      transform: translateY(-1px);
    }

    .sample-name {
      font-size: 11px;
      font-weight: 700;
      color: #FFF;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .sample-desc {
      font-size: 9px;
      color: var(--text-muted);
      margin-top: 2px;
    }

    /* Results Column */
    .results-column {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    /* Stats HUD */
    .stats-hud {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 12px;
    }

    @media (max-width: 768px) {
      .stats-hud { grid-template-columns: repeat(2, 1fr); }
    }

    .stat-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 14px;
      text-align: center;
    }

    .stat-val {
      font-size: 26px;
      font-weight: 900;
      color: #FFF;
      font-family: 'Outfit', sans-serif;
    }

    .stat-label {
      font-size: 11px;
      font-weight: 600;
      color: var(--text-muted);
      margin-top: 4px;
    }

    .stat-card.total .stat-val { color: var(--gold); }
    .stat-card.a0 .stat-val { color: var(--accent-0); }
    .stat-card.a180 .stat-val { color: var(--accent-180); }
    .stat-card.a90 .stat-val { color: var(--accent-90); }
    .stat-card.a270 .stat-val { color: var(--accent-270); }

    /* Canvas / Image Preview */
    .canvas-container {
      background: #06080D;
      border: 1px solid var(--card-border);
      border-radius: 16px;
      overflow: hidden;
      min-height: 480px;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
    }

    .preview-img {
      max-width: 100%;
      max-height: 650px;
      object-fit: contain;
      display: block;
    }

    .empty-state {
      text-align: center;
      padding: 60px 20px;
      color: var(--text-muted);
    }

    .empty-icon {
      font-size: 50px;
      margin-bottom: 12px;
      opacity: 0.4;
    }

    /* Inscription Ribbon */
    .ribbon-panel {
      background: linear-gradient(135deg, rgba(245, 158, 11, 0.08), rgba(18, 24, 38, 0.9));
      border: 1px solid rgba(245, 158, 11, 0.25);
      border-radius: 14px;
      padding: 18px 22px;
    }

    .ribbon-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }

    .ribbon-title {
      font-size: 13px;
      font-weight: 700;
      color: var(--gold);
    }

    .btn-copy {
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid var(--card-border);
      color: #FFF;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 11px;
      cursor: pointer;
      font-weight: 600;
      transition: all 0.2s;
    }

    .btn-copy:hover { background: rgba(255, 255, 255, 0.16); }

    .runic-text-display {
      font-family: 'Noto Sans Runic', sans-serif;
      font-size: 32px;
      letter-spacing: 4px;
      color: #FFF;
      line-height: 1.5;
      word-break: break-all;
      text-shadow: 0 0 15px rgba(245, 158, 11, 0.3);
      direction: ltr;
      text-align: left;
    }

    .latin-text-display {
      font-family: 'Cinzel', serif;
      font-size: 18px;
      letter-spacing: 2px;
      color: #94A3B8;
      margin-top: 6px;
      direction: ltr;
      text-align: left;
    }

    /* Vikings Grid */
    .runes-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
      gap: 10px;
      max-height: 380px;
      overflow-y: auto;
      padding-left: 4px;
    }

    .rune-badge {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 10px;
      text-align: center;
      transition: all 0.2s;
      cursor: pointer;
    }

    .rune-badge:hover {
      border-color: var(--gold);
      background: rgba(245, 158, 11, 0.08);
      transform: translateY(-2px);
    }

    .rune-glyph {
      font-family: 'Noto Sans Runic', sans-serif;
      font-size: 26px;
      color: #FFF;
      font-weight: bold;
    }

    .rune-meta {
      font-size: 11px;
      font-weight: 700;
      color: var(--gold);
      margin-top: 2px;
    }

    .rune-trans {
      font-size: 10px;
      color: var(--text-muted);
    }

    .rune-tag {
      font-size: 9px;
      padding: 2px 6px;
      border-radius: 4px;
      margin-top: 4px;
      display: inline-block;
      font-weight: 700;
    }

    .tag-0 { background: rgba(16, 185, 129, 0.2); color: var(--accent-0); }
    .tag-180 { background: rgba(14, 165, 233, 0.2); color: var(--accent-180); }
    .tag-90 { background: rgba(249, 115, 22, 0.2); color: var(--accent-90); }
    .tag-270 { background: rgba(217, 70, 239, 0.2); color: var(--accent-270); }

    /* Loading Overlay */
    .loading-overlay {
      position: absolute;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(10, 14, 23, 0.85);
      backdrop-filter: blur(8px);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 16px;
      z-index: 20;
      display: none;
    }

    .spinner {
      width: 50px;
      height: 50px;
      border: 4px solid rgba(245, 158, 11, 0.2);
      border-top-color: var(--gold);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }

    @keyframes spin { to { transform: rotate(360deg); } }

    .loading-text {
      font-size: 14px;
      font-weight: 700;
      color: #FFF;
    }
  </style>
</head>
<body>

  <header>
    <div class="brand">
      <div class="brand-icon">᛭</div>
      <div>
        <div class="brand-title">Viking Epigraphy AI | منصة النقوش الفايكنج</div>
        <div class="brand-subtitle">خوارزمية المسح التدويري الرباعي الأصلية (4-Way TTA 360°)</div>
      </div>
    </div>
    <div class="badges-row">
      <div class="status-badge">⚡ الموديل الأصلي الكامل (Float32 / 1024px)</div>
      <div class="spec-badge">Intel Core i7 Engine</div>
    </div>
  </header>

  <main class="main-container">
    <!-- Left Sidebar: Controls & Samples -->
    <div class="panel">
      <div class="panel-title">
        <span>📸</span>
        <span>اختيار حجر الفايكنج</span>
      </div>

      <div class="upload-zone" id="uploadZone" onclick="document.getElementById('fileInput').click()">
        <div class="upload-icon">🏛️</div>
        <div class="upload-text">اسحب صورة الحجر هنا أو انقر للاختيار</div>
        <div class="upload-hint">يدعم صور عالية الدقة JPG, PNG (الأصلية بدون ضغط)</div>
        <input type="file" id="fileInput" accept="image/*" onchange="handleFileSelect(event)">
      </div>

      <div class="panel-title" style="margin-top: 22px;">
        <span>📜</span>
        <span>عينات الأحجار الشهيرة للاختبار الفوري</span>
      </div>

      <div class="samples-grid">
        {% for s in samples %}
        <div class="sample-item" onclick="loadSample('{{ s.id }}', this)">
          <div class="sample-name">{{ s.title }}</div>
          <div class="sample-desc">{{ s.desc }}</div>
        </div>
        {% endfor %}
      </div>

      <div class="panel-title" style="margin-top: 22px;">
        <span>⚙️</span>
        <span>إعدادات الذكاء الاصطناعي</span>
      </div>

      <div class="control-group">
        <div class="control-label">
          <span>عتبة الثقة (Confidence Threshold):</span>
          <span id="confVal" style="color: var(--gold); font-weight: bold;">18%</span>
        </div>
        <input type="range" class="range-slider" id="confSlider" min="5" max="80" value="18" oninput="updateConf(this.value)">
      </div>

      <div class="toggle-card">
        <div class="toggle-info">
          <h4>المسح الرباعي التدويري (4-Way TTA)</h4>
          <p>فحص في 4 زوايا (0° + 90° + 180° + 270°) لاكتشاف الحروف المقلوبة والمائلة</p>
        </div>
        <label class="switch">
          <input type="checkbox" id="ttaSwitch" checked>
          <span class="slider"></span>
        </label>
      </div>

      <button class="btn-scan" id="btnScan" onclick="runPrediction()">
        <span>⚡ بدء الفحص العميق واكتشاف الرموز</span>
      </button>
    </div>

    <!-- Right Column: Results & Interactive Canvas -->
    <div class="results-column">
      <!-- HUD Stats -->
      <div class="stats-hud">
        <div class="stat-card total">
          <div class="stat-val" id="statTotal">0</div>
          <div class="stat-label">إجمالي الرموز المكتشفة</div>
        </div>
        <div class="stat-card a0">
          <div class="stat-val" id="stat0">0</div>
          <div class="stat-label">أفقي طبيعي (0°) 🟢</div>
        </div>
        <div class="stat-card a180">
          <div class="stat-val" id="stat180">0</div>
          <div class="stat-label">مقلوب رأساً (180°) 🔵</div>
        </div>
        <div class="stat-card a90">
          <div class="stat-val" id="stat90">0</div>
          <div class="stat-label">عمودي يمين (90°) 🟠</div>
        </div>
        <div class="stat-card a270">
          <div class="stat-val" id="stat270">0</div>
          <div class="stat-label">عمودي يسار (270°) 🟣</div>
        </div>
      </div>

      <!-- Main Canvas Container -->
      <div class="canvas-container" id="canvasContainer">
        <div class="loading-overlay" id="loadingOverlay">
          <div class="spinner"></div>
          <div class="loading-text" id="loadingStatus">جاري فحص الحجر بالذكاء الاصطناعي (المسح الرباعي 0° + 90° + 180° + 270°)...</div>
        </div>

        <div class="empty-state" id="emptyState">
          <div class="empty-icon">🛡️</div>
          <h3>اختر صورة حجر فايكنج أثري أو انقر على إحدى العينات لبدء الفحص</h3>
          <p style="font-size: 13px; margin-top: 6px;">سيتم رسم مربعات التحديد بألوان تعبر عن زاوية كل حرف مع ترقيم اتجاه القراءة</p>
        </div>

        <img id="resultImage" class="preview-img" style="display: none;" alt="Result">
      </div>

      <!-- Inscription Ribbon -->
      <div class="ribbon-panel" id="ribbonPanel" style="display: none;">
        <div class="ribbon-header">
          <div class="ribbon-title">᛭ النص الروني المستخرج وترجمته اللاتينية (مرتب باتجاه القراءة)</div>
          <button class="btn-copy" onclick="copyText()">📋 نسخ النص</button>
        </div>
        <div class="runic-text-display" id="runicDisplay"></div>
        <div class="latin-text-display" id="latinDisplay"></div>
      </div>

      <!-- Vikings Grid -->
      <div class="panel" id="runesPanel" style="display: none;">
        <div class="panel-title">
          <span>🔍</span>
          <span>قاموس الرموز المكتشفة في هذا الحجر</span>
        </div>
        <div class="runes-grid" id="runesGrid"></div>
      </div>
    </div>
  </main>

  <script>
    let currentImageBase64 = null;

    function updateConf(val) {
      document.getElementById('confVal').innerText = val + '%';
    }

    function handleFileSelect(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
          currentImageBase64 = e.target.result;
          showPreview(currentImageBase64);
          document.querySelectorAll('.sample-item').forEach(el => el.classList.remove('active'));
          runPrediction();
        };
        reader.readAsDataURL(file);
      }
    }

    // Drag & Drop
    const uploadZone = document.getElementById('uploadZone');
    uploadZone.addEventListener('dragover', (e) => { e.preventDefault(); uploadZone.classList.add('dragover'); });
    uploadZone.addEventListener('dragleave', () => { uploadZone.classList.remove('dragover'); });
    uploadZone.addEventListener('drop', (e) => {
      e.preventDefault();
      uploadZone.classList.remove('dragover');
      if (e.dataTransfer.files.length) {
        document.getElementById('fileInput').files = e.dataTransfer.files;
        handleFileSelect({ target: { files: e.dataTransfer.files } });
      }
    });

    async function loadSample(sampleId, el) {
      document.querySelectorAll('.sample-item').forEach(i => i.classList.remove('active'));
      if (el) el.classList.add('active');

      document.getElementById('emptyState').style.display = 'none';
      document.getElementById('loadingOverlay').style.display = 'flex';
      document.getElementById('loadingStatus').innerText = 'جاري جلب صورة العينة وفحصها...';

      try {
        const resp = await fetch('/sample/' + sampleId);
        const data = await resp.json();
        currentImageBase64 = data.image_base64;
        showPreview(currentImageBase64);
        runPrediction();
      } catch (err) {
        alert('خطأ في تحميل العينة: ' + err);
        document.getElementById('loadingOverlay').style.display = 'none';
      }
    }

    function showPreview(b64) {
      document.getElementById('emptyState').style.display = 'none';
      const img = document.getElementById('resultImage');
      img.src = b64;
      img.style.display = 'block';
    }

    async function runPrediction() {
      if (!currentImageBase64) {
        alert('يرجى اختيار صورة أولاً أو الضغط على إحدى العينات!');
        return;
      }

      const conf = parseFloat(document.getElementById('confSlider').value) / 100.0;
      const enable4way = document.getElementById('ttaSwitch').checked;

      document.getElementById('loadingOverlay').style.display = 'flex';
      document.getElementById('loadingStatus').innerText = enable4way
        ? 'جاري الفحص الدقيق بالمعالج الأصلي (المسح الرباعي 0° + 90° + 180° + 270°)...'
        : 'جاري الفحص بالزاوية العادية 0°...';

      document.getElementById('btnScan').disabled = true;

      try {
        const resp = await fetch('/predict_web', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            image_base64: currentImageBase64,
            conf: conf,
            enable_4way: enable4way
          })
        });

        const data = await resp.json();
        if (data.success) {
          renderResults(data);
        } else {
          alert('خطأ أثناء الفحص: ' + (data.error || 'فشل'));
        }
      } catch (err) {
        alert('تعذر الاتصال بالذكاء الاصطناعي: ' + err);
      } finally {
        document.getElementById('loadingOverlay').style.display = 'none';
        document.getElementById('btnScan').disabled = false;
      }
    }

    function renderResults(data) {
      // Update HUD
      document.getElementById('statTotal').innerText = data.total_runes;
      document.getElementById('stat0').innerText = data.stats.angle_0;
      document.getElementById('stat180').innerText = data.stats.angle_180;
      document.getElementById('stat90').innerText = data.stats.angle_90;
      document.getElementById('stat270').innerText = data.stats.angle_270;

      // Update Image
      const img = document.getElementById('resultImage');
      img.src = data.annotated_image;
      img.style.display = 'block';

      // Update Ribbon
      document.getElementById('ribbonPanel').style.display = 'block';
      document.getElementById('runicDisplay').innerText = data.runic_text || '—';
      document.getElementById('latinDisplay').innerText = data.transliteration || '—';

      // Update Grid
      const grid = document.getElementById('runesGrid');
      grid.innerHTML = '';
      document.getElementById('runesPanel').style.display = 'block';

      data.detections.forEach(d => {
        const badge = document.createElement('div');
        badge.className = 'rune-badge';
        const tagClass = 'tag-' + d.angle;
        badge.innerHTML = `
          <div class="rune-glyph">${d.rune}</div>
          <div class="rune-meta">${d.name} (${d.latin})</div>
          <div class="rune-trans">${d.meaning || 'Younger Futhark'}</div>
          <span class="rune-tag ${tagClass}">زاوية ${d.angle}° | ${(d.conf * 100).toFixed(0)}%</span>
        `;
        grid.appendChild(badge);
      });
    }

    function copyText() {
      const text = document.getElementById('runicDisplay').innerText + '\\n' + document.getElementById('latinDisplay').innerText;
      navigator.clipboard.writeText(text);
      alert('تم نسخ النص الروني وترجمته بنجاح!');
    }

    // Auto-load first sample on start
    window.onload = function() {
      const firstSample = document.querySelector('.sample-item');
      if (firstSample) firstSample.click();
    };
  </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE, samples=SAMPLES)

@app.route("/sample/<sample_id>")
def get_sample_data(sample_id):
    for s in SAMPLES:
        if s["id"] == sample_id:
            if s["path"].exists():
                with open(s["path"], "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                mime = "image/png" if s["path"].suffix.lower() == ".png" else "image/jpeg"
                return jsonify({
                    "id": s["id"],
                    "title": s["title"],
                    "image_base64": f"data:{mime};base64,{b64}"
                })
    return jsonify({"error": "Sample not found"}), 404

@app.route("/predict_web", methods=["POST"])
def predict_web():
    try:
        data = request.get_json(silent=True)
        if not data or "image_base64" not in data:
            return jsonify({"error": "No image data provided"}), 400

        img_b64 = data["image_base64"].split(",")[-1]
        img_bytes = base64.b64decode(img_b64)
        nparr = np.frombuffer(img_bytes, np.uint8)
        cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if cv_img is None:
            return jsonify({"error": "Could not decode image"}), 400

        conf = float(data.get("conf", 0.18))
        enable_4way = bool(data.get("enable_4way", True))

        result = process_viking_image(cv_img, conf_thresh=conf, imgsz=1024, enable_4way=enable_4way)
        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    PORT = 5050
    print(f"\n===========================================================")
    print(f"  Viking Epigraphy Web Testing Platform")
    print(f"  Running on: http://127.0.0.1:{PORT}")
    print(f"  Model: Full-Precision Float32 (1024x1024) + 4-Way TTA 360")
    print(f"===========================================================\n")
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)
