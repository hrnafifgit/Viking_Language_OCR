import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# --- الاعدادات ---
BASE_URL   = "https://www.arild-hauge.com/sweden.htm"
SAVE_DIR   = "images"
HEADERS    = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}
DELAY      = 0.5
TIMEOUT    = 15


def create_save_dir(path):
    os.makedirs(path, exist_ok=True)
    print(f"[OK] Save folder: {os.path.abspath(path)}")


def fetch_page(url):
    try:
        print(f"[->] Loading page: {url}")
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"[X] Page load error: {e}")
        return None


def extract_image_urls(soup, base_url):
    img_tags = soup.find_all("img")
    urls = []
    for img in img_tags:
        src = img.get("src")
        if not src:
            continue
        full_url = urljoin(base_url, src)
        ext = os.path.splitext(urlparse(full_url).path)[1].lower()
        if ext in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"):
            urls.append(full_url)
    seen = set()
    unique_urls = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    print(f"[OK] Found {len(unique_urls)} unique images")
    return unique_urls


def download_image(url, save_dir, index):
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True)
        response.raise_for_status()
        filename = os.path.basename(urlparse(url).path)
        if not filename:
            filename = f"image_{index:04d}.jpg"
        save_path = os.path.join(save_dir, filename)
        if os.path.exists(save_path):
            print(f"  [~] Already exists: {filename}")
            return True
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        size_kb = os.path.getsize(save_path) / 1024
        print(f"  [OK] ({index:03d}) {filename}  --  {size_kb:.1f} KB")
        return True
    except requests.RequestException as e:
        print(f"  [X] ({index:03d}) Failed: {url}  -> {e}")
        return False


def main():
    print("=" * 55)
    print("   Web Scraper -- Arild Hauge Rune Stones Images")
    print("=" * 55)

    create_save_dir(SAVE_DIR)

    soup = fetch_page(BASE_URL)
    if soup is None:
        return

    image_urls = extract_image_urls(soup, BASE_URL)
    if not image_urls:
        print("[!] No images found.")
        return

    print(f"\n[->] Starting download...\n")
    success_count = 0
    fail_count    = 0

    for i, url in enumerate(image_urls, start=1):
        ok = download_image(url, SAVE_DIR, i)
        if ok:
            success_count += 1
        else:
            fail_count += 1
        time.sleep(DELAY)

    print("\n" + "=" * 55)
    print(f"   Download Complete!")
    print(f"   OK : {success_count}")
    print(f"   X  : {fail_count}")
    print(f"   Folder : {os.path.abspath(SAVE_DIR)}")
    print("=" * 55)


if __name__ == "__main__":
    main()
