import cv2
import json
from pathlib import Path
from ultralytics import YOLO

model_path = r"C:\Users\ZBook 4K\Desktop\Lab 5\LASTMODEL\best(1).pt"
img_path = r"C:\Users\ZBook 4K\.gemini\antigravity-ide\brain\fa0c5609-b873-439c-ba02-db6bf84af288\.user_uploaded\media_1788706143443.jpg"
out_dir = Path(r"C:\Users\ZBook 4K\Desktop\Lab 5\master_model_test_results")
out_dir.mkdir(parents=True, exist_ok=True)

model = YOLO(model_path)

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

for test_conf in [0.15, 0.18, 0.22, 0.25]:
    r = model.predict(img_path, conf=test_conf, imgsz=1024, device="cpu", verbose=False)[0]
    print(f"Conf threshold: {test_conf} -> Detected: {len(r.boxes)} runes")

# Best operational confidence
r = model.predict(img_path, conf=0.18, imgsz=1024, device="cpu", verbose=False)[0]
dets = []
for b in r.boxes:
    cls_id = int(b.cls[0].item())
    conf = float(b.conf[0].item())
    xyxy = b.xyxy[0].tolist()
    info = RUNES_INFO.get(cls_id, {"rune": "?", "latin": "?", "name": model.names.get(cls_id, "unknown")})
    dets.append({
        "cls_id": cls_id,
        "name": info["name"],
        "rune": info["rune"],
        "latin": info["latin"],
        "conf": conf,
        "box": [round(x, 1) for x in xyxy],
        "cx": (xyxy[0] + xyxy[2]) / 2,
        "cy": (xyxy[1] + xyxy[3]) / 2
    })

orig_h, orig_w = r.orig_shape
print(f"\nImage Dimensions: {orig_w} x {orig_h}")

# The image has two inscription lines:
# Upper line y is roughly 120-200
# Lower line y is roughly 200-280
upper_line = sorted([d for d in dets if d["cy"] < 200], key=lambda x: x["cx"])
lower_line = sorted([d for d in dets if 200 <= d["cy"] < 320], key=lambda x: x["cx"])

print("\n=======================================================")
print(f" [1] UPPER LINE DETECTIONS ({len(upper_line)} runes):")
print("=======================================================")
print("Runic Text    : " + "".join([d["rune"] for d in upper_line]))
print("Transliterated: " + "".join([d["latin"] for d in upper_line]))
for d in upper_line:
    print(f"  {d['rune']} ({d['name']:10s} : {d['conf']:.2f})  at x={d['cx']:.0f}, y={d['cy']:.0f}")

print("\n=======================================================")
print(f" [2] LOWER LINE DETECTIONS ({len(lower_line)} runes):")
print("=======================================================")
print("Runic Text    : " + "".join([d["rune"] for d in lower_line]))
print("Transliterated: " + "".join([d["latin"] for d in lower_line]))
for d in lower_line:
    print(f"  {d['rune']} ({d['name']:10s} : {d['conf']:.2f})  at x={d['cx']:.0f}, y={d['cy']:.0f}")

# Save annotated image
ann_img = r.plot()
out_save = out_dir / "user_image_detected.jpg"
cv2.imwrite(str(out_save), ann_img)
print(f"\nAnnotated image saved to:\n  {out_save}")

art_save = Path(r"C:\Users\ZBook 4K\.gemini\antigravity-ide\brain\fa0c5609-b873-439c-ba02-db6bf84af288\user_image_detected.jpg")
cv2.imwrite(str(art_save), ann_img)
print(f"Saved copy to artifact directory:\n  {art_save}")
