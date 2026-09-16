"""
================================================================================
  Viking Rune YOLOv8 - Local CPU Fine-Tuning Engine
  - Uses Pre-trained Model (pretrained_bestmodel/best.pt)
  - 2-Stage Curriculum:
      Stage 1: Frozen Backbone (Head Adaptation on real stone textures)
      Stage 2: Unfrozen End-to-End Fine-Tuning (Fine feature refinement)
  - Strict epigraphic rules: fliplr=0.0, flipud=0.0 (preserves rune chirality)
  - Automatic evaluation and final model export
================================================================================
"""

import os
import sys
import argparse
from pathlib import Path
import shutil
import torch
from ultralytics import YOLO

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent
DATASET_YAML = BASE_DIR / "viking_finetune_dataset" / "dataset.yaml"
OUTPUT_RUNS = BASE_DIR / "finetune_local_runs"
FINAL_MASTER_MODEL = BASE_DIR / "viking_master_finetuned_best.pt"

# Candidate weights: prefer verified pretrained model
WEIGHT_CANDIDATES = [
    BASE_DIR / "pretrained_bestmodel" / "best.pt",
    BASE_DIR / "viking_finetune_dataset" / "bestmodel" / "best.pt",
    BASE_DIR / "best.pt"
]

def find_starting_weights():
    for w in WEIGHT_CANDIDATES:
        if w.exists():
            return str(w)
    raise FileNotFoundError("Could not find any pretrained best.pt weights file!")

