import pyqtgraph as pg
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtGui import QBrush, QColor, QLinearGradient
from PySide6.QtCore import Qt
from collections import deque

class LiveSignalGraphWidget(QFrame):
    """Real-time Signal Strength (% / dBm) Live Graph with Gradient Fill & Neon Curve"""

    def __init__(self, title: str = "Canlı Sinyal Gücü Geçmişi", max_points: int = 60, parent=None):
        super().__init__(parent)
        self.max_points = max_points
        self.data_history = deque([0] * max_points, maxlen=max_points)

        self.setProperty("class", "glass-panel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        # Header Row
        header_row = QHBoxLayout()
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("color: #f8fafc; font-size: 13px; font-weight: bold;")
        header_row.addWidget(self.lbl_title)

        header_row.addStretch()

        self.lbl_stats = QLabel("Peak: 0% | Avg: 0%")
        self.lbl_stats.setStyleSheet("color: #00f2fe; font-size: 11px; font-weight: bold; background-color: #141c2e; padding: 3px 8px; border-radius: 6px;")
        header_row.addWidget(self.lbl_stats)
        layout.addLayout(header_row)

        # Pyqtgraph plot widget setup
        pg.setConfigOption('background', '#080b10')
        pg.setConfigOption('foreground', '#64748b')

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.showGrid(x=True, y=True, alpha=0.15)
        self.plot_widget.setYRange(0, 100)
        self.plot_widget.setLabel('left', 'Sinyal (%)', color='#94a3b8')
        self.plot_widget.setLabel('bottom', 'Zaman (sn)', color='#94a3b8')

        # Cyber neon cyan line curve with area fill
        pen = pg.mkPen(color='#00f2fe', width=2.5)
        fill_brush = QBrush(QColor(0, 242, 254, 40))
        self.curve = self.plot_widget.plot(list(self.data_history), pen=pen, fillLevel=0, fillBrush=fill_brush)

        layout.addWidget(self.plot_widget)

    def add_data_point(self, value: float):
        self.data_history.append(value)
        data_list = list(self.data_history)
        self.curve.setData(data_list)

        # Calculate live stats
        if data_list:
            peak = max(data_list)
            avg = sum(data_list) / len(data_list)
            self.lbl_stats.setText(f"Peak: {int(peak)}% | Avg: {int(avg)}%")
