"""
================================================================================
  Full Stone Sliding Window (SAHI) Inference & Inscription Reader
  - Reads large real stone monuments of any resolution (even 4K/8K)
  - Uses overlapping sliding windows (patches) matching the fine-tuned model
  - Merges bounding boxes via global Non-Maximum Suppression (NMS)
  - Transliterates and reads the full runic inscription into Latin text
================================================================================
"""

import os
import sys
from pathlib import Path
import numpy as np
import cv2
import torch
from ultralytics import YOLO

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent

RUNES_DICT = {
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
    16: {"rune": ":", "latin": " : ", "name": "separator"},
}

def nms_boxes(boxes, scores, iou_threshold=0.45):
    """Standard Non-Maximum Suppression for merged patch boxes."""
    if len(boxes) == 0:
        return []
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]
    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    order = scores.argsort()[::-1]
    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])
        w = np.maximum(0.0, xx2 - xx1 + 1)
        h = np.maximum(0.0, yy2 - yy1 + 1)
        inter = w * h
        ovr = inter / (areas[i] + areas[order[1:]] - inter)
        inds = np.where(ovr <= iou_threshold)[0]
        order = order[inds + 1]
    return keep

def scan_full_stone(
    image_path: str,
    model_path: str,
    window_size: int = 640,
    overlap: float = 0.25,
    conf_thresh: float = 0.35,
    output_annotated_path: str = None
):
    """Scans full stone monument using sliding window inference."""
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")

    h, w = img.shape[:2]
    model = YOLO(model_path)
    step = int(window_size * (1 - overlap))

    all_boxes = []
    all_scores = []
    all_classes = []

    # Slide window across entire image
    y_starts = list(range(0, max(1, h - window_size + 1), step))
    if y_starts[-1] + window_size < h:
        y_starts.append(h - window_size)

    x_starts = list(range(0, max(1, w - window_size + 1), step))
    if x_starts[-1] + window_size < w:
        x_starts.append(w - window_size)

    # Handle smaller images directly
    if h <= window_size and w <= window_size:
        y_starts = [0]
        x_starts = [0]

    for y in y_starts:
        for x in x_starts:
            patch = img[y:y+window_size, x:x+window_size]
            results = model.predict(patch, conf=conf_thresh, imgsz=window_size, verbose=False)[0]

            if results.boxes is not None and len(results.boxes) > 0:
                for box in results.boxes:
                    bx1, by1, bx2, by2 = box.xyxy[0].tolist()
                    score = float(box.conf[0].item())
                    cid = int(box.cls[0].item())

                    # Shift coordinates back to global full image
                    gx1 = bx1 + x
                    gy1 = by1 + y
                    gx2 = bx2 + x
                    gy2 = by2 + y

                    all_boxes.append([gx1, gy1, gx2, gy2])
                    all_scores.append(score)
                    all_classes.append(cid)

    if not all_boxes:
        print(f"⚠️ No runes detected with confidence >= {conf_thresh}")
        return "", img

    # Global NMS merging
    boxes_np = np.array(all_boxes)
    scores_np = np.array(all_scores)
    classes_np = np.array(all_classes)

    keep_indices = nms_boxes(boxes_np, scores_np, iou_threshold=0.40)
    final_boxes = boxes_np[keep_indices]
    final_scores = scores_np[keep_indices]
    final_classes = classes_np[keep_indices]

    # Order characters sequentially (Left to Right along the stone ribbon)
    detections = []
    for i in range(len(final_boxes)):
        x1, y1, x2, y2 = final_boxes[i]
        cid = int(final_classes[i])
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        detections.append({
            "box": (int(x1), int(y1), int(x2), int(y2)),
            "score": float(final_scores[i]),
            "cid": cid,
            "rune": RUNES_DICT[cid]["rune"],
            "latin": RUNES_DICT[cid]["latin"],
            "cx": cx,
            "cy": cy
        })

    # Sort left-to-right (horizontal priority)
    detections.sort(key=lambda d: d["cx"])

    # Build decoded inscription string
    rune_str = "".join([d["rune"] for d in detections])
    latin_str = "".join([d["latin"] for d in detections])

    # Draw visual annotations
    annotated = img.copy()
    for d in detections:
        x1, y1, x2, y2 = d["box"]
        cid = d["cid"]
        color = (0, 220, 80) if cid != 16 else (40, 100, 255) # Separator in orange
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        cv2.putText(annotated, f"{d['latin']} ({d['score']:.2f})", (x1, max(18, y1-6)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

    if output_annotated_path:
        cv2.imwrite(output_annotated_path, annotated)
        print(f"✓ Saved annotated reading to: {output_annotated_path}")

    print("\n" + "=" * 60)
    print(f"📖 DETECTED RUNIC INSCRIPTION ({len(detections)} GLYPHS):")
    print(f"   Runes        : {rune_str}")
    print(f"   Transliterated: {latin_str}")
    print("=" * 60)

    return latin_str, annotated

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Full Stone Sliding Window Inscription Reader")
    parser.add_argument("--image", type=str, default="imagesfintune/1.png", help="Path to stone photo")
    parser.add_argument("--model", type=str, default="yolov8n.pt", help="Path to best.pt model")
    parser.add_argument("--output", type=str, default="decoded_stone.jpg", help="Output annotated image")
    args = parser.parse_args()

    if os.path.exists(args.image):
        scan_full_stone(args.image, args.model, output_annotated_path=args.output)
    else:
        print(f"File not found: {args.image}")
