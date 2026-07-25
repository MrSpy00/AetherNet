import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from aethernet.utils.logger import setup_logger
from aethernet.gui.main_window import MainWindow


def main():
    logger = setup_logger()
    logger.info("Starting AetherNet WiFi & Network Hub...")

    app = QApplication(sys.argv)
    app.setApplicationName("AetherNet")
    app.setOrganizationName("MrSpy00")

    icon_path = Path("assets/icon.ico")
    if not icon_path.exists():
        icon_path = Path("assets/logo.png")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))


    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
