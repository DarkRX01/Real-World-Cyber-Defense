#!/usr/bin/env python3
"""
Generate Windows .ico file from shield.svg

Requirements:
    pip install cairosvg pillow

Usage:
    python generate-ico.py

This will create icons/icon.ico for use with PyInstaller builds.
"""

import sys
from pathlib import Path

try:
    from PIL import Image
    import cairosvg
    import io
except ImportError:
    print("Please install required packages:")
    print("  pip install cairosvg pillow")
    sys.exit(1)


def svg_to_ico(svg_path: Path, ico_path: Path, sizes: list = None):
    """Convert SVG to ICO with multiple sizes."""
    if sizes is None:
        sizes = [16, 24, 32, 48, 64, 128, 256]
    
    images = []
    
    for size in sizes:
        # Convert SVG to PNG at this size
        png_data = cairosvg.svg2png(
            url=str(svg_path),
            output_width=size,
            output_height=size
        )
        
        # Open with PIL
        img = Image.open(io.BytesIO(png_data))
        img = img.convert("RGBA")
        images.append(img)
        print(f"  Generated {size}x{size}")
    
    # Save as ICO with all sizes
    # ICO saves the first image and appends others
    images[0].save(
        ico_path,
        format="ICO",
        sizes=[(img.width, img.height) for img in images],
        append_images=images[1:]
    )
    
    print(f"\n✅ Created: {ico_path}")


def main():
    script_dir = Path(__file__).parent
    svg_path = script_dir / "shield.svg"
    ico_path = script_dir / "icon.ico"
    
    if not svg_path.exists():
        print(f"❌ SVG not found: {svg_path}")
        sys.exit(1)
    
    print("🛡️ Generating Windows icon...")
    print(f"   Source: {svg_path}")
    print(f"   Output: {ico_path}")
    print()
    
    svg_to_ico(svg_path, ico_path)
    
    print()
    print("You can now use this icon with PyInstaller:")
    print(f'  pyinstaller --icon="{ico_path}" app_main.py')


if __name__ == "__main__":
    main()
