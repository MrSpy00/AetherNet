import os
import sys
import PyInstaller.__main__
from pathlib import Path

def build():
    root = Path(__file__).parent.parent.resolve()
    spec_file = root / "AetherNet.spec"

    print(f"[*] AetherNet - PyInstaller spec dosyasi ile derleniyor: {spec_file}")
    args = [
        str(spec_file),
        "--noconfirm",
        "--clean",
    ]
    PyInstaller.__main__.run(args)

if __name__ == "__main__":
    build()
