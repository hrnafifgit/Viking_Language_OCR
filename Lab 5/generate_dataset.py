"""
================================================================================
  ᚱ Viking Rune YOLO Dataset Generator — Authentic Younger Futhark (Framed Bands)
  - 100% Strict Younger Futhark (16 Runes + Separator)
  - ELIMINATED all Elder Futhark anomalies (NO "N" or "M" double staves)
  - Horizontal & Vertical Carved Framing Bands (as seen on classical rune monuments)
  - Upright Staves with natural subtle hand-tilt (-5° to +5°)
  - 3D Realistic Chisel Physics: Dual-tone engraved relief (Shadow + Highlight)
  - 4 Authentic Rock Textures: Granite, Limestone, Sandstone, Weathered Slate
  - 17 Classes: 16 Younger Futhark Runes + 1 Separator
================================================================================
"""

import os
import sys
import random
import math
import argparse
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ──────────────────────────────────────────────────────────────────────────────
# Strict Younger Futhark Viking Runes (Canonical 16 Runes + Separator)
# ──────────────────────────────────────────────────────────────────────────────
RUNES = [
    {
        "id": 0, "name": "fehu", "latin": "F",  # ᚠ
        "variants": [
            [[(0.35, 0.10), (0.35, 0.90)], [(0.35, 0.45), (0.52, 0.35), (0.75, 0.20)], [(0.35, 0.70), (0.52, 0.60), (0.75, 0.45)]],
            [[(0.35, 0.10), (0.35, 0.90)], [(0.35, 0.42), (0.75, 0.18)], [(0.35, 0.68), (0.75, 0.42)]]
        ]
    },
    {
        "id": 1, "name": "uruz", "latin": "U",  # ᚢ (Inverted arch ∩ matching classes.txt)
        "variants": [
            [[(0.30, 0.32), (0.30, 0.90)], [(0.30, 0.32), (0.34, 0.18), (0.50, 0.12), (0.66, 0.18), (0.70, 0.32)], [(0.70, 0.32), (0.70, 0.90)]],
            [[(0.28, 0.30), (0.28, 0.92)], [(0.28, 0.30), (0.50, 0.10), (0.72, 0.30)], [(0.72, 0.30), (0.72, 0.92)]]
        ]
    },
    {
        "id": 2, "name": "thurisaz", "latin": "Th",  # ᚦ (Stave with D-shaped loop)
        "variants": [
            [[(0.35, 0.10), (0.35, 0.90)], [(0.35, 0.28), (0.55, 0.28), (0.72, 0.38), (0.72, 0.58), (0.55, 0.68), (0.35, 0.68)]],
            [[(0.35, 0.10), (0.35, 0.90)], [(0.35, 0.25), (0.75, 0.48), (0.35, 0.72)]]
        ]
    },
    {
        "id": 3, "name": "ansuz", "latin": "A",  # ᚬ (Stave with two crossing downward branches)
        "variants": [
            [[(0.50, 0.10), (0.50, 0.90)], [(0.25, 0.28), (0.75, 0.40)], [(0.25, 0.48), (0.75, 0.60)]],
            [[(0.50, 0.10), (0.50, 0.90)], [(0.22, 0.26), (0.78, 0.38)], [(0.22, 0.46), (0.78, 0.58)]]
        ]
    },
    {
        "id": 4, "name": "raidho", "latin": "R",  # ᚱ (Stave with loop and leg)
        "variants": [
            [[(0.35, 0.10), (0.35, 0.90)], [(0.35, 0.14), (0.55, 0.15), (0.70, 0.24), (0.70, 0.38), (0.55, 0.46), (0.35, 0.48)], [(0.35, 0.48), (0.70, 0.90)]],
            [[(0.35, 0.10), (0.35, 0.90)], [(0.35, 0.12), (0.72, 0.28), (0.35, 0.48)], [(0.35, 0.48), (0.72, 0.90)]]
        ]
    },
    {
        "id": 5, "name": "kaunan", "latin": "K",  # ᚴ (Stave with upward branch)
        "variants": [
            [[(0.35, 0.10), (0.35, 0.90)], [(0.35, 0.50), (0.55, 0.38), (0.75, 0.20)]],
            [[(0.35, 0.10), (0.35, 0.90)], [(0.35, 0.48), (0.75, 0.18)]]
        ]
    },
    {
        "id": 6, "name": "hagalaz", "latin": "H",  # ᚼ (Stave crossed by asterisk/cross)
        "variants": [
            [[(0.50, 0.10), (0.50, 0.90)], [(0.22, 0.35), (0.78, 0.65)], [(0.22, 0.65), (0.78, 0.35)]],
            [[(0.50, 0.10), (0.50, 0.90)], [(0.20, 0.38), (0.80, 0.62)], [(0.20, 0.62), (0.80, 0.38)]]
        ]
    },
    {
        "id": 7, "name": "naudiz", "latin": "N",  # ᚾ (Stave with crossing diagonal)
        "variants": [
            [[(0.50, 0.10), (0.50, 0.90)], [(0.25, 0.38), (0.75, 0.62)]],
            [[(0.50, 0.10), (0.50, 0.90)], [(0.22, 0.40), (0.78, 0.60)]]
        ]
    },
    {
        "id": 8, "name": "isaz", "latin": "I",  # ᛁ (Single vertical stave)
        "variants": [
            [[(0.50, 0.10), (0.50, 0.90)]],
            [[(0.48, 0.10), (0.48, 0.90)]]
        ]
    },
    {
        "id": 9, "name": "ar_jera", "latin": "A_J",  # ᛅ (Stave crossed by upward diagonal)
        "variants": [
            [[(0.50, 0.10), (0.50, 0.90)], [(0.25, 0.62), (0.75, 0.38)]],
            [[(0.50, 0.10), (0.50, 0.90)], [(0.22, 0.60), (0.78, 0.40)]]
        ]
    },
    {
        "id": 10, "name": "sowilo", "latin": "S",  # ᛋ (Step shape matching classes.txt exactly: top vertical, middle horizontal, bottom vertical)
        "variants": [
            [[(0.35, 0.12), (0.35, 0.48), (0.65, 0.48), (0.65, 0.88)]],
            [[(0.32, 0.14), (0.32, 0.50), (0.68, 0.50), (0.68, 0.86)]]
        ]
    },
    {
        "id": 11, "name": "tiwaz", "latin": "T",  # ᛏ (Arrowhead pointing up)
        "variants": [
            [[(0.50, 0.10), (0.50, 0.90)], [(0.25, 0.35), (0.50, 0.10), (0.75, 0.35)]],
            [[(0.50, 0.10), (0.50, 0.90)], [(0.20, 0.32), (0.50, 0.10), (0.80, 0.32)]]
        ]
    },
    {
        "id": 12, "name": "berkanan", "latin": "B",  # ᛒ (Stave with double B-lobes)
        "variants": [
            [[(0.35, 0.10), (0.35, 0.90)], [(0.35, 0.14), (0.55, 0.15), (0.70, 0.24), (0.70, 0.38), (0.55, 0.46), (0.35, 0.48)], [(0.35, 0.48), (0.55, 0.50), (0.70, 0.60), (0.70, 0.74), (0.55, 0.84), (0.35, 0.86)]],
            [[(0.35, 0.10), (0.35, 0.90)], [(0.35, 0.12), (0.72, 0.30), (0.35, 0.48)], [(0.35, 0.48), (0.72, 0.68), (0.35, 0.88)]]
        ]
    },
    {
        "id": 13, "name": "mannaz", "latin": "M",  # ᛉ (Stave with two upward branches)
        "variants": [
            [[(0.50, 0.10), (0.50, 0.90)], [(0.20, 0.12), (0.50, 0.42)], [(0.80, 0.12), (0.50, 0.42)]],
            [[(0.50, 0.10), (0.50, 0.90)], [(0.18, 0.10), (0.50, 0.40)], [(0.82, 0.10), (0.50, 0.40)]]
        ]
    },
    {
        "id": 14, "name": "laguz", "latin": "L",  # ᛚ (Stave with downward branch)
        "variants": [
            [[(0.40, 0.10), (0.40, 0.90)], [(0.40, 0.10), (0.70, 0.35)]],
            [[(0.38, 0.10), (0.38, 0.90)], [(0.38, 0.10), (0.72, 0.38)]]
        ]
    },
    {
        "id": 15, "name": "yr", "latin": "Y",  # ᛦ (Stave with two downward branches)
        "variants": [
            [[(0.50, 0.10), (0.50, 0.90)], [(0.20, 0.88), (0.50, 0.58)], [(0.80, 0.88), (0.50, 0.58)]],
            [[(0.50, 0.10), (0.50, 0.90)], [(0.18, 0.90), (0.50, 0.60)], [(0.82, 0.90), (0.50, 0.60)]]
        ]
    },
]

