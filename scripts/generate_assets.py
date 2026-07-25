import sys
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# 1. Create Assets Directory
assets_dir = Path("assets")
screenshots_dir = assets_dir / "screenshots"
assets_dir.mkdir(exist_ok=True)
screenshots_dir.mkdir(exist_ok=True)

def generate_logo():
    """Generates a high-quality Cyber-Noir AetherNet App Icon & Logo"""
    size = (256, 256)
    img = Image.new("RGBA", size, (11, 14, 20, 255)) # #0b0e14 background
    draw = ImageDraw.Draw(img)

    # Outer Neon Circle Gradient/Ring
    draw.ellipse([16, 16, 240, 240], outline=(0, 242, 254, 255), width=6)
    draw.ellipse([28, 28, 228, 228], outline=(30, 41, 61, 255), width=3)

    # WiFi Signal Arcs (Top Center)
    # Arc 1 (Outer)
    draw.arc([60, 60, 196, 196], start=210, end=330, fill=(0, 242, 254, 255), width=8)
    # Arc 2 (Middle)
    draw.arc([84, 84, 172, 172], start=210, end=330, fill=(56, 189, 248, 255), width=8)
    # Arc 3 (Inner)
    draw.arc([108, 108, 148, 148], start=210, end=330, fill=(74, 222, 128, 255), width=8)

    # Central Lightning Bolt Symbol (Cyber Polygon)
    lightning_points = [
        (134, 125), (115, 160), (130, 160), (122, 195),
        (148, 150), (132, 150), (142, 125)
    ]
    draw.polygon(lightning_points, fill=(0, 242, 254, 255))

    # Save PNG Logo
    logo_png = assets_dir / "logo.png"
    img.save(logo_png, format="PNG")
    print(f"Generated logo at: {logo_png}")

    # Save Multi-resolution Windows ICO Icon
    icon_ico = assets_dir / "icon.ico"
    img.save(
        icon_ico,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    )
    print(f"Generated ICO icon at: {icon_ico}")

if __name__ == "__main__":
    generate_logo()
