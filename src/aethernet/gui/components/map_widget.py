import math
import logging
import urllib.request
import webbrowser
from typing import Dict, Tuple, Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt, QRectF, QPoint, Signal, QObject, QThread
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QRadialGradient, QPixmap, QImage

logger = logging.getLogger(__name__)

TILE_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AetherNet-OSMMap/1.0"


def latlon_to_tile(lat: float, lon: float, zoom: int) -> Tuple[int, int, float, float]:
    """Converts lat/lon to OpenStreetMap tile coordinates and pixel offsets inside tile (256x256)."""
    lat_clamped = max(-85.0511, min(85.0511, lat))
    lon_clamped = max(-180.0, min(180.0, lon))
    lat_rad = math.radians(lat_clamped)
    n = 2.0 ** zoom
    x_exact = (lon_clamped + 180.0) / 360.0 * n
    y_exact = (1.0 - math.log(math.tan(lat_rad) + (1.0 / math.cos(lat_rad))) / math.pi) / 2.0 * n
    
    xtile = int(x_exact)
    ytile = int(y_exact)
    
    offset_x = (x_exact - xtile) * 256.0
    offset_y = (y_exact - ytile) * 256.0
    return xtile, ytile, offset_x, offset_y


class TileFetcherWorker(QObject):
    """Background worker thread to fetch OpenStreetMap PNG tiles without blocking UI."""
    tile_fetched = Signal(int, int, int, bytes)  # zoom, x, y, image_bytes

    def fetch_tile(self, zoom: int, x: int, y: int):
        url = f"https://tile.openstreetmap.org/{zoom}/{x}/{y}.png"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": TILE_USER_AGENT})
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    data = resp.read()
                    self.tile_fetched.emit(zoom, x, y, data)
        except Exception as e:
            logger.debug(f"Failed to fetch OSM tile ({zoom}/{x}/{y}): {e}")