SEPARATOR_DEF = {
    "id": 16,
    "name": "separator",
    "types": ["colon", "cross", "single_dot"]
}

CLASS_NAMES = [r["name"] for r in RUNES] + [SEPARATOR_DEF["name"]]


# ──────────────────────────────────────────────────────────────────────────────
# Clean Geological Texture Synthesis (Noise-Free, Clean Data Mining Standards)
# ──────────────────────────────────────────────────────────────────────────────
class BalancedRuneSampler:
    """Guarantees 100% balanced stratified representation across all 16 rune classes."""
    def __init__(self, runes):
        self.runes = runes
        self.n = len(runes)
        self.pool = []
        self._refill()

    def _refill(self):
        self.pool = list(range(self.n))
        random.shuffle(self.pool)

    def next_rune(self):
        if not self.pool:
            self._refill()
        return self.runes[self.pool.pop()]

GLOBAL_SAMPLER = BalancedRuneSampler(RUNES)


def generate_stone_texture(w=640, h=640, rock_type=None):
    if rock_type is None:
        rock_type = random.choice(["granite", "sandstone", "limestone", "slate"])

    if rock_type == "granite":
        base_rgb = np.array([160.0, 155.0, 150.0], dtype=np.float32)
        tint = np.array([random.uniform(-8, 12), random.uniform(-4, 4), random.uniform(-12, -2)])
    elif rock_type == "sandstone":
        base_rgb = np.array([180.0, 160.0, 130.0], dtype=np.float32)
        tint = np.array([random.uniform(5, 20), random.uniform(0, 10), random.uniform(-18, -5)])
    elif rock_type == "limestone":
        base_rgb = np.array([195.0, 192.0, 185.0], dtype=np.float32)
        tint = np.array([random.uniform(-4, 8), random.uniform(-4, 4), random.uniform(-8, 0)])
    else:  # slate
        base_rgb = np.array([90.0, 95.0, 100.0], dtype=np.float32)
        tint = np.array([random.uniform(-8, 4), random.uniform(-4, 4), random.uniform(0, 12)])

    gx = np.linspace(random.uniform(0.94, 1.0), random.uniform(1.0, 1.06), w)[None, :]
    gy = np.linspace(random.uniform(0.94, 1.0), random.uniform(1.0, 1.06), h)[:, None]
    lighting = gy * gx

    c_grid = np.random.uniform(0.88, 1.12, (h // 20 + 1, w // 20 + 1)).astype(np.float32)
    c_map = np.array(
        Image.fromarray((c_grid * 128).astype(np.uint8)).resize((w, h), Image.BICUBIC),
        dtype=np.float32
    ) / 128.0

    f_grid = np.random.uniform(0.94, 1.06, (h // 6 + 1, w // 6 + 1)).astype(np.float32)
    f_map = np.array(
        Image.fromarray((f_grid * 128).astype(np.uint8)).resize((w, h), Image.BILINEAR),
        dtype=np.float32
    ) / 128.0

    color_base = (base_rgb + tint)[None, None, :]
    surface = color_base * (c_map[:, :, None] * 0.70 + f_map[:, :, None] * 0.30) * lighting[:, :, None]
    surface = np.clip(surface, 25, 245).astype(np.uint8)

    img = Image.fromarray(surface)
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    return img


# ──────────────────────────────────────────────────────────────────────────────
# 3D Chisel Physics, Stroke Jitter & Transformation
# ──────────────────────────────────────────────────────────────────────────────
def transform_point(nx, ny, cx, cy, size, angle_deg, shear_x=0.0):
    lx = (nx - 0.5) * size
    ly = (ny - 0.5) * size
    # Subtle shear / italic slant (ميلان الحرف الطبيعي)
    lx += ly * shear_x
    rad = math.radians(angle_deg)
    ca, sa = math.cos(rad), math.sin(rad)
    return (cx + lx * ca - ly * sa, cy + lx * sa + ly * ca)


def jitter_stroke_points(pts, jitter_amp=1.6, step_len=14):
    """Subdivides straight segments and introduces subtle chisel irregularity (تشويه الحفر اليدوي)."""
    out = []
    for i in range(len(pts) - 1):
        p1 = pts[i]
        p2 = pts[i + 1]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        dist = math.hypot(dx, dy)
        steps = max(2, int(dist / step_len))
        if dist > 0:
            ux, uy = dx / dist, dy / dist
            px, py = -uy, ux
        else:
            px, py = 0, 0

        if i == 0:
            out.append(p1)
        for s in range(1, steps):
            t = s / float(steps)
            bx = p1[0] + dx * t
            by = p1[1] + dy * t
            offset = random.uniform(-jitter_amp, jitter_amp)
            out.append((bx + px * offset, by + py * offset))
        out.append(p2)
    return out


def draw_carved_framing_line(draw, p1, p2, color, line_w=2):
    """Draws incised parallel framing lines with subtle stone surface waviness."""
    pts = jitter_stroke_points([p1, p2], jitter_amp=1.2, step_len=24)
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill=color, width=line_w)


def render_carved_rune(draw, rune_def, cx, cy, size, angle_deg, line_w, base_dark, light_dir=(1.2, -1.2)):
    strokes = random.choice(rune_def["variants"])
    shear_x = random.uniform(-0.14, 0.14)
    all_pts = []

    hx, hy = light_dir[0] * 1.5, light_dir[1] * 1.5
    high_c = (min(255, base_dark[0] + 75), min(255, base_dark[1] + 75), min(255, base_dark[2] + 70))
    groove_c = (max(0, base_dark[0] - 65), max(0, base_dark[1] - 65), max(0, base_dark[2] - 65))

    # Highlight bevel edge
    for stroke in strokes:
        raw_pts = [transform_point(p[0], p[1], cx - hx, cy - hy, size, angle_deg, shear_x) for p in stroke]
        pts = jitter_stroke_points(raw_pts, jitter_amp=1.2)
        all_pts.extend(pts)
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i + 1]], fill=high_c, width=line_w + 1)

    # Shadowed core groove with subtle chisel thickness variation
    for stroke in strokes:
        raw_pts = [transform_point(p[0], p[1], cx, cy, size, angle_deg, shear_x) for p in stroke]
        pts = jitter_stroke_points(raw_pts, jitter_amp=1.6)
        all_pts.extend(pts)
        for i in range(len(pts) - 1):
            lw_var = max(2, line_w + random.choice([-1, 0, 0, 1]))
            draw.line([pts[i], pts[i + 1]], fill=groove_c, width=lw_var)
            r = max(1, lw_var // 2)
            draw.ellipse([pts[i][0] - r, pts[i][1] - r, pts[i][0] + r, pts[i][1] + r], fill=groove_c)
        r = max(1, line_w // 2)
        draw.ellipse([pts[-1][0] - r, pts[-1][1] - r, pts[-1][0] + r, pts[-1][1] + r], fill=groove_c)

    xs = [p[0] for p in all_pts]
    ys = [p[1] for p in all_pts]
    pad = line_w + 3
    xmin = max(0, min(xs) - pad)
    ymin = max(0, min(ys) - pad)
    xmax = min(640, max(xs) + pad)
    ymax = min(640, max(ys) + pad)

    return (xmin, ymin, xmax, ymax)


def render_carved_separator(draw, cx, cy, size, angle_deg, line_w, base_dark, sep_type=None):
    if sep_type is None:
        sep_type = random.choice(SEPARATOR_DEF["types"])

    groove_c = (max(0, base_dark[0] - 65), max(0, base_dark[1] - 65), max(0, base_dark[2] - 65))
    high_c = (min(255, base_dark[0] + 70), min(255, base_dark[1] + 70), min(255, base_dark[2] + 70))
    dot_r = max(2, line_w)
    shear_x = random.uniform(-0.10, 0.10)
    all_pts = []

    def T(lx, ly):
        return transform_point(lx / size + 0.5, ly / size + 0.5, cx, cy, size, angle_deg, shear_x)

    if sep_type == "colon":
        p1 = T(0, -size * 0.22)
        p2 = T(0, size * 0.22)
        for p in [p1, p2]:
            all_pts.append(p)
            draw.ellipse([p[0] - dot_r - 1, p[1] - dot_r - 1, p[0] + dot_r + 1, p[1] + dot_r + 1], fill=high_c)
            draw.ellipse([p[0] - dot_r, p[1] - dot_r, p[0] + dot_r, p[1] + dot_r], fill=groove_c)
    elif sep_type == "single_dot":
        all_pts.append((cx, cy))
        draw.ellipse([cx - dot_r - 1, cy - dot_r - 1, cx + dot_r + 1, cy + dot_r + 1], fill=high_c)
        draw.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r], fill=groove_c)
    else:  # cross
        s = size * 0.22
        pts = [T(0, -s), T(0, s), T(-s, 0), T(s, 0)]
        all_pts.extend(pts)
        draw.line([pts[0], pts[1]], fill=groove_c, width=line_w)
        draw.line([pts[2], pts[3]], fill=groove_c, width=line_w)

    xs = [p[0] for p in all_pts]
    ys = [p[1] for p in all_pts]
    pad = dot_r + line_w + 3
    return (max(0, min(xs) - pad), max(0, min(ys) - pad), min(640, max(xs) + pad), min(640, max(ys) + pad))


