import sys
from PySide6.QtWidgets import QApplication
from aethernet.utils.logger import setup_logger
from aethernet.gui.main_window import MainWindow

def main():
    logger = setup_logger()
    logger.info("Starting AetherNet WiFi & Network Hub...")

    app = QApplication(sys.argv)
    app.setApplicationName("AetherNet")
    app.setOrganizationName("MrSpy00")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
