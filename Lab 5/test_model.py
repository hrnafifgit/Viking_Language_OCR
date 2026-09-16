import os
import sys
from pathlib import Path
from ultralytics import YOLO
import cv2

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(r"c:\Users\ZBook 4K\Desktop\Lab 5")
MODEL_PATH = BASE_DIR / "viking_finetune_dataset" / "bestmodel" / "best.pt"
OUTPUT_DIR = BASE_DIR / "test_inference_output"
OUTPUT_DIR.mkdir(exist_ok=True)

RUNES_UNICODE = {
    "fehu": "ᚠ", "uruz": "ᚢ", "thurisaz": "ᚦ", "ansuz": "ᚬ",
    "raidho": "ᚱ", "kaunan": "ᚴ", "hagalaz": "ᚼ", "naudiz": "ᚾ",
    "isaz": "ᛁ", "ar_jera": "ᛅ", "sowilo": "ᛋ", "tiwaz": "ᛏ",
    "berkanan": "ᛒ", "mannaz": "ᛉ", "laguz": "ᛚ", "yr": "ᛦ",
    "separator": ":"
}

def main():
    print(f"Loading Model: {MODEL_PATH}")
    model = YOLO(str(MODEL_PATH))

    # 1. Select sample test images
    val_images = list((BASE_DIR / "viking_finetune_dataset" / "images" / "val").glob("*.png"))
    real_images = list((BASE_DIR / "imagesfintune").glob("*.png"))[:10]
    
    test_samples = val_images[:5] + real_images[:5]
    print(f"\nRunning predictions on {len(test_samples)} sample images...")

    for img_path in test_samples:
        results = model.predict(source=str(img_path), conf=0.25, imgsz=640, verbose=False)[0]
        
        boxes = results.boxes
        detected_runes = []
        
        if boxes is not None and len(boxes) > 0:
            for b in boxes:
                cls_id = int(b.cls[0].item())
                cls_name = model.names[cls_id]
                conf = float(b.conf[0].item())
                x1, y1, x2, y2 = b.xyxy[0].tolist()
                cx = (x1 + x2) / 2
                rune_char = RUNES_UNICODE.get(cls_name, "?")
                detected_runes.append((cx, cls_name, rune_char, conf))

            # Sort by horizontal position (reading direction)
            detected_runes.sort(key=lambda x: x[0])
            runic_text = "".join([r[2] for r in detected_runes])
            names_text = " - ".join([f"{r[1]}({r[3]:.2f})" for r in detected_runes])
            
            print(f"\n📷 Image: {img_path.name}")
            print(f"   Detected ({len(detected_runes)} runes): {runic_text}")
            print(f"   Details: {names_text}")
        else:
            print(f"\n📷 Image: {img_path.name} -> No runes detected at conf 0.25")

        # Save annotated image
        annotated_bgr = results.plot()
        out_save_path = OUTPUT_DIR / f"pred_{img_path.name}"
        cv2.imwrite(str(out_save_path), annotated_bgr)

    print(f"\n Annotated images successfully saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
