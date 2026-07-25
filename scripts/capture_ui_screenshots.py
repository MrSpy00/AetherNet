import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication

# Add src directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aethernet.platform import get_platform_adapter
from aethernet.gui.i18n_manager import I18nManager
from aethernet.gui.views.dashboard_view import DashboardView
from aethernet.gui.views.wifi_view import WifiView
from aethernet.gui.views.tools_view import ToolsView
from aethernet.gui.views.security_view import SecurityView
from aethernet.gui.views.api_hub_view import APIHubView
from aethernet.gui.views.pentest_view import PentestView
from aethernet.gui.theme_manager import ThemeManager

def capture_screenshots():
    app = QApplication.instance() or QApplication(sys.argv)
    adapter = get_platform_adapter()

    screenshots_dir = Path("assets/screenshots")
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    views_to_capture = [
        ("dashboard", DashboardView),
        ("wifi", WifiView),
        ("tools", ToolsView),
        ("security", SecurityView),
        ("api_hub", APIHubView),
        ("pentest", PentestView),
    ]

    for lang in ["tr", "en"]:
        i18n = I18nManager(lang)
        for name, cls in views_to_capture:
            try:
                widget = cls(adapter, i18n)
            except Exception as e:
                print(f"Skipping {name} ({lang}): {e}")
                continue
            widget.setStyleSheet(ThemeManager.get_theme_stylesheet("cyber_dark"))
            widget.resize(1100, 700)
            widget.show()

            app.processEvents()

            pixmap = widget.grab()
            out_file = screenshots_dir / f"{name}_{lang}.png"
            pixmap.save(str(out_file))
            print(f"[OK] Captured screenshot: {out_file}")
            widget.close()

if __name__ == "__main__":
    capture_screenshots()
