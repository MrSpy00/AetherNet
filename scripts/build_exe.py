import os
import sys
import PyInstaller.__main__
from pathlib import Path

def build():
    root = Path(__file__).parent.parent.resolve()
    main_script = root / "src" / "aethernet" / "main.py"
    icon_file = root / "assets" / "icon.ico"
    config_dir = root / "config"
    assets_dir = root / "assets"

    sep = ";" if sys.platform.startswith("win") else ":"

    args = [
        str(main_script),
        "--name=AetherNet",
        "--onefile",
        "--noconsole",
        f"--icon={icon_file}",
        f"--add-data={config_dir}{sep}config",
        f"--add-data={assets_dir}{sep}assets",
        "--exclude-module=scipy",
        "--exclude-module=matplotlib",
        "--exclude-module=PIL",
        "--exclude-module=tkinter",
        "--exclude-module=tcl",
        "--exclude-module=unittest",
        "--exclude-module=pytest",
        "--exclude-module=IPython",
        "--exclude-module=jupyter"
    ]
    print(f"Building PyInstaller optimized executable: {args}")
    PyInstaller.__main__.run(args)

if __name__ == "__main__":
    build()
