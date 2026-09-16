import os
import sys
from pathlib import Path
import json
import cv2
import numpy as np
from ultralytics import YOLO

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(r"C:\Users\ZBook 4K\Desktop\Lab 5")
DEFAULT_MODEL = BASE_DIR / "LASTMODEL" / "best(1).pt"
MODEL_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MODEL
DATASET_YAML = BASE_DIR / "viking_finetune_dataset" / "dataset.yaml"
OUTPUT_DIR = BASE_DIR / "master_model_test_results"
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

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

def test_model():
    print("=" * 70)
    print(" Viking Master Epigraphy Model Evaluation")
    print(f" Model Path: {MODEL_PATH}")
    print("=" * 70)

    if not MODEL_PATH.exists():
        print(f"Error: Model not found at {MODEL_PATH}")
        return

    # Load Model
    model = YOLO(str(MODEL_PATH))
    print(f"\n[1/3] Model Loaded Successfully!")
    print(f" Model Task: {model.task}")
    print(f" Number of Classes: {len(model.names)}")
    print(f" Class Names: {list(model.names.values())}")

    # 1. Quantitative Validation
    val_results = None
    if DATASET_YAML.exists():
        print("\n" + "=" * 70)
        print(" [2/3] Running Validation Evaluation on Validation Set (36 images)...")
        print("=" * 70)
        try:
            metrics = model.val(
                data=str(DATASET_YAML),
                imgsz=1024,
                batch=2,
                device="cpu",
                plots=False,
                save_json=False,
                verbose=True
            )
            val_results = {
                "precision": float(metrics.box.mp),
                "recall": float(metrics.box.mr),
                "mAP50": float(metrics.box.map50),
                "mAP50_95": float(metrics.box.map),
            }
            print("\n--- Summary Validation Metrics ---")
            print(f" Precision (P) : {val_results['precision'] * 100:.2f}%")
            print(f" Recall (R)    : {val_results['recall'] * 100:.2f}%")
            print(f" mAP@0.50      : {val_results['mAP50'] * 100:.2f}%")
            print(f" mAP@0.50:0.95 : {val_results['mAP50_95'] * 100:.2f}%")
        except Exception as e:
            print(f"Validation note: {e}")

    # 2. Qualitative Inference on Real Stone Images & Val Images
    print("\n" + "=" * 70)
    print(" [3/3] Running Inference on Test Epigraphy & Stone Images...")
    print("=" * 70)

    real_images = sorted(list((BASE_DIR / "imagesfintune").glob("*.png")) + list((BASE_DIR / "imagesfintune").glob("*.jpg")))
    # Select a diverse spread of real stone images
    selected_real = [img for img in real_images if img.name != "viking_master_epigraphy_best.pt"][:12]

    val_images = sorted(list((BASE_DIR / "viking_finetune_dataset" / "images" / "val").glob("*.png")))[:6]

    test_queue = [("Real Stone", img) for img in selected_real] + [("Val Dataset", img) for img in val_images]

    predictions_summary = []

    for category, img_path in test_queue:
        results = model.predict(source=str(img_path), conf=0.20, imgsz=1024, device="cpu", verbose=False)[0]
        boxes = results.boxes

        detections = []
        if boxes is not None and len(boxes) > 0:
            for b in boxes:
                cls_id = int(b.cls[0].item())
                conf = float(b.conf[0].item())
                xyxy = b.xyxy[0].tolist()
                cx = (xyxy[0] + xyxy[2]) / 2
                
                info = RUNES_INFO.get(cls_id, {"rune": "?", "latin": "?", "name": model.names.get(cls_id, "unknown")})
                detections.append({
                    "cls_id": cls_id,
                    "name": info["name"],
                    "rune": info["rune"],
                    "latin": info["latin"],
                    "conf": conf,
                    "cx": cx,
                    "box": [round(x, 1) for x in xyxy]
                })

        # Sort detections horizontally (left to right)
        detections.sort(key=lambda d: d["cx"])
        runic_string = "".join([d["rune"] for d in detections])
        latin_translit = "".join([d["latin"] for d in detections])

        print(f"\n[{category}] Image: {img_path.name}")
        if detections:
            print(f"  Count: {len(detections)} runes detected")
            print(f"  Runic Text    : {runic_string}")
            print(f"  Transliterated: {latin_translit}")
            conf_str = ", ".join([f"{d['rune']}({d['name']}:{d['conf']:.2f})" for d in detections[:8]])
            if len(detections) > 8:
                conf_str += f" ... (+{len(detections)-8} more)"
            print(f"  Confidence    : {conf_str}")
        else:
            print("  No runes detected at conf=0.25")

        # Save annotated image
        annotated_img = results.plot()
        save_path = OUTPUT_DIR / f"{img_path.stem}_pred.jpg"
        cv2.imwrite(str(save_path), annotated_img)

        predictions_summary.append({
            "image": img_path.name,
            "category": category,
            "num_detected": len(detections),
            "runic": runic_string,
            "latin": latin_translit,
            "detections": detections,
            "saved_to": str(save_path.name)
        })

    # Save test report JSON
    report = {
        "model_path": str(MODEL_PATH),
        "validation_metrics": val_results,
        "sample_predictions": predictions_summary
    }
    with open(OUTPUT_DIR / "test_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print("Testing Complete!")
    print(f"Annotated prediction images & report saved to:")
    print(f" {OUTPUT_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    test_model()
