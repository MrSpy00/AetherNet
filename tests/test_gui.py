import os
import sys
import pytest
from PySide6.QtWidgets import QApplication
from aethernet.gui.main_window import MainWindow

_qapp_instance = None

@pytest.fixture(scope="session")
def qapp():
    global _qapp_instance
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    _qapp_instance = QApplication.instance()
    if _qapp_instance is None:
        _qapp_instance = QApplication(sys.argv)
    yield _qapp_instance



def test_main_window_instantiation(qapp):
    win = MainWindow()
    assert win.windowTitle() == "AetherNet - WiFi & Ağ Yönetim Hub'ı"
    assert win.stacked_widget.count() == 13
    for i in range(win.stacked_widget.count()):
        v = win.stacked_widget.widget(i)
        if hasattr(v, 'close'):
            v.close()
    win.close()
    win.deleteLater()
    qapp.processEvents()