def bbox_to_yolo(xmin, ymin, xmax, ymax, img_w=640, img_h=640):
    bw = (xmax - xmin) / img_w
    bh = (ymax - ymin) / img_h
    bx = (xmin + xmax) / (2.0 * img_w)
    by = (ymin + ymax) / (2.0 * img_h)
    return max(0.001, min(0.999, bx)), max(0.001, min(0.999, by)), max(0.01, min(0.99, bw)), max(0.01, min(0.99, bh))


# ──────────────────────────────────────────────────────────────────────────────
# Primary Layout: Framed Horizontal / Slanted Stone Inscription Band (مع ميلان وتشويه)
# ──────────────────────────────────────────────────────────────────────────────
def generate_horizontal_stone(fixed_class_id=None, img_size=640):
    img = generate_stone_texture(img_size, img_size)
    draw = ImageDraw.Draw(img)
    labels = []

    # 1 to 3 text rows
    num_rows = random.randint(1, 3)
    row_height = random.randint(60, 85)
    start_y = random.randint(90, max(100, img_size - (num_rows * row_height) - 90))

    # Natural band tilt (الميلان عبر سطح الحجر: -12 إلى +12 درجة)
    band_angle = random.uniform(-12.0, 12.0)
    rad = math.radians(band_angle)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    tan_a = math.tan(rad)

    base_dark = (random.randint(55, 90), random.randint(55, 90), random.randint(55, 90))
    lw = random.randint(3, 5)

    cx_mid = img_size / 2.0
    x_left = 15.0
    x_right = img_size - 15.0

    for r_idx in range(num_rows):
        y_center = start_y + r_idx * (row_height + random.randint(28, 42))
        rune_size = row_height - random.randint(8, 14)
        half_h = row_height / 2.0

        # Incised parallel framing bands tilted with the stone angle
        y_mid_left = y_center + (x_left - cx_mid) * tan_a
        y_mid_right = y_center + (x_right - cx_mid) * tan_a

        top_p1 = (x_left, y_mid_left - half_h / cos_a)
        top_p2 = (x_right, y_mid_right - half_h / cos_a)
        bot_p1 = (x_left, y_mid_left + half_h / cos_a)
        bot_p2 = (x_right, y_mid_right + half_h / cos_a)

        band_c = (max(0, base_dark[0] - 25), max(0, base_dark[1] - 25), max(0, base_dark[2] - 25))
        draw_carved_framing_line(draw, top_p1, top_p2, band_c, line_w=2)
        draw_carved_framing_line(draw, bot_p1, bot_p2, band_c, line_w=2)

        # Trace runes along the tilted band baseline
        t_curr = 45.0
        max_t = (img_size - 85.0) / max(0.2, abs(cos_a))
        runes_since_sep = 0

        while t_curr < max_t:
            rcx = cx_mid + (t_curr - (img_size / 2.0)) * cos_a
            rcy = y_center + (t_curr - (img_size / 2.0)) * sin_a

            if rcx < 35 or rcx > img_size - 35 or rcy < 35 or rcy > img_size - 35:
                t_curr += rune_size * 0.75
                continue

            # Individual rune tilt (ميلان متناسق مع السطر مع انحراف يدوي طفيف)
            rune_angle = band_angle + random.uniform(-6.0, 6.0)

            if fixed_class_id == 16 or (fixed_class_id is None and runes_since_sep >= random.randint(3, 5) and random.random() < 0.85):
                xmin, ymin, xmax, ymax = render_carved_separator(draw, rcx, rcy, rune_size, rune_angle, lw, base_dark)
                bx, by, bw, bh = bbox_to_yolo(xmin, ymin, xmax, ymax, img_size, img_size)
                labels.append(f"16 {bx:.6f} {by:.6f} {bw:.6f} {bh:.6f}")
                t_curr += int(rune_size * random.uniform(0.70, 0.82))
                runes_since_sep = 0
            else:
                rune = GLOBAL_SAMPLER.next_rune() if fixed_class_id is None else (RUNES[16] if fixed_class_id == 16 else RUNES[fixed_class_id])
                xmin, ymin, xmax, ymax = render_carved_rune(draw, rune, rcx, rcy, rune_size, rune_angle, lw, base_dark)
                bx, by, bw, bh = bbox_to_yolo(xmin, ymin, xmax, ymax, img_size, img_size)
                labels.append(f"{rune['id']} {bx:.6f} {by:.6f} {bw:.6f} {bh:.6f}")
                t_curr += int(rune_size * random.uniform(0.92, 1.08))
                runes_since_sep += 1

    return apply_weathering(img), labels


