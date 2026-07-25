from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSystemTrayIcon, QMenu
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QIcon, QGuiApplication

from aethernet.platform import get_platform_adapter
from aethernet.gui.theme_manager import ThemeManager
from aethernet.gui.i18n_manager import I18nManager
from aethernet.gui.animations import FadingStackedWidget
from aethernet.gui.components.top_bar import TopBar
from aethernet.gui.components.sidebar import Sidebar
from aethernet.utils.path_utils import get_asset_path

from aethernet.gui.views.dashboard_view import DashboardView
from aethernet.gui.views.wifi_view import WifiView
from aethernet.gui.views.profiles_view import ProfilesView
from aethernet.gui.views.environment_view import EnvironmentView
from aethernet.gui.views.discovery_view import DiscoveryView
from aethernet.gui.views.tools_view import ToolsView
from aethernet.gui.views.security_view import SecurityView
from aethernet.gui.views.pentest_view import PentestView
from aethernet.gui.views.topology_view import TopologyView
from aethernet.gui.views.router_view import RouterView
from aethernet.gui.views.settings_view import SettingsView
from aethernet.gui.views.logs_view import LogsView
from aethernet.gui.views.api_hub_view import APIHubView

class MainWindow(QMainWindow):
    """AetherNet Primary GUI Window"""

    def __init__(self):
        super().__init__()
        # Window Title and Clean Initial Centered Geometry
        self.setWindowTitle("AetherNet - WiFi & Ağ Yönetim Hub'ı")
        
        screen_geo = QGuiApplication.primaryScreen().geometry()
        w, h = 1280, 800
        x = (screen_geo.width() - w) // 2
        y = (screen_geo.height() - h) // 2
        self.setGeometry(x, y, w, h)
        self.setMinimumSize(1100, 700)

        # Set Window Icon
        icon_path = get_asset_path("assets/icon.ico")
        if not icon_path.exists():
            icon_path = get_asset_path("assets/logo.png")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Platform adapter & i18n
        self.platform_adapter = get_platform_adapter()
        self.i18n = I18nManager("tr")

        # Apply Initial Theme
        self.current_theme = "cyber_dark"
        self.setStyleSheet(ThemeManager.get_theme_stylesheet(self.current_theme))

        # Central Root Layout
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Sidebar Panel
        self.sidebar = Sidebar(self.i18n)
        self.sidebar.nav_changed.connect(self._on_navigation)
        root_layout.addWidget(self.sidebar)

        # Right Main Content (TopBar + FadingStackedWidget)
        right_container = QWidget()
        right_container.setObjectName("RightContainer")
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Top Bar
        self.top_bar = TopBar(self.i18n)
        self.top_bar.refresh_requested.connect(self._on_timer_tick)
        self.top_bar.theme_changed.connect(self._on_theme_changed)
        right_layout.addWidget(self.top_bar)

        # Animated Fading Stacked Views Container
        self.stacked_widget = FadingStackedWidget()
        right_layout.addWidget(self.stacked_widget)

        root_layout.addWidget(right_container)

        # Initialize Views
        self.view_dashboard = DashboardView(self.platform_adapter, self.i18n)
        self.view_wifi = WifiView(self.platform_adapter, self.i18n)
        self.view_profiles = ProfilesView(self.platform_adapter, self.i18n)
        self.view_env = EnvironmentView(self.platform_adapter, self.i18n)
        self.view_discovery = DiscoveryView(self.platform_adapter, self.i18n)
        self.view_tools = ToolsView(self.platform_adapter, self.i18n)
        self.view_security = SecurityView(self.platform_adapter, self.i18n)
        self.view_pentest = PentestView(self.platform_adapter, self.i18n)
        self.view_topology = TopologyView(self.platform_adapter, self.i18n)
        self.view_router = RouterView(self.platform_adapter, self.i18n)
        self.view_settings = SettingsView(self.i18n)
        self.view_logs = LogsView(self.i18n)
        self.view_api_hub = APIHubView(self.platform_adapter, self.i18n)

        # Mapping dict from nav index to view widget
        self.view_map = {
            0: self.view_dashboard,
            1: self.view_wifi,
            2: self.view_profiles,
            3: self.view_env,
            4: self.view_discovery,
            5: self.view_tools,
            6: self.view_security,
            7: self.view_pentest,
            8: self.view_topology,
            9: self.view_settings,
            10: self.view_logs,
            11: self.view_router,
            12: self.view_api_hub
        }

        # Add all views to stacked widget
        for i in self.view_map.keys():
            self.stacked_widget.addWidget(self.view_map[i])

        # Setup Refresh Timer (Every 3 seconds)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timer_tick)
        self.timer.start(3000)

        # Initial refresh
        self._on_timer_tick()

    def closeEvent(self, event):
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        super().closeEvent(event)

    def _on_navigation(self, index: int):

        if index in self.view_map:
            widget = self.view_map[index]
            stacked_idx = self.stacked_widget.indexOf(widget)
            if stacked_idx >= 0:
                self.stacked_widget.setCurrentIndex(stacked_idx)

    def _on_theme_changed(self, theme_name: str):
        self.current_theme = theme_name
        self.setStyleSheet(ThemeManager.get_theme_stylesheet(theme_name))
        self.sidebar.update_theme(theme_name)
        self.top_bar.update_theme(theme_name)

    def _on_timer_tick(self):
        # Refresh dashboard live metrics
        self.view_dashboard.refresh_data()

        # Update top bar status
        conn = self.platform_adapter.get_current_connection()
        if conn:
            ifaces = self.platform_adapter.get_interfaces()
            active_ip = next((i.ipv4_address for i in ifaces if i.is_enabled and i.ipv4_address), "")
            self.top_bar.update_status(True, conn.ssid, active_ip)
        else:
            self.top_bar.update_status(False)