def main():
    parser = argparse.ArgumentParser(description="Local Viking Rune Fine-Tuning")
    parser.add_argument("--stage1-epochs", type=int, default=15, help="Epochs for Stage 1 (Backbone frozen)")
    parser.add_argument("--stage2-epochs", type=int, default=20, help="Epochs for Stage 2 (Full fine-tune)")
    parser.add_argument("--batch", type=int, default=8, help="Batch size (default 8)")
    parser.add_argument("--imgsz", type=int, default=640, help="Image resolution (default 640)")
    parser.add_argument("--workers", type=int, default=2, help="DataLoader workers (default 2)")
    parser.add_argument("--resume", action="store_true", default=True, help="Resume from last checkpoint if found (default True)")
    parser.add_argument("--no-resume", dest="resume", action="store_false", help="Do not resume, restart from scratch")
    args = parser.parse_args()

    init_weights = find_starting_weights()
    device = "0" if torch.cuda.is_available() else "cpu"
    if device == "cpu":
        torch.set_num_threads(4)
    device_desc = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "Intel CPU (4 OpenMP Threads)"

    print("=" * 75)
    print("🚀 VIKING RUNE LOCAL FINE-TUNING ENGINE")
    print(f"   Starting Model : {init_weights}")
    print(f"   Dataset Config : {DATASET_YAML}")
    print(f"   Hardware       : {device_desc} (device={device})")
    print(f"   Batch Size     : {args.batch}")
    print(f"   Stage 1 Epochs : {args.stage1_epochs} (Backbone Frozen)")
    print(f"   Stage 2 Epochs : {args.stage2_epochs} (Full Fine-Tune)")
    print(f"   Resume Support : {args.resume}")
    print("=" * 75)

    if not DATASET_YAML.exists():
        print(f"❌ Error: {DATASET_YAML} not found! Run package_finetune_dataset.py first.")
        sys.exit(1)

    # ──────────────────────────────────────────────────────────────────────────
    # STAGE 1: Head Adaptation (Frozen Backbone: layers 0..9)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[+] 🟢 STAGE 1: Freezing Backbone layers (Adapting Head to Stone Backgrounds)...")
    stage1_dir = OUTPUT_RUNS / "stage1_frozen"
    stage1_last = stage1_dir / "weights" / "last.pt"
    stage1_csv = stage1_dir / "results.csv"

    stage1_completed = False
    if stage1_csv.exists():
        with open(stage1_csv, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
            num_done = max(0, len(lines) - 1)
            if num_done >= args.stage1_epochs:
                stage1_completed = True
                print(f"✓ Stage 1 already completed ({num_done}/{args.stage1_epochs} epochs). Skipping.")

    if not stage1_completed:
        if args.resume and stage1_last.exists():
            print(f"🔄 Resuming Stage 1 from checkpoint: {stage1_last}")
            model_s1 = YOLO(str(stage1_last))
            model_s1.train(resume=True)
        else:
            model_s1 = YOLO(init_weights)
            model_s1.train(
                data=str(DATASET_YAML),
                epochs=args.stage1_epochs,
                imgsz=args.imgsz,
                batch=args.batch,
                device=device,
                workers=args.workers,
                freeze=10,            # Freeze backbone layers 0-9
                lr0=0.0015,           # Learning rate for detection head
                lrf=0.01,
                fliplr=0.0,           # CRITICAL: Runes are chiral! Never flip horizontally
                flipud=0.0,           # Never flip vertically
                degrees=10.0,         # Slight stone tilt rotation
                scale=0.20,           # Scale variation
                mosaic=0.5,           # Mosaic augmentation
                close_mosaic=5,
                project=str(OUTPUT_RUNS),
                name="stage1_frozen",
                exist_ok=True,
                verbose=True
            )

    stage1_best = OUTPUT_RUNS / "stage1_frozen" / "weights" / "best.pt"
    if not stage1_best.exists():
        stage1_best = OUTPUT_RUNS / "stage1_frozen" / "weights" / "last.pt"

    print(f"\n✓ Stage 1 ready! Checkpoint: {stage1_best}")

    # ──────────────────────────────────────────────────────────────────────────
    # STAGE 2: End-to-End Fine-Tuning (Unfrozen with very low LR)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[+] 🔵 STAGE 2: Unfrozen End-to-End Fine-Tuning (Gentle Adjustment)...")
    stage2_dir = OUTPUT_RUNS / "stage2_unfrozen"
    stage2_last = stage2_dir / "weights" / "last.pt"
    stage2_csv = stage2_dir / "results.csv"

    stage2_completed = False
    if stage2_csv.exists():
        with open(stage2_csv, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
            num_done = max(0, len(lines) - 1)
            if num_done >= args.stage2_epochs:
                stage2_completed = True
                print(f"✓ Stage 2 already completed ({num_done}/{args.stage2_epochs} epochs). Skipping.")

    if not stage2_completed:
        if args.resume and stage2_last.exists():
            print(f"🔄 Resuming Stage 2 from checkpoint: {stage2_last}")
            model_s2 = YOLO(str(stage2_last))
            model_s2.train(resume=True)
        else:
            s2_batch = min(args.batch, 4) if device == "cpu" else args.batch
            model_s2 = YOLO(str(stage1_best))
            model_s2.train(
                data=str(DATASET_YAML),
                epochs=args.stage2_epochs,
                imgsz=args.imgsz,
                batch=s2_batch,
                device=device,
                workers=args.workers,
                freeze=0,             # Unfreeze all layers
                lr0=0.0003,           # Very low learning rate to protect pre-trained features
                lrf=0.01,
                fliplr=0.0,           # CRITICAL: Preserve rune orientation
                flipud=0.0,
                degrees=8.0,
                scale=0.15,
                mosaic=0.3,
                close_mosaic=5,
                project=str(OUTPUT_RUNS),
                name="stage2_unfrozen",
                exist_ok=True,
                verbose=True
            )

    stage2_best = OUTPUT_RUNS / "stage2_unfrozen" / "weights" / "best.pt"
    if not stage2_best.exists():
        stage2_best = OUTPUT_RUNS / "stage2_unfrozen" / "weights" / "last.pt"

    # Export final master model
    shutil.copy2(stage2_best, FINAL_MASTER_MODEL)
    print("\n" + "=" * 75)
    print(f"🏆 SUCCESS! Final Master Model exported to: {FINAL_MASTER_MODEL}")
    print("=" * 75)

    # ──────────────────────────────────────────────────────────────────────────
    # FINAL EVALUATION: Real Stone Validation Metrics
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[+] Running Final Comprehensive Validation...")
    eval_model = YOLO(str(FINAL_MASTER_MODEL))
    val_res = eval_model.val(data=str(DATASET_YAML), imgsz=args.imgsz, verbose=True)

    print("\n" + "=" * 75)
    print("📊 FINAL FINE-TUNED VALIDATION RESULTS:")
    print(f"   Precision (P) : {val_res.box.mp:.4f} ({val_res.box.mp*100:.2f}%)")
    print(f"   Recall (R)    : {val_res.box.mr:.4f} ({val_res.box.mr*100:.2f}%)")
    print(f"   mAP@50        : {val_res.box.map50:.4f} ({val_res.box.map50*100:.2f}%)")
    print(f"   mAP@50-95     : {val_res.box.map:.4f} ({val_res.box.map*100:.2f}%)")
    print("=" * 75)

if __name__ == "__main__":
    main()
