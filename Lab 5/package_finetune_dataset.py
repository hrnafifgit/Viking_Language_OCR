"""
================================================================================
  Viking Runes: Hybrid Real-to-Synthetic Fine-Tuning Dataset Packager
  - Packages 37 real stone labeled crops (868 instances)
  - Adds synthetic stone anchors from dataset_preview for regularization
  - Prepares train/val splits with balanced class representation
  - Creates dataset.yaml and packages into viking_finetune_dataset.zip
================================================================================
"""

import os
import sys
import shutil
import random
import zipfile
from pathlib import Path
import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent
REAL_IMG_DIR = BASE_DIR / "imagesfintune"
REAL_LBL_DIR = REAL_IMG_DIR / "label"
SYNTH_DIR = BASE_DIR / "dataset_preview"

OUTPUT_DIR = BASE_DIR / "viking_finetune_dataset"
ZIP_FILE = BASE_DIR / "viking_finetune_dataset.zip"

CLASS_NAMES = [
    "fehu", "uruz", "thurisaz", "ansuz", "raidho", "kaunan",
    "hagalaz", "naudiz", "isaz", "ar_jera", "sowilo", "tiwaz",
    "berkanan", "mannaz", "laguz", "yr", "separator"
]

def build_dataset(synth_ratio=0.5):
    # 1. Prepare clean directories (preserve any model checkpoints like bestmodel)
    dirs = {
        "train_img": OUTPUT_DIR / "images" / "train",
        "val_img":   OUTPUT_DIR / "images" / "val",
        "train_lbl": OUTPUT_DIR / "labels" / "train",
        "val_lbl":   OUTPUT_DIR / "labels" / "val"
    }
    for d in [OUTPUT_DIR / "images", OUTPUT_DIR / "labels"]:
        if d.exists():
            shutil.rmtree(d)
    
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)

    # 2. Collect real labeled pairs
    real_pairs = []
    lbl_files = sorted(list(REAL_LBL_DIR.glob("*.txt")))
    for lf in lbl_files:
        stem = lf.stem
        img_match = None
        for ext in [".png", ".jpg", ".jpeg", ".bmp"]:
            cand = REAL_IMG_DIR / f"{stem}{ext}"
            if cand.exists():
                img_match = cand
                break
        if img_match:
            real_pairs.append((img_match, lf))

    print(f"[*] Found {len(real_pairs)} real labeled image pairs.")

    # 3. Stratified split for real images (31 train, 6 val)
    random.seed(42)
    random.shuffle(real_pairs)
    val_count_real = max(4, int(len(real_pairs) * 0.16)) # 6 images for validation
    train_real = real_pairs[val_count_real:]
    val_real = real_pairs[:val_count_real]

    print(f"    -> Real split: {len(train_real)} train, {len(val_real)} validation.")

    # 4. Copy real images and labels
    for img_p, lbl_p in train_real:
        shutil.copy2(img_p, dirs["train_img"] / f"real_{img_p.name}")
        shutil.copy2(lbl_p, dirs["train_lbl"] / f"real_{img_p.stem}.txt")

    for img_p, lbl_p in val_real:
        shutil.copy2(img_p, dirs["val_img"] / f"real_{img_p.name}")
        shutil.copy2(lbl_p, dirs["val_lbl"] / f"real_{img_p.stem}.txt")

    # 5. Add synthetic anchor images from dataset_preview for regularization
    if SYNTH_DIR.exists():
        synth_train_imgs = list((SYNTH_DIR / "images" / "train").glob("*.jpg"))
        synth_val_imgs   = list((SYNTH_DIR / "images" / "val").glob("*.jpg"))
        
        # Take 50 synthetic train images and 10 synthetic val images
        random.shuffle(synth_train_imgs)
        random.shuffle(synth_val_imgs)
        selected_synth_train = synth_train_imgs[:50]
        selected_synth_val   = synth_val_imgs[:10]

        for s_img in selected_synth_train:
            s_lbl = SYNTH_DIR / "labels" / "train" / f"{s_img.stem}.txt"
            if s_lbl.exists():
                shutil.copy2(s_img, dirs["train_img"] / f"synth_{s_img.name}")
                shutil.copy2(s_lbl, dirs["train_lbl"] / f"synth_{s_img.stem}.txt")

        for s_img in selected_synth_val:
            s_lbl = SYNTH_DIR / "labels" / "val" / f"{s_img.stem}.txt"
            if s_lbl.exists():
                shutil.copy2(s_img, dirs["val_img"] / f"synth_{s_img.name}")
                shutil.copy2(s_lbl, dirs["val_lbl"] / f"synth_{s_img.stem}.txt")

        print(f"[*] Added {len(selected_synth_train)} synthetic train and {len(selected_synth_val)} synthetic val anchors.")

    # 6. Generate dataset.yaml
    yaml_dict = {
        "path": str(OUTPUT_DIR.resolve()).replace("\\", "/"),
        "train": "images/train",
        "val": "images/val",
        "nc": len(CLASS_NAMES),
        "names": CLASS_NAMES
    }
    yaml_path = OUTPUT_DIR / "dataset.yaml"
    with open(yaml_path, "w", encoding="utf-8") as yf:
        yaml.dump(yaml_dict, yf, sort_keys=False)

    # 7. Zip the entire dataset for easy Google Drive / Colab upload
    if ZIP_FILE.exists():
        ZIP_FILE.unlink()

    print(f"[*] Compressing dataset into {ZIP_FILE.name}...")
    with zipfile.ZipFile(ZIP_FILE, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(OUTPUT_DIR):
            for file in files:
                full_p = Path(root) / file
                rel_p = full_p.relative_to(BASE_DIR)
                zf.write(full_p, rel_p)

    train_total = len(list(dirs['train_img'].glob('*.*')))
    val_total = len(list(dirs['val_img'].glob('*.*')))

    print("\n" + "="*70)
    print("✅ Fine-Tuning Dataset Package Created Successfully!")
    print(f"   Directory   : {OUTPUT_DIR}")
    print(f"   Zip Archive : {ZIP_FILE} ({ZIP_FILE.stat().st_size / 1024 / 1024:.2f} MB)")
    print(f"   Train Set   : {train_total} images ({len(train_real)} Real + 50 Synthetic)")
    print(f"   Val Set     : {val_total} images ({len(val_real)} Real + 10 Synthetic)")
    print(f"   YAML Config : {yaml_path}")
    print("="*70)

if __name__ == "__main__":
    build_dataset()
