import sys
import pytest
from PySide6.QtWidgets import QApplication
from aethernet.gui.main_window import MainWindow

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

def test_main_window_instantiation(qapp):
    win = MainWindow()
    assert win.windowTitle().startswith("AetherNet")
    assert win.stacked_widget.count() == 11
