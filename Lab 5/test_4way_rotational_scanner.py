import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO

# 1. Configuration
MODEL_PATH = r"C:\Users\ZBook 4K\Desktop\Lab 5\LASTMODEL\best(1).pt"
IMG_PATH = r"C:\Users\ZBook 4K\.gemini\antigravity-ide\brain\fa0c5609-b873-439c-ba02-db6bf84af288\.user_uploaded\media_1788706143443.jpg"
OUTPUT_DIR = Path(r"C:\Users\ZBook 4K\Desktop\Lab 5\master_model_test_results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RUNES_INFO = {
    0:  {"rune": "ᚠ", "latin": "f",   "name": "fehu"},
    1:  {"rune": "ᚢ", "latin": "u",   "name": "uruz"},
    2:  {"rune": "ᚦ", "latin": "th",  "name": "thurisaz"},
    3:  {"rune": "ᚬ", "latin": "a",   "name": "ansuz"},
    4:  {"rune": "ᚱ", "latin": "r",   "name": "raidho"},
    5:  {"rune": "ᚴ", "latin": "k",   "name": "kaunan"},
    6:  {"rune": "ᚼ", "latin": "h",   "name": "hagalaz"},
    7:  {"rune": "ᚾ", "latin": "n",   "name": "naudiz"},
    8:  {"rune": "ᛁ", "latin": "i",   "name": "isaz"},
    9:  {"rune": "ᛅ", "latin": "a",   "name": "ar_jera"},
    10: {"rune": "ᛋ", "latin": "s",   "name": "sowilo"},
    11: {"rune": "ᛏ", "latin": "t",   "name": "tiwaz"},
    12: {"rune": "ᛒ", "latin": "b",   "name": "berkanan"},
    13: {"rune": "ᛉ", "latin": "m",   "name": "mannaz"},
    14: {"rune": "ᛚ", "latin": "l",   "name": "laguz"},
    15: {"rune": "ᛦ", "latin": "R",   "name": "yr"},
    16: {"rune": ":", "latin": ":",   "name": "separator"},
}

