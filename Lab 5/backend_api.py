import os
import sys
import io
import json
import base64
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, request, jsonify, send_file

# Set utf-8 output encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

app = Flask(__name__)

# Native CORS handling (zero external dependency)
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "LASTMODEL" / "best(1).pt"
if not MODEL_PATH.exists():
    MODEL_PATH = BASE_DIR / "viking_finetune_dataset" / "viking_master_epigraphy_v2_best.pt"

import torch
num_threads = os.cpu_count() or 4
torch.set_num_threads(num_threads)
device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"Loading YOLO Model from: {MODEL_PATH} on device={device} (threads={num_threads}) ...")
from ultralytics import YOLO
model = YOLO(str(MODEL_PATH))
print(f"YOLO Model loaded successfully on {device}!")

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
    font_rune = ImageFont.truetype(FONT_PATH, 18)
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

def process_image(cv_img, conf_thresh=0.18, imgsz=1024, enable_4way=True):
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

    # Sort detections reading order: primary by Y ribbons, then by X
    all_accepted.sort(key=lambda d: (round(d["cy"] / 60), d["cx"]))

    runic_text = "".join([d["rune"] for d in all_accepted])
    latin_translit = "".join([d["latin"] for d in all_accepted])

    # Render Annotated Image
    COLOR_MAP = {
        0:   (0, 220, 70),     # Green
        180: (30, 180, 255),   # Bright Sky Blue
        90:  (255, 140, 0),    # Orange
        270: (230, 0, 230)     # Magenta
    }

    pil_img = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)

    for d in all_accepted:
        box = [int(v) for v in d["box"]]
        color = COLOR_MAP.get(d["angle"], (0, 255, 0))
        draw.rectangle(box, outline=color, width=2)
        label_text = str(d["rune"])
        bw = box[2] - box[0]
        bbox = draw.textbbox((0, 0), label_text, font=font_rune)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = box[0] + (bw - tw) // 2
        ty = max(0, box[1] - th - 4)
        draw.rectangle([tx - 2, ty - 2, tx + tw + 2, ty + th + 2], fill=(15, 20, 25), outline=color, width=1)
        draw.text((tx, ty - 1), label_text, fill=(255, 255, 255), font=font_rune)

    # Encode to base64 JPEG
    buffer = io.BytesIO()
    pil_img.save(buffer, format="JPEG", quality=90)
    b64_img = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return {
        "success": True,
        "width": orig_w,
        "height": orig_h,
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

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": str(MODEL_PATH.name), "classes": len(model.names)})

@app.route("/samples", methods=["GET"])
def get_samples():
    sample_files = [
        {"id": "viggeby", "name": "Viggeby Runestone (Vertical Arch)", "file": "se-rune-viggeby.jpg"},
        {"id": "drawing", "name": "Dr 42 Inscribed Monument (Boustrophedon)", "file": "sample_drawing.jpg"},
        {"id": "stone_1", "name": "Real Stone #1 (Maria Sun Hiabi)", "file": "1.png"},
        {"id": "stone_10", "name": "Real Stone #10 (Tóki Memorial)", "file": "10.png"},
    ]
    return jsonify(sample_files)

@app.route("/samples/<sample_id>", methods=["GET"])
def get_sample_image(sample_id):
    path_map = {
        "viggeby": BASE_DIR / "images" / "se-rune-viggeby.jpg",
        "drawing": Path(r"C:\Users\ZBook 4K\.gemini\antigravity-ide\brain\fa0c5609-b873-439c-ba02-db6bf84af288\.user_uploaded\media_1788706143443.jpg"),
        "stone_1": BASE_DIR / "imagesfintune" / "1.png",
        "stone_10": BASE_DIR / "imagesfintune" / "10.png",
    }
    file_path = path_map.get(sample_id)
    if file_path and file_path.exists():
        return send_file(str(file_path), mimetype="image/jpeg" if file_path.suffix.lower() in [".jpg", ".jpeg"] else "image/png")
    return jsonify({"error": "Sample not found"}), 404

@app.route("/predict", methods=["POST"])
def predict():
    try:
        conf = float(request.form.get("conf", 0.18))
        imgsz = int(request.form.get("imgsz", 1024))
        enable_4way = request.form.get("enable_4way", "true").lower() in ["true", "1", "yes"]

        if "image" not in request.files:
            # Check JSON base64
            data = request.get_json(silent=True)
            if data and "image_base64" in data:
                img_data = base64.b64decode(data["image_base64"].split(",")[-1])
                nparr = np.frombuffer(img_data, np.uint8)
                cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            else:
                return jsonify({"error": "No image file or image_base64 provided"}), 400
        else:
            file = request.files["image"]
            file_bytes = file.read()
            nparr = np.frombuffer(file_bytes, np.uint8)
            cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if cv_img is None:
            return jsonify({"error": "Could not decode image"}), 400

        result = process_image(cv_img, conf_thresh=conf, imgsz=imgsz, enable_4way=enable_4way)
        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n===========================================================")
    print(f"  Viking Epigraphy Flask AI Server Running on port {port}")
    print(f"  Local API: http://127.0.0.1:{port}")
    print(f"  Ready for Flutter App connections!")
    print(f"===========================================================\n")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
