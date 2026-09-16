"""
================================================================================
  Clipboard Auto-Saver: Instant Screenshot to Folder
  - Monitors Windows Clipboard for 'Win + Shift + S' snipping
  - Saves new snips directly to 'imagesfintune/' numbered sequentially
  - Plays a subtle audio chime so you know it was saved!
================================================================================
"""

import os
import sys
import time
import hashlib
from pathlib import Path
from PIL import Image, ImageGrab
import winsound

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TARGET_DIR = Path(__file__).resolve().parent / "imagesfintune"
TARGET_DIR.mkdir(parents=True, exist_ok=True)

def get_next_index():
    nums = []
    for f in TARGET_DIR.iterdir():
        if f.is_file() and f.stem.isdigit():
            nums.append(int(f.stem))
    return max(nums, default=0) + 1

def image_hash(img: Image.Image) -> str:
    # Quick downsampled hash for comparison
    thumb = img.resize((32, 32)).convert("L")
    return hashlib.md5(thumb.tobytes()).hexdigest()

def main():
    print("=" * 65)
    print(" 📸 Clipboard Auto-Saver Active!")
    print(f" Target Folder: {TARGET_DIR}")
    print(" Instructions : Just press [ Win + Shift + S ] and snip any region.")
    print("                The image will automatically save to the folder!")
    print("=" * 65)

    last_hash = None
    
    # Check if there's an existing image already in clipboard to avoid saving stale data
    current = ImageGrab.grabclipboard()
    if isinstance(current, Image.Image):
        last_hash = image_hash(current)

    print("\nWaiting for your snips... (Press Ctrl+C to stop at any time)\n")

    while True:
        try:
            content = ImageGrab.grabclipboard()
            if isinstance(content, Image.Image):
                cur_hash = image_hash(content)
                if cur_hash != last_hash:
                    idx = get_next_index()
                    save_path = TARGET_DIR / f"{idx}.png"
                    content.save(save_path, "PNG")
                    last_hash = cur_hash
                    
                    w, h = content.size
                    print(f"✓ [{time.strftime('%H:%M:%S')}] Saved snippet: {save_path.name} ({w}x{h} px)")
                    # Beep for audio feedback
                    try:
                        winsound.MessageBeep(winsound.MB_OK)
                    except:
                        pass

            time.sleep(0.4)
        except KeyboardInterrupt:
            print("\nStopped.")
            break
        except Exception as e:
            time.sleep(0.5)

if __name__ == "__main__":
    main()
