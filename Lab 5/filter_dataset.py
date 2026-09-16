import os
import shutil
from pathlib import Path
import zipfile

def run_filter():
    base_dir = Path("FINETUNEIMAGE")
    labels_dir = base_dir / "labels"
    images_dir = base_dir / "images"

    all_ids = sorted([int(f.stem) for f in labels_dir.glob("*.txt") if f.stem.isdigit()])
    print(f"Total files before filtering: {len(all_ids)}")

    kept = []
    deleted = []

    for idx in all_ids:
        lbl_file = labels_dir / f"{idx}.txt"
        img_candidates = list(images_dir.glob(f"{idx}.*"))
        if not img_candidates:
            print(f"Warning: No image found for {idx}")
            continue
        img_file = img_candidates[0]
        
        lines = [l.strip() for l in lbl_file.read_text(encoding="utf-8", errors="ignore").splitlines() if l.strip()]
        rune_count = len(lines)
        
        if rune_count < 5:
            deleted.append({"old_id": idx, "img_name": img_file.name, "rune_count": rune_count})
        else:
            kept.append({"old_id": idx, "img_path": img_file, "lbl_path": lbl_file, "rune_count": rune_count})

    print(f"Kept (>= 5 runes): {len(kept)}")
    print(f"Deleted (< 5 runes): {len(deleted)}")

    temp_dir = Path("FINETUNEIMAGE_TEMP")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    (temp_dir / "images").mkdir(parents=True, exist_ok=True)
    (temp_dir / "labels").mkdir(parents=True, exist_ok=True)

    # Copy classes.txt
    classes_file = base_dir / "classes.txt"
    if classes_file.exists():
        shutil.copy2(classes_file, temp_dir / "classes.txt")

    # Copy kept items with new sequential numbering 1..N
    mapping_lines = ["# FINETUNEIMAGE MAPPING (Filtered for >= 5 Runes)",
                     f"# Total Retained High-Quality Images: {len(kept)}",
                     f"# Total Filtered/Deleted Images (< 5 Runes): {len(deleted)}",
                     "#" + "-" * 50,
                     "NEW_ID\tOLD_ID\tRUNE_COUNT\tFILENAME"]

    for new_idx, item in enumerate(kept, start=1):
        old_img = item["img_path"]
        old_lbl = item["lbl_path"]
        ext = old_img.suffix
        
        new_img_name = f"{new_idx}{ext}"
        new_lbl_name = f"{new_idx}.txt"

        # Copy to subdirs
        shutil.copy2(old_img, temp_dir / "images" / new_img_name)
        shutil.copy2(old_lbl, temp_dir / "labels" / new_lbl_name)

        # Copy flat to root
        shutil.copy2(old_img, temp_dir / new_img_name)
        shutil.copy2(old_lbl, temp_dir / new_lbl_name)

        mapping_lines.append(f"{new_idx}\t{item['old_id']}\t{item['rune_count']}\t{new_img_name}")

    (temp_dir / "MAPPING_INDEX.txt").write_text("\n".join(mapping_lines), encoding="utf-8")

    # Deleted log
    del_lines = ["# DELETED IMAGES LOG (Fewer than 5 Runes in Text File)",
                 f"# Total Deleted: {len(deleted)}",
                 "#" + "-" * 50,
                 "OLD_ID\tRUNE_COUNT\tFILENAME"]
    for d in deleted:
        del_lines.append(f"{d['old_id']}\t{d['rune_count']}\t{d['img_name']}")
    
    (temp_dir / "DELETED_IMAGES_LOG.txt").write_text("\n".join(del_lines), encoding="utf-8")

    # Readme
    readme_content = f"""# FINETUNEIMAGE Dataset (Filtered & Refined)

## Overview
This dataset contains high-quality Viking rune inscription images and their corresponding YOLO annotation text files.
All images have been rigorously filtered to retain **only images with 5 or more runes** (`>= 5 runes`), ensuring maximum training quality and informative annotations.

- **Total Retained Images & Labels:** {len(kept)} (Numbered sequentially from 1 to {len(kept)})
- **Removed Sparse Images (< 5 runes):** {len(deleted)}
- **Format:**
  - Standard YOLO format: `FINETUNEIMAGE/images/` and `FINETUNEIMAGE/labels/`
  - Flat access: Direct copies `{1}..{len(kept)}.png/.jpg` and `.txt` are also provided in the root folder.
  - Mapping: See `MAPPING_INDEX.txt` for previous ID mapping.
  - Deleted log: See `DELETED_IMAGES_LOG.txt` for details on removed files.
"""
    (temp_dir / "README_DATASET.md").write_text(readme_content, encoding="utf-8")

    print("Staged temporary clean dataset successfully.")

    # Now replace FINETUNEIMAGE
    print("Replacing FINETUNEIMAGE...")
    shutil.rmtree(base_dir)
    shutil.copytree(temp_dir, base_dir)

    # Mirror to project_requirment/FINETUNEIMAGE
    pr_dest = Path("project_requirment/FINETUNEIMAGE")
    print(f"Mirroring to {pr_dest}...")
    if pr_dest.exists():
        shutil.rmtree(pr_dest)
    shutil.copytree(temp_dir, pr_dest)

    # Clean up temp
    shutil.rmtree(temp_dir)
    print("FINETUNEIMAGE and project_requirment/FINETUNEIMAGE updated successfully!")

    # Now rebuild zip archive
    zip_path = Path("Viking_Epigraphy_Project_Akram_Lab5.zip")
    src_folder = Path("project_requirment")
    print(f"Rebuilding submission zip archive: {zip_path} ...")
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in src_folder.rglob("*"):
            if file.name.startswith("~$") or file.suffix in [".tmp", ".log"]:
                continue
            if file.is_file():
                arcname = file.relative_to(src_folder.parent)
                zf.write(file, arcname)

    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"Zip successfully created: {zip_path.name} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    run_filter()
