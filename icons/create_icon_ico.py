#!/usr/bin/env python3
"""Create icon.ico - Cyber Defense app icon. Modern shield with cyan/purple accent."""
from pathlib import Path
try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Run: pip install Pillow")
    exit(1)

def draw_shield(size):
    """Draw a sleek shield icon: dark bg, cyan shield, subtle glow."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = max(2, size // 12)
    cx, cy = size // 2, size // 2
    w = size - 2 * pad
    h = size - 2 * pad
    # Shield: wide at top, narrow at bottom (classic shield)
    # Points: top-center, top-right, mid-right, bottom, mid-left, top-left
    pts = [
        (cx, pad + h // 12),
        (size - pad - w // 12, pad + h // 3),
        (size - pad, cy),
        (cx, size - pad - h // 12),
        (pad, cy),
        (pad + w // 12, pad + h // 3),
    ]
    # Main shield - teal/cyan (#06b6d4)
    d.polygon(pts, fill=(6, 182, 212, 255), outline=(14, 165, 233, 255))
    # Inner highlight
    inner_pts = [
        (cx, pad + h // 6),
        (size - pad - w // 6, pad + h // 3 + h // 24),
        (size - pad - w // 24, cy),
        (cx, size - pad - h // 6),
        (pad + w // 24, cy),
        (pad + w // 6, pad + h // 3 + h // 24),
    ]
    d.polygon(inner_pts, outline=(159, 243, 229, 120))
    # Small checkmark or lock accent at center (for small sizes, skip)
    if size >= 32:
        mx, my = cx, cy + h // 12
        d.line([(mx - w//8, my), (mx - w//24, my + h//12), (mx + w//6, my - h//12)], 
               fill=(255, 255, 255, 200), width=max(1, size // 32))
    return img

def main():
    script_dir = Path(__file__).parent
    ico_path = script_dir / "icon.ico"
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = [draw_shield(s) for s in sizes]
    images[0].save(ico_path, format="ICO", sizes=[(s, s) for s in sizes], append_images=images[1:])
    print(f"Created: {ico_path}")

def create_png_logo():
    """Also create 256x256 PNG for window icon (app_main uses this)."""
    script_dir = Path(__file__).parent
    png_path = script_dir / "cyberdefense_logo_256.png"
    img = draw_shield(256)
    img.save(png_path)
    print(f"Created: {png_path}")

if __name__ == "__main__":
    main()
    create_png_logo()