def calculate_iou(boxA, boxB):
    # box = [x1, y1, x2, y2]
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    if interArea == 0:
        return 0.0

    boxAArea = max(1e-5, (boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    boxBArea = max(1e-5, (boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))

    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou

def is_point_inside(px, py, box):
    return (box[0] <= px <= box[2]) and (box[1] <= py <= box[3])

def mask_detected_regions(img, boxes):
    masked = img.copy()
    for box in boxes:
        x1, y1, x2, y2 = [int(v) for v in box]
        h, w = img.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w - 1, x2), min(h - 1, y2)
        if x2 > x1 and y2 > y1:
            # Sample surrounding border pixels for median stone color
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
        # Rotated 90 CW: W_rot = H, H_rot = W
        ox1 = ry1
        ox2 = ry1_max
        oy1 = orig_h - 1 - rx2
        oy2 = orig_h - 1 - rx1
        return [min(ox1, ox2), min(oy1, oy2), max(ox1, ox2), max(oy1, oy2)]
    elif angle == 270:
        # Rotated 270 CW (90 CCW)
        ox1 = orig_w - 1 - ry1_max
        ox2 = orig_w - 1 - ry1
        oy1 = rx1
        oy2 = rx2
        return [min(ox1, ox2), min(oy1, oy2), max(ox1, ox2), max(oy1, oy2)]
    return box

def run_rotational_scan(img_path, conf_thresh=0.18, imgsz=1024):
    print("=" * 75)
    print(" Viking Epigraphy 4-Way Rotational TTA Scanner")
    print(f" Image: {img_path}")
    print(f" Model: {MODEL_PATH}")
    print("=" * 75)

    model = YOLO(MODEL_PATH)
    raw_img = cv2.imread(str(img_path))
    if raw_img is None:
        raise FileNotFoundError(f"Could not load image from {img_path}")
    
    orig_h, orig_w = raw_img.shape[:2]
    working_img = raw_img.copy()

    rotations = [
        (0, None, "Normal (0° Upright)"),
        (180, cv2.ROTATE_180, "Inverted (180° Upside-Down)"),
        (90, cv2.ROTATE_90_CLOCKWISE, "Vertical Right (90° CW)"),
        (270, cv2.ROTATE_90_COUNTERCLOCKWISE, "Vertical Left (270° CW)"),
    ]

    all_accepted_detections = []
    round_stats = {}

    for angle, cv_rot, desc in rotations:
        print(f"\n[🔄 Scanning Pass] {desc} ...")
        
        # 1. Mask previously detected regions on the working image
        if all_accepted_detections:
            prev_boxes = [d["box"] for d in all_accepted_detections]
            masked_img = mask_detected_regions(working_img, prev_boxes)
        else:
            masked_img = working_img

        # 2. Apply rotation
        if cv_rot is not None:
            scan_img = cv2.rotate(masked_img, cv_rot)
        else:
            scan_img = masked_img

        # 3. Model Inference on rotated orientation
        results = model.predict(source=scan_img, conf=conf_thresh, imgsz=imgsz, device="cpu", verbose=False)[0]
        boxes = results.boxes

        new_accepted = 0
        rejected_overlap = 0

        if boxes is not None and len(boxes) > 0:
            for b in boxes:
                cls_id = int(b.cls[0].item())
                conf = float(b.conf[0].item())
                r_box = b.xyxy[0].tolist()

                # 4. Map box back to original coordinates
                orig_box = transform_box_to_original(r_box, angle, orig_w, orig_h)
                cx = (orig_box[0] + orig_box[2]) / 2.0
                cy = (orig_box[1] + orig_box[3]) / 2.0

                # 5. Spatial Exclusion Check: IoU and Center Inside
                overlap = False
                for accepted in all_accepted_detections:
                    iou = calculate_iou(orig_box, accepted["box"])
                    if iou > 0.15 or is_point_inside(cx, cy, accepted["box"]):
                        overlap = True
                        break

                if overlap:
                    rejected_overlap += 1
                    continue

                info = RUNES_INFO.get(cls_id, {"rune": "?", "latin": "?", "name": model.names.get(cls_id, "unknown")})
                all_accepted_detections.append({
                    "cls_id": cls_id,
                    "name": info["name"],
                    "rune": info["rune"],
                    "latin": info["latin"],
                    "conf": conf,
                    "angle": angle,
                    "box": [round(x, 1) for x in orig_box],
                    "cx": cx,
                    "cy": cy
                })
                new_accepted += 1

        print(f"  ✓ Found {len(boxes)} candidates -> Accepted: {new_accepted}, Rejected Overlaps: {rejected_overlap}")
        round_stats[angle] = new_accepted

    print("\n" + "=" * 75)
    print(" SCAN SUMMARY BY ORIENTATION:")
    print("=" * 75)
    for angle, count in round_stats.items():
        print(f"  • Angle {angle:3d}°: {count:2d} runes discovered")
    print(f"  Total Unique Epigraphic Runes: {len(all_accepted_detections)}")

    # Group into ribbon lines (Upper and Lower) based on Y-coordinate
    upper_line = sorted([d for d in all_accepted_detections if d["cy"] < 205], key=lambda x: x["cx"])
    lower_line = sorted([d for d in all_accepted_detections if 205 <= d["cy"] < 320], key=lambda x: x["cx"])

    print("\n[Upper Ribbon Detected Runes]")
    print(f"  Count: {len(upper_line)} runes")
    print("  Runes : " + "".join([d["rune"] for d in upper_line]))
    print("  Latin : " + "".join([d["latin"] for d in upper_line]))
    
    print("\n[Lower Ribbon Detected Runes]")
    print(f"  Count: {len(lower_line)} runes")
    print("  Runes : " + "".join([d["rune"] for d in lower_line]))
    print("  Latin : " + "".join([d["latin"] for d in lower_line]))

    # Draw color-coded bounding boxes on original image with Pillow for full Unicode support
    from PIL import Image, ImageDraw, ImageFont

    COLOR_MAP = {
        0:   (0, 220, 70),     # Green
        180: (30, 180, 255),   # Bright Sky Blue
        90:  (255, 140, 0),    # Orange
        270: (230, 0, 230)     # Magenta
    }

    # Load Historic Unicode font for runes
    font_path = r"C:\Windows\Fonts\seguihis.ttf"
    try:
        font_rune = ImageFont.truetype(font_path, 18)
    except Exception:
        font_rune = ImageFont.load_default()

    pil_img = Image.fromarray(cv2.cvtColor(raw_img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)

    for idx, d in enumerate(all_accepted_detections):
        box = [int(v) for v in d["box"]]
        color = COLOR_MAP.get(d["angle"], (0, 255, 0))
        
        # Draw box outline
        draw.rectangle(box, outline=color, width=2)
        
        # Display ONLY the Rune symbol itself
        label_text = str(d['rune'])
        
        # Compute badge background position directly above the box
        bw = box[2] - box[0]
        bbox = draw.textbbox((0, 0), label_text, font=font_rune)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        # Center the rune horizontally above the box
        tx = box[0] + (bw - text_w) // 2
        ty = max(0, box[1] - text_h - 4)
        
        badge_bg = [tx - 2, ty - 2, tx + text_w + 2, ty + text_h + 2]
        draw.rectangle(badge_bg, fill=(15, 20, 25))
        draw.rectangle(badge_bg, outline=color, width=1)
        
        # Draw the Rune symbol in pure white or bright contrast
        draw.text((tx, ty - 1), label_text, fill=(255, 255, 255), font=font_rune)

    out_file = OUTPUT_DIR / "rotational_tta_result.jpg"
    pil_img.save(str(out_file), quality=95)
    print(f"\nAnnotated result with rune symbols only saved to:\n  {out_file}")

    art_file = Path(r"C:\Users\ZBook 4K\.gemini\antigravity-ide\brain\fa0c5609-b873-439c-ba02-db6bf84af288\rotational_tta_result.jpg")
    pil_img.save(str(art_file), quality=95)
    print(f"Artifact copy saved to:\n  {art_file}")

    # Generate a High-Resolution Zoomed Crop of the Inscribed Ribbons (y: 110 to 310)
    crop_box = (0, 110, orig_w, 310)
    cropped_ribbon = pil_img.crop(crop_box)
    cropped_ribbon_2x = cropped_ribbon.resize((cropped_ribbon.width * 2, cropped_ribbon.height * 2), Image.Resampling.LANCZOS)
    
    crop_file = OUTPUT_DIR / "ribbon_zoom_names.jpg"
    cropped_ribbon_2x.save(str(crop_file), quality=95)
    print(f"High-res ribbon crop with rune symbols saved to:\n  {crop_file}")

    art_crop = Path(r"C:\Users\ZBook 4K\.gemini\antigravity-ide\brain\fa0c5609-b873-439c-ba02-db6bf84af288\ribbon_zoom_names.jpg")
    cropped_ribbon_2x.save(str(art_crop), quality=95)

if __name__ == "__main__":
    run_rotational_scan(IMG_PATH)
