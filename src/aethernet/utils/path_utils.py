import sys
from pathlib import Path

def get_asset_path(relative_path: str) -> Path:
    """Get absolute path to asset, works for dev and PyInstaller bundle"""
    if hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(".").resolve()
    
    full_path = base_path / relative_path
    if not full_path.exists():
        # Fallback to local cwd
        full_path = Path(".").resolve() / relative_path
    return full_path
