from PySide6.QtWidgets import QStackedWidget, QWidget, QGraphicsDropShadowEffect, QGraphicsOpacityEffect
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSequentialAnimationGroup, Qt
from PySide6.QtGui import QColor

class GlowEffectHelper:
    """Helper for adding neon glowing drop shadow effects to PySide6 widgets"""

    @staticmethod
    def apply_glow(widget: QWidget, color_hex: str = "#00f2fe", blur_radius: int = 20, offset_y: int = 0):
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setBlurRadius(blur_radius)
        shadow.setColor(QColor(color_hex))
        shadow.setOffset(0, offset_y)
        widget.setGraphicsEffect(shadow)
        return shadow

class FadingStackedWidget(QStackedWidget):
    """QStackedWidget subclass that smoothly fades between stacked views"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.fade_duration = 180
        self._anim_group = None

    def setCurrentIndex(self, index: int):
        if index == self.currentIndex() or index < 0 or index >= self.count():
            return

        current_widget = self.currentWidget()
        next_widget = self.widget(index)

        if not current_widget or not next_widget:
            super().setCurrentIndex(index)
            return

        # Clear any existing animation
        if self._anim_group and self._anim_group.state() == QParallelAnimationGroup.Running:
            self._anim_group.stop()

        # Switch view first
        super().setCurrentIndex(index)

        # Prepare opacity effect on next widget
        eff_next = QGraphicsOpacityEffect(next_widget)
        next_widget.setGraphicsEffect(eff_next)

        anim_in = QPropertyAnimation(eff_next, b"opacity")
        anim_in.setDuration(self.fade_duration)
        anim_in.setStartValue(0.2)
        anim_in.setEndValue(1.0)
        anim_in.setEasingCurve(QEasingCurve.OutCubic)

        def _on_finished():
            next_widget.setGraphicsEffect(None)

        anim_in.finished.connect(_on_finished)
        self._anim_group = anim_in
        anim_in.start()