# ──────────────────────────────────────────────────────────────────────────────
# Secondary Layout: Framed Vertical Column Staves (مع ميلان طفيف)
# ──────────────────────────────────────────────────────────────────────────────
def generate_vertical_column_stone(fixed_class_id=None, img_size=640):
    img = generate_stone_texture(img_size, img_size)
    draw = ImageDraw.Draw(img)
    labels = []

    num_cols = random.randint(1, 2)
    col_width = random.randint(70, 95)
    start_x = random.randint(80, max(90, img_size - (num_cols * col_width) - 80))

    # Natural vertical column slant (-8 to +8 degrees)
    col_angle = random.uniform(-8.0, 8.0)
    rad = math.radians(col_angle)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)

    base_dark = (random.randint(55, 90), random.randint(55, 90), random.randint(55, 90))
    lw = random.randint(3, 5)

    for c_idx in range(num_cols):
        x_center = start_x + c_idx * (col_width + random.randint(30, 50))
        rune_size = col_width - random.randint(12, 20)
        half_w = col_width / 2.0

        # Slanted framing ribbons
        bx1_top = (x_center - half_w - sin_a * 280, 25)
        bx1_bot = (x_center - half_w + sin_a * 280, img_size - 25)
        bx2_top = (x_center + half_w - sin_a * 280, 25)
        bx2_bot = (x_center + half_w + sin_a * 280, img_size - 25)

        band_c = (max(0, base_dark[0] - 25), max(0, base_dark[1] - 25), max(0, base_dark[2] - 25))
        draw_carved_framing_line(draw, bx1_top, bx1_bot, band_c, line_w=2)
        draw_carved_framing_line(draw, bx2_top, bx2_bot, band_c, line_w=2)

        y_curr = random.randint(50, 75)
        runes_since_sep = 0

        while y_curr < img_size - 60:
            rcx = x_center + (y_curr - img_size / 2.0) * sin_a
            rcy = y_curr
            rune_angle = col_angle + random.uniform(-5.0, 5.0)

            if fixed_class_id == 16 or (fixed_class_id is None and runes_since_sep >= random.randint(3, 5) and random.random() < 0.85):
                xmin, ymin, xmax, ymax = render_carved_separator(draw, rcx, rcy, rune_size, rune_angle, lw, base_dark)
                bx, by, bw, bh = bbox_to_yolo(xmin, ymin, xmax, ymax, img_size, img_size)
                labels.append(f"16 {bx:.6f} {by:.6f} {bw:.6f} {bh:.6f}")
                y_curr += int(rune_size * random.uniform(0.85, 1.05))
                runes_since_sep = 0
            else:
                rune = GLOBAL_SAMPLER.next_rune() if fixed_class_id is None else (RUNES[16] if fixed_class_id == 16 else RUNES[fixed_class_id])
                xmin, ymin, xmax, ymax = render_carved_rune(draw, rune, rcx, rcy, rune_size, rune_angle, lw, base_dark)
                bx, by, bw, bh = bbox_to_yolo(xmin, ymin, xmax, ymax, img_size, img_size)
                labels.append(f"{rune['id']} {bx:.6f} {by:.6f} {bw:.6f} {bh:.6f}")
                y_curr += int(rune_size * random.uniform(1.25, 1.45))
                runes_since_sep += 1

    return apply_weathering(img), labels


