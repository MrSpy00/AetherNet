import PyInstaller.__main__
import sys
from pathlib import Path

def build():
    root = Path(__file__).parent.parent
    main_script = root / "src" / "aethernet" / "main.py"

    args = [
        str(main_script),
        "--name=AetherNet",
        "--onefile",
        "--noconsole",
        f"--add-data={root / 'config'};config",
        "--clean"
    ]
    print(f"Building PyInstaller executable with args: {args}")
    PyInstaller.__main__.run(args)

if __name__ == "__main__":
    build()
