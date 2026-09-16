import os
import sys
import yaml
from pathlib import Path
from ultralytics import YOLO

# Set encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

workspace_dir = Path(r"g:\haroonalafif\universty\level four\project\imageprocessing_Akram\Lab 5")
dataset_dir = workspace_dir / "viking_finetune_dataset"

# Create a local valid yaml file pointing directly to this workspace
temp_yaml = workspace_dir / "temp_val_dataset.yaml"
data = {
    "path": str(dataset_dir).replace("\\", "/"),
    "train": "images/train",
    "val": "images/val",
    "nc": 17,
    "names": [
        "fehu", "uruz", "thurisaz", "ansuz", "raidho", "kaunan", 
        "hagalaz", "naudiz", "isaz", "ar_jera", "sowilo", "tiwaz", 
        "berkanan", "mannaz", "laguz", "yr", "separator"
    ]
}

with open(temp_yaml, "w", encoding="utf-8") as f:
    yaml.dump(data, f)

RUNES_INFO = {
    0:  {"rune": "ᚠ", "latin": "f",   "name": "fehu",      "ar": "فيهو"},
    1:  {"rune": "ᚢ", "latin": "u",   "name": "uruz",      "ar": "أوروز"},
    2:  {"rune": "ᚦ", "latin": "th",  "name": "thurisaz",  "ar": "ثوريساز"},
    3:  {"rune": "ᚬ", "latin": "a/o", "name": "ansuz",     "ar": "أنسوز"},
    4:  {"rune": "ᚱ", "latin": "r",   "name": "raidho",    "ar": "رايدو"},
    5:  {"rune": "ᚴ", "latin": "k",   "name": "kaunan",    "ar": "كاونان"},
    6:  {"rune": "ᚼ", "latin": "h",   "name": "hagalaz",   "ar": "هاغالاز"},
    7:  {"rune": "ᚾ", "latin": "n",   "name": "naudiz",    "ar": "ناوديز"},
    8:  {"rune": "ᛁ", "latin": "i",   "name": "isaz",      "ar": "إيساز"},
    9:  {"rune": "ᛅ", "latin": "a",   "name": "ar_jera",   "ar": "أر / ييرا"},
    10: {"rune": "ᛋ", "latin": "s",   "name": "sowilo",    "ar": "سوفيلو"},
    11: {"rune": "ᛏ", "latin": "t",   "name": "tiwaz",     "ar": "تيفاز"},
    12: {"rune": "ᛒ", "latin": "b",   "name": "berkanan",  "ar": "بركانان"},
    13: {"rune": "ᛉ", "latin": "m",   "name": "mannaz",    "ar": "ماناز"},
    14: {"rune": "ᛚ", "latin": "l",   "name": "laguz",     "ar": "لاغوز"},
    15: {"rune": "ᛦ", "latin": "R/y", "name": "yr",        "ar": "إير"},
    16: {"rune": ":", "latin": ":",   "name": "separator", "ar": "فاصل (نقطتين)"},
}

models_to_check = [
    ("LASTMODEL/best(1).pt", workspace_dir / "LASTMODEL" / "best(1).pt"),
    ("viking_master_epigraphy_v2_best.pt", dataset_dir / "viking_master_epigraphy_v2_best.pt"),
    ("best.pt", workspace_dir / "best.pt")
]

for label, model_file in models_to_check:
    if not model_file.exists():
        continue
    print(f"\n==========================================")
    print(f"EVALUATING: {label} ({model_file.stat().st_size} bytes)")
    print(f"==========================================")
    
    model = YOLO(str(model_file))
    metrics = model.val(
        data=str(temp_yaml),
        imgsz=1024,
        batch=4,
        plots=False,
        verbose=False
    )
    
    print("\nOVERALL METRICS:")
    print(f"Precision (P):  {metrics.box.mp * 100:.2f}%")
    print(f"Recall (R):     {metrics.box.mr * 100:.2f}%")
    print(f"mAP@50:         {metrics.box.map50 * 100:.2f}%")
    print(f"mAP@50-95:      {metrics.box.map * 100:.2f}%")
    
    print("\nPER-CLASS DETAILED BREAKDOWN:")
    print(f"{'ID':<3} | {'Rune':<4} | {'Name':<10} | {'Latin':<6} | {'Precision':<10} | {'Recall':<10} | {'mAP@50':<10} | {'mAP@50-95':<10}")
    print("-" * 80)
    
    p_per_class = metrics.box.p
    r_per_class = metrics.box.r
    map50_per_class = metrics.box.all_ap[:, 0] if hasattr(metrics.box, "all_ap") else metrics.box.ap50
    map_per_class = metrics.box.ap
    
    for i in range(len(model.names)):
        c_name = model.names[i]
        info = RUNES_INFO.get(i, {"rune": "?", "latin": "?", "name": c_name})
        p = p_per_class[i] * 100 if i < len(p_per_class) else 0.0
        r = r_per_class[i] * 100 if i < len(r_per_class) else 0.0
        m50 = map50_per_class[i] * 100 if i < len(map50_per_class) else 0.0
        m = map_per_class[i] * 100 if i < len(map_per_class) else 0.0
        
        print(f"{i:<3} | {info['rune']:<4} | {c_name:<10} | {info['latin']:<6} | {p:>8.2f}% | {r:>8.2f}% | {m50:>8.2f}% | {m:>8.2f}%")
    
    # We only need the primary model
    break

if temp_yaml.exists():
    try:
        temp_yaml.unlink()
    except Exception:
        pass