# ──────────────────────────────────────────────────────────────────────────────
# Master Image Dispatcher: Prioritizes Framed Bands
# ──────────────────────────────────────────────────────────────────────────────
def generate_sample(fixed_class_id=None, img_size=640):
    if random.random() < 0.85:
        return generate_horizontal_stone(fixed_class_id, img_size)
    else:
        return generate_vertical_column_stone(fixed_class_id, img_size)


# ──────────────────────────────────────────────────────────────────────────────
# Realistic Weathering & Surface Erosion (التشويه وعوامل التعرية الحجرية)
# ──────────────────────────────────────────────────────────────────────────────
def apply_weathering(img):
    draw = ImageDraw.Draw(img)
    w, h = img.size

    # 1. Weathering flakes & erosion chips (تآكل وتشظي في أجزاء الحجر)
    if random.random() < 0.75:
        for _ in range(random.randint(3, 8)):
            cx = random.randint(30, w - 30)
            cy = random.randint(30, h - 30)
            rad_chip = random.randint(4, 15)
            chip_c = (random.randint(85, 150), random.randint(85, 150), random.randint(80, 145))
            num_pts = random.randint(5, 8)
            poly = []
            for i in range(num_pts):
                theta = 2 * math.pi * i / num_pts
                r = rad_chip * random.uniform(0.6, 1.4)
                poly.append((cx + r * math.cos(theta), cy + r * math.sin(theta)))
            draw.polygon(poly, fill=chip_c)

    # 2. Lichen & organic discoloration patches (بقع الأشنة والرطوبة الطبيعية)
    if random.random() < 0.55:
        for _ in range(random.randint(1, 3)):
            lx = random.randint(40, w - 40)
            ly = random.randint(40, h - 40)
            lr = random.randint(25, 70)
            lichen_c = random.choice([
                (random.randint(70, 110), random.randint(85, 125), random.randint(65, 95)),
                (random.randint(135, 175), random.randint(125, 160), random.randint(85, 120))
            ])
            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            o_draw = ImageDraw.Draw(overlay)
            o_draw.ellipse([lx - lr, ly - lr, lx + lr, ly + lr], fill=(*lichen_c, random.randint(35, 75)))
            overlay = overlay.filter(ImageFilter.GaussianBlur(radius=random.uniform(8, 16)))
            img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    # 3. Photometric variation
    img = ImageEnhance.Brightness(img).enhance(random.uniform(0.75, 1.25))
    img = ImageEnhance.Contrast(img).enhance(random.uniform(0.80, 1.25))
    if random.random() < 0.35:
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.3, 0.85)))
    if random.random() < 0.40:
        arr = np.array(img).astype(np.int16)
        arr = np.clip(arr + np.random.randint(-8, 8, arr.shape, dtype=np.int16), 0, 255).astype(np.uint8)
        img = Image.fromarray(arr)
    return img