class CyberMapCanvas(QWidget):
    """High-Performance Native Interactive OpenStreetMap Canvas with Cyber-Noir Styling."""

    request_tile = Signal(int, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lat = 0.0
        self.lon = 0.0
        self.ip = ""
        self.city = ""
        self.country = ""
        self.isp = ""
        self.zoom = 12

        self.tile_cache: Dict[Tuple[int, int, int], QPixmap] = {}
        self.pending_tiles = set()
        
        # Pan drag state
        self.is_dragging = False
        self.drag_start = QPoint()
        self.pan_offset_x = 0.0
        self.pan_offset_y = 0.0

        self.setMinimumHeight(280)
        self.setCursor(Qt.OpenHandCursor)

    def set_location(self, lat: float, lon: float, ip: str, city: str, country: str, isp: str):
        self.lat = lat
        self.lon = lon
        self.ip = ip
        self.city = city
        self.country = country
        self.isp = isp
        self.pan_offset_x = 0.0
        self.pan_offset_y = 0.0
        self.update()

    def set_zoom(self, new_zoom: int):
        self.zoom = max(2, min(18, new_zoom))
        self.update()

    def on_tile_received(self, zoom: int, x: int, y: int, data: bytes):
        key = (zoom, x, y)
        if key in self.pending_tiles:
            self.pending_tiles.remove(key)
        
        img = QImage()
        if img.loadFromData(data):
            pixmap = QPixmap.fromImage(img)
            self.tile_cache[key] = pixmap
            self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_start = event.pos()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            delta = event.pos() - self.drag_start
            self.drag_start = event.pos()
            self.pan_offset_x += delta.x()
            self.pan_offset_y += delta.y()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.setCursor(Qt.OpenHandCursor)

    def wheelEvent(self, event):
        angle = event.angleDelta().y()
        if angle > 0:
            self.set_zoom(self.zoom + 1)
        elif angle < 0:
            self.set_zoom(self.zoom - 1)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        w = self.width()
        h = self.height()

        # Background Cyber Fill
        painter.fillRect(0, 0, w, h, QColor(9, 5, 20))

        if self.lat == 0.0 and self.lon == 0.0:
            # Standby background grid & message
            pen_grid = QPen(QColor(30, 27, 75, 120), 1, Qt.DashLine)
            painter.setPen(pen_grid)
            for x in range(0, w, 40):
                painter.drawLine(x, 0, x, h)
            for y in range(0, h, 40):
                painter.drawLine(0, y, w, y)

            painter.setPen(QColor(0, 242, 254, 200))
            painter.setFont(QFont("Segoe UI", 11, QFont.Bold))
            painter.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, "📍 CANLI OPENSTREETMAP VE COĞRAFİ KONUM MODÜLÜ HAZIR\nIP sorgulaması yapıldığında harita anında yüklenecektir.")
            return

        # Calculate OpenStreetMap tiles
        center_x = w / 2.0 + self.pan_offset_x
        center_y = h / 2.0 + self.pan_offset_y

        xtile, ytile, px_off, py_off = latlon_to_tile(self.lat, self.lon, self.zoom)

        # Draw 5x5 tile matrix around target
        tiles_range = 2
        for dx in range(-tiles_range, tiles_range + 1):
            for dy in range(-tiles_range, tiles_range + 1):
                tx = xtile + dx
                ty = ytile + dy
                key = (self.zoom, tx, ty)

                dest_x = int(center_x + dx * 256 - px_off)
                dest_y = int(center_y + dy * 256 - py_off)

                # Check bounding box
                if dest_x + 256 < 0 or dest_x > w or dest_y + 256 < 0 or dest_y > h:
                    continue

                if key in self.tile_cache:
                    painter.drawPixmap(dest_x, dest_y, self.tile_cache[key])
                else:
                    # Draw Cyber Grid Tile Placeholder
                    painter.fillRect(dest_x, dest_y, 256, 256, QColor(15, 10, 30))
                    painter.setPen(QPen(QColor(124, 58, 237, 40), 1))
                    painter.drawRect(dest_x, dest_y, 256, 256)

                    if key not in self.pending_tiles:
                        self.pending_tiles.add(key)
                        self.request_tile.emit(self.zoom, tx, ty)

        # Apply Subtle Cyber-Noir Tint Overlay over OSM Tiles
        painter.fillRect(0, 0, w, h, QColor(9, 5, 20, 75))

        # Draw Target Location Marker Pin
        px = int(center_x)
        py = int(center_y)

        # Pulse Glow Radius
        gradient = QRadialGradient(px, py, 36)
        gradient.setColorAt(0.0, QColor(0, 242, 254, 210))
        gradient.setColorAt(0.5, QColor(124, 58, 237, 100))
        gradient.setColorAt(1.0, QColor(9, 5, 20, 0))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(px - 36, py - 36, 72, 72)

        # Target Crosshair
        painter.setPen(QPen(QColor(0, 242, 254), 1.5))
        painter.drawLine(px - 16, py, px + 16, py)
        painter.drawLine(px, py - 16, px, py + 16)
        painter.drawEllipse(px - 7, py - 7, 14, 14)

        # Center Red Hotspot Pin
        painter.setBrush(QColor(239, 68, 68))
        painter.setPen(QPen(QColor(255, 255, 255), 1.5))
        painter.drawEllipse(px - 4, py - 4, 8, 8)

        # Telemetry Overlay Card (Top Left)
        painter.setBrush(QColor(9, 5, 20, 220))
        painter.setPen(QPen(QColor(0, 242, 254), 1))
        painter.drawRoundedRect(12, 12, 340, 76, 8, 8)

        painter.setPen(QColor(0, 242, 254))
        painter.setFont(QFont("Segoe UI", 10, QFont.Bold))
        painter.drawText(24, 34, f"TARGET IP: {self.ip}")

        painter.setPen(QColor(248, 250, 252))
        painter.setFont(QFont("Segoe UI", 9))
        painter.drawText(24, 54, f"Konum: {self.city}, {self.country} ({self.lat:.4f}, {self.lon:.4f})")
        painter.drawText(24, 72, f"ISP: {self.isp}")


