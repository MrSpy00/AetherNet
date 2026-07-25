from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize
from aethernet.gui.icon_manager import IconManager

class ToastNotification(QWidget):
    """Floating Glassmorphism Toast Notification Overlay for UI Feedback"""

    _instance = None

    @classmethod
    def show_toast(cls, parent: QWidget, message: str, is_success: bool = True, duration_ms: int = 2500):
        if cls._instance is not None:
            try:
                cls._instance.close()
            except Exception:
                pass

        cls._instance = ToastNotification(parent, message, is_success, duration_ms)
        cls._instance.show()

    def __init__(self, parent: QWidget, message: str, is_success: bool, duration_ms: int):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)

        bg_color = "#0f291e" if is_success else "#3b1115"
        border_color = "#22c55e" if is_success else "#ef4444"
        text_color = "#4ade80" if is_success else "#f87171"

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 6px 16px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)

        icon_name = "wifi" if is_success else "security"
        lbl_icon = QLabel()
        lbl_icon.setPixmap(IconManager.get_pixmap(icon_name, color=text_color, size=16))
        layout.addWidget(lbl_icon)

        lbl_msg = QLabel(message)
        lbl_msg.setStyleSheet(f"color: {text_color}; font-weight: bold; font-size: 12px; background: transparent; border: none;")
        layout.addWidget(lbl_msg)

        # Position at top center of parent widget
        self.adjustSize()
        if parent:
            px = (parent.width() - self.width()) // 2
            py = 30
            self.move(px, py)

        # Fade in & out animation
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.anim_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim_in.setDuration(300)
        self.anim_in.setStartValue(0.0)
        self.anim_in.setEndValue(1.0)
        self.anim_in.start()

        QTimer.singleShot(duration_ms, self._fade_out)

    def _fade_out(self):
        self.anim_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim_out.setDuration(400)
        self.anim_out.setStartValue(1.0)
        self.anim_out.setEndValue(0.0)
        self.anim_out.finished.connect(self.close)
        self.anim_out.start()
