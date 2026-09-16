"""
================================================================================
  Viking Rune YOLOv8 - Curriculum Fine-Tuning Engine
  - 2-Stage Fine-Tuning:
      Stage 1: Frozen Backbone (Head Adaptation)
      Stage 2: Unfrozen End-to-End Fine-Tuning (Fine Feature Alignment)
  - Strict epigraphic chirality: fliplr=0.0, flipud=0.0
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
DATASET_YAML = BASE_DIR / "viking_finetune_dataset" / "dataset.yaml"
OUTPUT_RUNS = BASE_DIR / "finetune_runs"

# Find best starting checkpoint
CANDIDATE_WEIGHTS = [
    BASE_DIR / "runs" / "detect" / "train" / "weights" / "best.pt",
    BASE_DIR / "best.pt",
    BASE_DIR / "yolov8n.pt",
]

INITIAL_WEIGHTS = "yolov8n.pt"
for w in CANDIDATE_WEIGHTS:
    if w.exists():
        INITIAL_WEIGHTS = str(w)
        break

def run_curriculum_finetune(
    weights_path: str = INITIAL_WEIGHTS,
    epochs_stage1: int = 25,
    epochs_stage2: int = 25,
    img_size: int = 640,
    batch_size: int = 8,
    device: str = "0" if torch.cuda.is_available() else "cpu"
):
    print("=" * 70)
    print("🚀 Starting 2-Stage Curriculum Fine-Tuning on Viking Rune Stones")
    print(f"   Initial Weights: {weights_path}")
    print(f"   Dataset Config : {DATASET_YAML}")
    print(f"   Device         : {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")
    print(f"   Stage 1 Epochs : {epochs_stage1} (Frozen Backbone)")
    print(f"   Stage 2 Epochs : {epochs_stage2} (Full Fine Adjustment)")
    print("=" * 70)

    # ──────────────────────────────────────────────────────────────────────────
    # Stage 1: Frozen Backbone Adaptation (Head Only)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[+] --- STAGE 1: Freezing Backbone (Layer 0..9) ---")
    model_stage1 = YOLO(weights_path)
    
    stage1_results = model_stage1.train(
        data=str(DATASET_YAML),
        epochs=epochs_stage1,
        imgsz=img_size,
        batch=batch_size,
        device=device,
        freeze=10,            # Freeze backbone layers
        lr0=0.0015,           # Moderate learning rate for heads
        lrf=0.01,
        fliplr=0.0,           # CRITICAL: Do NOT mirror asymmetric runes
        flipud=0.0,
        degrees=12.0,         # Subtle rotation for stone tilt
        scale=0.25,           # Zoom variations
        close_mosaic=10,      # Clean final epochs
        project=str(OUTPUT_RUNS),
        name="stage1_frozen_backbone",
        exist_ok=True,
        verbose=True
    )

    stage1_best_weights = OUTPUT_RUNS / "stage1_frozen_backbone" / "weights" / "best.pt"
    if not stage1_best_weights.exists():
        stage1_best_weights = OUTPUT_RUNS / "stage1_frozen_backbone" / "weights" / "last.pt"

    print(f"✓ Stage 1 Finished! Best Stage 1 weights: {stage1_best_weights}")

    # ──────────────────────────────────────────────────────────────────────────
    # Stage 2: End-to-End Fine-Tuning with Low Learning Rate
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[+] --- STAGE 2: Unfrozen End-to-End Fine-Tuning ---")
    model_stage2 = YOLO(str(stage1_best_weights))
    
    stage2_results = model_stage2.train(
        data=str(DATASET_YAML),
        epochs=epochs_stage2,
        imgsz=img_size,
        batch=batch_size,
        device=device,
        freeze=0,             # Unfreeze all layers
        lr0=0.0004,           # Very low LR to prevent forgetting
        lrf=0.01,
        fliplr=0.0,
        flipud=0.0,
        degrees=8.0,
        scale=0.15,
        close_mosaic=10,
        project=str(OUTPUT_RUNS),
        name="stage2_full_finetune",
        exist_ok=True,
        verbose=True
    )

    final_best_weights = OUTPUT_RUNS / "stage2_full_finetune" / "weights" / "best.pt"
    master_save_path = BASE_DIR / "viking_master_finetuned_best.pt"

    if final_best_weights.exists():
        import shutil
        shutil.copy2(final_best_weights, master_save_path)
        print(f"\n🏆 Final Master Model saved to: {master_save_path}")

    # ──────────────────────────────────────────────────────────────────────────
    # Real Inscription Evaluation
    # ──────────────────────────────────────────────────────────────────────────
    eval_model = YOLO(str(master_save_path if master_save_path.exists() else final_best_weights))
    val_metrics = eval_model.val(data=str(DATASET_YAML))

    print("\n" + "=" * 70)
    print("📈 FINAL VALIDATION METRICS ON REAL STONE INSCRIPTIONS:")
    print(f"   mAP@50    : {val_metrics.box.map50:.4f}")
    print(f"   mAP@50-95 : {val_metrics.box.map:.4f}")
    print(f"   Precision : {val_metrics.box.mp:.4f}")
    print(f"   Recall    : {val_metrics.box.mr:.4f}")
    print("=" * 70)

if __name__ == "__main__":
    run_curriculum_finetune()
