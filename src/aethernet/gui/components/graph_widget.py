import pyqtgraph as pg
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from collections import deque

class LiveSignalGraphWidget(QFrame):
    """Real-time Signal Strength (% / dBm) Live Graph using pyqtgraph"""

    def __init__(self, title: str = "Canlı Sinyal Gücü Geçmişi", max_points: int = 60, parent=None):
        super().__init__(parent)
        self.max_points = max_points
        self.data_history = deque([0] * max_points, maxlen=max_points)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("color: #94a3b8; font-size: 13px; font-weight: bold;")
        layout.addWidget(self.lbl_title)

        # Pyqtgraph plot widget setup
        pg.setConfigOption('background', '#10141d')
        pg.setConfigOption('foreground', '#64748b')

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.showGrid(x=True, y=True, alpha=0.15)
        self.plot_widget.setYRange(0, 100)
        self.plot_widget.setLabel('left', 'Sinyal (%)', color='#94a3b8')
        self.plot_widget.setLabel('bottom', 'Zaman (sn)', color='#94a3b8')

        # Cyber neon cyan line curve
        pen = pg.mkPen(color='#00f2fe', width=2)
        self.curve = self.plot_widget.plot(list(self.data_history), pen=pen)

        layout.addWidget(self.plot_widget)

    def add_data_point(self, value: float):
        self.data_history.append(value)
        self.curve.setData(list(self.data_history))