class MapViewerWidget(QFrame):
    """High-Performance Cyber-Noir Geolocation & Live OpenStreetMap Widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(300)
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

        # Setup Worker Thread for OSM Tile Downloading
        self.worker = TileFetcherWorker()
        self.thread = QThread(self)
        self.worker.moveToThread(self.thread)
        self.thread.start()

        self.canvas.request_tile.connect(self.worker.fetch_tile)
        self.worker.tile_fetched.connect(self.canvas.on_tile_received)

        # Bottom Controls Bar
        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(8, 4, 8, 6)

        self.status_label = QLabel("🗺️ Canlı OpenStreetMap Modülü Aktif")
        self.status_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        bottom_bar.addWidget(self.status_label)

        bottom_bar.addStretch()

        # Zoom Controls (+ / -)
        btn_zoom_in = QPushButton("🔍 +")
        btn_zoom_in.setToolTip("Yakınlaş")
        btn_zoom_in.setCursor(Qt.PointingHandCursor)
        btn_zoom_in.setStyleSheet("""
            QPushButton {
                background-color: #1e1b4b; color: #00f2fe; border: 1px solid #7c3aed;
                border-radius: 4px; padding: 3px 8px; font-weight: bold;
            }
            QPushButton:hover { background-color: #7c3aed; color: #ffffff; }
        """)
        btn_zoom_in.clicked.connect(lambda: self.canvas.set_zoom(self.canvas.zoom + 1))
        bottom_bar.addWidget(btn_zoom_in)

        btn_zoom_out = QPushButton("🔍 -")
        btn_zoom_out.setToolTip("Uzaklaş")
        btn_zoom_out.setCursor(Qt.PointingHandCursor)
        btn_zoom_out.setStyleSheet("""
            QPushButton {
                background-color: #1e1b4b; color: #00f2fe; border: 1px solid #7c3aed;
                border-radius: 4px; padding: 3px 8px; font-weight: bold;
            }
            QPushButton:hover { background-color: #7c3aed; color: #ffffff; }
        """)
        btn_zoom_out.clicked.connect(lambda: self.canvas.set_zoom(self.canvas.zoom - 1))
        bottom_bar.addWidget(btn_zoom_out)

        # Reset Center Button
        btn_reset = QPushButton("🎯 Odaklan")
        btn_reset.setToolTip("Hedef Konuma Odaklan")
        btn_reset.setCursor(Qt.PointingHandCursor)
        btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #1e1b4b; color: #a855f7; border: 1px solid #7c3aed;
                border-radius: 4px; padding: 3px 8px; font-weight: bold; font-size: 11px;
            }
            QPushButton:hover { background-color: #7c3aed; color: #ffffff; }
        """)
        btn_reset.clicked.connect(lambda: self.canvas.set_location(self.canvas.lat, self.canvas.lon, self.canvas.ip, self.canvas.city, self.canvas.country, self.canvas.isp))
        bottom_bar.addWidget(btn_reset)

        self.btn_open_external = QPushButton("🌍 OSM Web")
        self.btn_open_external.setCursor(Qt.PointingHandCursor)
        self.btn_open_external.setStyleSheet("""
            QPushButton {
                background-color: #1e1b4b; color: #a855f7; border: 1px solid #7c3aed;
                border-radius: 4px; padding: 3px 8px; font-weight: bold; font-size: 11px;
            }
            QPushButton:hover { background-color: #7c3aed; color: #ffffff; }
        """)
        self.btn_open_external.clicked.connect(self._open_in_browser)
        bottom_bar.addWidget(self.btn_open_external)

        layout.addLayout(bottom_bar)

    def _open_in_browser(self):
        if self.canvas.lat != 0.0 or self.canvas.lon != 0.0:
            url = f"https://www.openstreetmap.org/?mlat={self.canvas.lat}&mlon={self.canvas.lon}#map={self.canvas.zoom}/{self.canvas.lat}/{self.canvas.lon}"
            webbrowser.open(url)

    def update_location(self, lat: float, lon: float, ip: str, city: str, country: str, isp: str):
        """Updates geolocation map canvas with given IP details."""
        self.canvas.set_location(lat, lon, ip, city, country, isp)
        if lat != 0.0 or lon != 0.0:
            self.status_label.setText(f"📍 Canlı Harita Konumu: {city}, {country} ({lat:.4f}, {lon:.4f})")
        else:
            self.status_label.setText("🗺️ Canlı OpenStreetMap Modülü Aktif")

    def closeEvent(self, event):
        self.thread.quit()
        self.thread.wait()
        super().closeEvent(event)
