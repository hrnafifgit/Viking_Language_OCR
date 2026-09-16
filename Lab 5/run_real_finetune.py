"""
================================================================================
  Viking Rune YOLO - Real Stone Fine-Tuning Script
  - Fine-tunes pre-trained model on real archaeological stone inscriptions
  - Uses transfer learning with backbone freezing (preserves rune geometry)
  - Prevents chirality flipping (fliplr=0.0, flipud=0.0)
  - Disables plots=False during validation to prevent Pillow x1>=x0 crash
================================================================================
"""

import os
import sys
from pathlib import Path
import torch
from ultralytics import YOLO

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent

# 1. Paths configuration
STARTING_MODEL = BASE_DIR / "viking_finetune_dataset" / "viking_master_epigraphy_v2_best.pt"
if not STARTING_MODEL.exists():
    STARTING_MODEL = BASE_DIR / "best.pt"

DATASET_YAML = BASE_DIR / "viking_finetune_dataset" / "dataset.yaml"
OUTPUT_DIR = BASE_DIR / "runs_real_finetune"

def run_finetuning(
    model_path=str(STARTING_MODEL),
    data_yaml=str(DATASET_YAML),
    epochs=40,
    batch=8,
    imgsz=640,
    freeze_layers=10,
    lr0=0.001,
):
    print("=" * 70)
    print(" Viking Rune Real-Stone Fine-Tuning")
    print(f" Initial Model : {model_path}")
    print(f" Dataset YAML  : {data_yaml}")
    print(f" Epochs        : {epochs}")
    print(f" Batch Size    : {batch}")
    print(f" Resolution    : {imgsz}x{imgsz}")
    print(f" Freeze Layers : {freeze_layers} (Backbone)")
    print(f" Initial LR    : {lr0}")
    print("=" * 70)

    # Hardware detection
    device = "0" if torch.cuda.is_available() else "cpu"
    if device == "cpu":
        torch.set_num_threads(os.cpu_count() or 4)
        print(f" Using CPU with {torch.get_num_threads()} threads")
        if batch > 4:
            batch = 4  # Safer batch size on CPU
            print(f" Reduced batch to {batch} for CPU training")
    else:
        print(f" Using GPU: {torch.cuda.get_device_name(0)}")

    # Load Model
    model = YOLO(model_path)

    # Run Fine-Tuning
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        batch=batch,
        imgsz=imgsz,
        device=device,
        project=str(OUTPUT_DIR),
        name="real_stone_epigraphy",
        exist_ok=True,
        pretrained=True,
        freeze=freeze_layers,       # Freeze backbone to prevent catastrophic forgetting
        lr0=lr0,                    # Lower initial learning rate for fine-tuning
        lrf=0.01,                   # Final learning rate factor (cosine decay)
        cos_lr=True,
        warmup_epochs=2.0,
        # Critical Epigraphic Constraints:
        fliplr=0.0,                 # DO NOT flip horizontally (distorts rune letters)
        flipud=0.0,                 # DO NOT flip vertically
        degrees=5.0,                # Minor tilt only
        scale=0.2,                  # Scale variation
        hsv_h=0.015,                # Lighting variation
        hsv_s=0.6,                  # Weathering/saturation variation
        hsv_v=0.4,                  # Brightness variation
        mosaic=0.3,
        patience=15,                # Early stopping
        plots=False,                # Avoid PIL x1>=x0 crash
        val=True,
        save=True,
        verbose=True
    )

    best_weights = OUTPUT_DIR / "real_stone_epigraphy" / "weights" / "best.pt"
    print("\n" + "=" * 70)
    print(" Fine-Tuning Completed Successfully!")
    if best_weights.exists():
        print(f" Best Fine-Tuned Model Saved to:\n   {best_weights}")
    print("=" * 70)

    # Quick evaluation on the val set
    print("\n Running Final Validation on Real Test Images...")
    val_metrics = model.val(
        data=data_yaml,
        imgsz=imgsz,
        device=device,
        plots=False,
        verbose=True
    )
    print(f" Final Precision (P) : {val_metrics.box.mp * 100:.2f}%")
    print(f" Final Recall (R)    : {val_metrics.box.mr * 100:.2f}%")
    print(f" Final mAP@0.50      : {val_metrics.box.map50 * 100:.2f}%")
    print(f" Final mAP@0.50:0.95 : {val_metrics.box.map * 100:.2f}%")

if __name__ == "__main__":
    run_finetuning()