# ──────────────────────────────────────────────────────────────────────────────
# Directory Setup & Previews
# ──────────────────────────────────────────────────────────────────────────────
def setup_dirs(base_path):
    dirs = {
        "train_img": Path(base_path) / "images" / "train",
        "val_img":   Path(base_path) / "images" / "val",
        "train_lbl": Path(base_path) / "labels" / "train",
        "val_lbl":   Path(base_path) / "labels" / "val",
        "preview":   Path(base_path) / "preview"
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs


def save_annotated_preview(img, labels, save_path):
    prev = img.copy()
    draw = ImageDraw.Draw(prev)
    w, h = prev.size

    for lbl in labels:
        parts = lbl.strip().split()
        if len(parts) != 5:
            continue
        cid = int(parts[0])
        bx, by, bw, bh = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
        xmin = int((bx - bw / 2) * w)
        ymin = int((by - bh / 2) * h)
        xmax = int((bx + bw / 2) * w)
        ymax = int((by + bh / 2) * h)

        cname = CLASS_NAMES[cid] if cid < len(CLASS_NAMES) else str(cid)
        color = (255, 60, 60) if cid == 16 else (30, 220, 80)

        draw.rectangle([xmin, ymin, xmax, ymax], outline=color, width=2)
        draw.text((xmin + 2, max(0, ymin - 12)), cname, fill=color)

    prev.save(save_path, quality=92)


def main():
    parser = argparse.ArgumentParser(description="Generate Canonical Younger Futhark Dataset")
    parser.add_argument("--output-dir", type=str, default="dataset", help="Output directory")
    parser.add_argument("--per-class", type=int, default=50, help="Images per class")
    parser.add_argument("--scenes", type=int, default=650, help="Scenes")
    parser.add_argument("--train-ratio", type=float, default=0.85, help="Train ratio")
    args = parser.parse_args()

    print("=" * 75)
    print("ᚱ AUTHENTIC YOUNGER FUTHARK DATASET GENERATOR")
    print(f"  - Classes : {len(CLASS_NAMES)} (16 Canonical Runes + Separator)")
    print(f"  - Output  : {Path(args.output_dir).resolve()}")
    print("=" * 75)

    dirs = setup_dirs(args.output_dir)

    yaml_dict = {
        "path": str(Path(args.output_dir).resolve()),
        "train": "images/train",
        "val": "images/val",
        "nc": len(CLASS_NAMES),
        "names": CLASS_NAMES
    }
    with open(Path(args.output_dir) / "dataset.yaml", "w", encoding="utf-8") as f:
        yaml.dump(yaml_dict, f, default_flow_style=False, allow_unicode=True)

    counter = 0
    val_step = max(2, int(1.0 / (1.0 - args.train_ratio)))

    for class_id in range(len(CLASS_NAMES)):
        cname = CLASS_NAMES[class_id]
        for i in range(args.per_class):
            img, labels = generate_sample(fixed_class_id=class_id)
            is_train = (i % val_step != 0)
            img_dest = dirs["train_img"] if is_train else dirs["val_img"]
            lbl_dest = dirs["train_lbl"] if is_train else dirs["val_lbl"]

            fname = f"rune_c{class_id:02d}_{i:04d}"
            img.save(img_dest / f"{fname}.jpg", quality=94)
            with open(lbl_dest / f"{fname}.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(labels))

            if counter < 20:
                save_annotated_preview(img, labels, dirs["preview"] / f"preview_{counter:03d}.jpg")

            counter += 1
        print(f"    ✓ Class {class_id:02d}: {cname:12s}")

    for i in range(args.scenes):
        img, labels = generate_sample(fixed_class_id=None)
        is_train = (i % val_step != 0)
        img_dest = dirs["train_img"] if is_train else dirs["val_img"]
        lbl_dest = dirs["train_lbl"] if is_train else dirs["val_lbl"]

        fname = f"scene_{i:05d}"
        img.save(img_dest / f"{fname}.jpg", quality=94)
        with open(lbl_dest / f"{fname}.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(labels))

        if counter < 40:
            save_annotated_preview(img, labels, dirs["preview"] / f"preview_{counter:03d}.jpg")

        counter += 1

    train_count = len(list(dirs["train_img"].glob("*.jpg")))
    val_count = len(list(dirs["val_img"].glob("*.jpg")))

    print("\n" + "=" * 75)
    print("🎉 DATASET GENERATION COMPLETE!")
    print(f"   Train Images : {train_count}")
    print(f"   Val Images   : {val_count}")
    print(f"   Total        : {train_count + val_count}")
    print("=" * 75)


if __name__ == "__main__":
    main()
