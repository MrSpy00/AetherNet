import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False

logger = logging.getLogger(__name__)


class MapViewerWidget(QFrame):
    """Interactive Dark-Mode OpenStreetMap Geolocation Visualizer Widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(280)
        self.setStyleSheet("""
            QFrame {
                background-color: #030712;
                border: 1px solid #7c3aed;
                border-radius: 10px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        if WEBENGINE_AVAILABLE:
            self.web_view = QWebEngineView()
            self.web_view.setStyleSheet("border: none; border-radius: 8px;")
            layout.addWidget(self.web_view)
            self._render_blank_map()
        else:
            self.fallback_label = QLabel("Harita görselleştirme için QWebEngine Yüklenemedi.")
            self.fallback_label.setAlignment(Qt.AlignCenter)
            self.fallback_label.setFont(QFont("Segoe UI", 12))
            self.fallback_label.setStyleSheet("color: #a855f7;")
            layout.addWidget(self.fallback_label)

    def _render_blank_map(self):
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { background-color: #030712; color: #a855f7; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
                .box { text-align: center; border: 1px dashed #7c3aed; padding: 20px; border-radius: 10px; }
            </style>
        </head>
        <body>
            <div class="box">
                <h3>📍 Coğrafi Konum Haritası Hazır</h3>
                <p>IP sorgulaması yapıldığında harita konumu otomatik olarak güncellenecektir.</p>
            </div>
        </body>
        </html>
        """
        self.web_view.setHtml(html)

    def update_location(self, lat: float, lon: float, ip: str, city: str, country: str, isp: str):
        """Loads Leaflet OpenStreetMap view pinned at the specified lat/lon."""
        if not WEBENGINE_AVAILABLE:
            if hasattr(self, 'fallback_label'):
                self.fallback_label.setText(f"📍 Konum: {city}, {country} ({lat}, {lon}) | IP: {ip} | ISP: {isp}")
            return

        if lat == 0.0 and lon == 0.0:
            self._render_blank_map()
            return

        leaflet_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                html, body, #map {{ height: 100%; width: 100%; margin: 0; padding: 0; background-color: #090514; }}
                .leaflet-popup-content-wrapper {{ background: #0d081a; color: #f8fafc; border: 1px solid #7c3aed; border-radius: 8px; font-family: sans-serif; }}
                .leaflet-popup-tip {{ background: #0d081a; }}
                .dark-tile {{ filter: brightness(0.7) invert(1) contrast(1.3) hue-rotate(200deg); }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                var map = L.map('map').setView([{lat}, {lon}], 10);
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    maxZoom: 19,
                    className: 'dark-tile',
                    attribution: '© OpenStreetMap contributors'
                }}).addTo(map);

                var marker = L.marker([{lat}, {lon}]).addTo(map);
                marker.bindPopup("<b>IP: {ip}</b><br/><b>Konum:</b> {city}, {country}<br/><b>ISP:</b> {isp}<br/><b>Koordinat:</b> {lat}, {lon}").openPopup();
            </script>
        </body>
        </html>
        """
        self.web_view.setHtml(leaflet_html)
