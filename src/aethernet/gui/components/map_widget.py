import logging
import webbrowser
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QRadialGradient

logger = logging.getLogger(__name__)


class CyberMapCanvas(QWidget):
    """High-Performance Native Cyber-Noir Geolocation & Radar Canvas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lat = 0.0
        self.lon = 0.0
        self.ip = ""
        self.city = ""
        self.country = ""
        self.isp = ""
        self.setMinimumHeight(240)

    def set_location(self, lat: float, lon: float, ip: str, city: str, country: str, isp: str):
        self.lat = lat
        self.lon = lon
        self.ip = ip
        self.city = city
        self.country = country
        self.isp = isp
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # Background
        painter.fillRect(0, 0, w, h, QColor(9, 5, 20))

        # Cyber Grid Lines
        pen_grid = QPen(QColor(30, 27, 75, 120), 1, Qt.DashLine)
        painter.setPen(pen_grid)
        grid_size = 40
        for x in range(0, w, grid_size):
            painter.drawLine(x, 0, x, h)
        for y in range(0, h, grid_size):
            painter.drawLine(0, y, w, y)

        # Concentric Radar Circles in Center
        cx, cy = w // 2, h // 2
        pen_radar = QPen(QColor(124, 58, 237, 40), 1)
        painter.setPen(pen_radar)
        for r in range(40, max(w, h) // 2, 40):
            painter.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        if self.lat == 0.0 and self.lon == 0.0:
            # Standby state
            painter.setPen(QColor(168, 85, 247, 200))
            painter.setFont(QFont("Segoe UI", 11, QFont.Bold))
            painter.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, "📍 SİBER COĞRAFİ KONUM VE RADAR MODÜLÜ HAZIR\nIP sorgulaması bekleniyor...")
            return

        # Target pulse pin position based on lat/lon projection onto grid
        # Map lat (-90..90) and lon (-180..180) to canvas offsets relative to center
        px = int(cx + (self.lon / 180.0) * (w / 2.5))
        py = int(cy - (self.lat / 90.0) * (h / 2.5))
        px = max(40, min(w - 40, px))
        py = max(40, min(h - 40, py))

        # Target Pulse Glow
        gradient = QRadialGradient(px, py, 40)
        gradient.setColorAt(0.0, QColor(0, 242, 254, 180))
        gradient.setColorAt(0.5, QColor(124, 58, 237, 80))
        gradient.setColorAt(1.0, QColor(9, 5, 20, 0))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(px - 40, py - 40, 80, 80)

        # Target Crosshair Lines
        pen_target = QPen(QColor(0, 242, 254, 200), 1, Qt.SolidLine)
        painter.setPen(pen_target)
        painter.drawLine(px - 20, py, px + 20, py)
        painter.drawLine(px, py - 20, px, py + 20)
        painter.drawEllipse(px - 8, py - 8, 16, 16)

        # Center Red Hotspot
        painter.setBrush(QColor(239, 68, 68))
        painter.setPen(QPen(QColor(255, 255, 255), 1.5))
        painter.drawEllipse(px - 4, py - 4, 8, 8)

        # Telemetry Banner Overlay (Top Left)
        painter.setBrush(QColor(13, 8, 26, 220))
        painter.setPen(QPen(QColor(124, 58, 237), 1))
        painter.drawRoundedRect(12, 12, 340, 76, 8, 8)

        painter.setPen(QColor(0, 242, 254))
        painter.setFont(QFont("Segoe UI", 10, QFont.Bold))
        painter.drawText(24, 34, f"TARGET IP: {self.ip}")

        painter.setPen(QColor(248, 250, 252))
        painter.setFont(QFont("Segoe UI", 9))
        painter.drawText(24, 54, f"Konum: {self.city}, {self.country} ({self.lat:.4f}, {self.lon:.4f})")
        painter.drawText(24, 72, f"ISP: {self.isp}")


class MapViewerWidget(QFrame):
    """High-Performance Cyber-Noir Geolocation Map Widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(280)
        self.setStyleSheet("""
            QFrame {
                background-color: #090514;
                border: 1px solid #7c3aed;
                border-radius: 10px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Canvas
        self.canvas = CyberMapCanvas()
        layout.addWidget(self.canvas)

        # Bottom Bar
        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(8, 2, 8, 6)

        self.status_label = QLabel("📍 Coğrafi Konum Modülü Aktif")
        self.status_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        bottom_bar.addWidget(self.status_label)

        bottom_bar.addStretch()

        self.btn_open_external = QPushButton("🌍 OpenStreetMap'te Aç")
        self.btn_open_external.setCursor(Qt.PointingHandCursor)
        self.btn_open_external.setStyleSheet("""
            QPushButton {
                background-color: #1e1b4b;
                color: #a855f7;
                border: 1px solid #7c3aed;
                border-radius: 6px;
                padding: 4px 12px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #7c3aed;
                color: #ffffff;
            }
        """)
        self.btn_open_external.clicked.connect(self._open_in_browser)
        bottom_bar.addWidget(self.btn_open_external)

        layout.addLayout(bottom_bar)

    def _open_in_browser(self):
        if self.canvas.lat != 0.0 or self.canvas.lon != 0.0:
            url = f"https://www.openstreetmap.org/?mlat={self.canvas.lat}&mlon={self.canvas.lon}#map=12/{self.canvas.lat}/{self.canvas.lon}"
            webbrowser.open(url)

    def update_location(self, lat: float, lon: float, ip: str, city: str, country: str, isp: str):
        """Updates geolocation map canvas with given IP details."""
        self.canvas.set_location(lat, lon, ip, city, country, isp)
        if lat != 0.0 or lon != 0.0:
            self.status_label.setText(f"📍 Konum Tespit Edildi: {city}, {country} ({lat:.4f}, {lon:.4f})")
        else:
            self.status_label.setText("📍 Coğrafi Konum Modülü Aktif")
