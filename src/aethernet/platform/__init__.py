import sys
from aethernet.platform.base import BasePlatformAdapter
from aethernet.platform.windows import WindowsPlatformAdapter

def get_platform_adapter() -> BasePlatformAdapter:
    """Returns the OS-appropriate platform adapter instance"""
    if sys.platform == "win32":
        return WindowsPlatformAdapter()
    else:
        # Fallback to Windows adapter interface or Linux implementation when added
        return WindowsPlatformAdapter()
