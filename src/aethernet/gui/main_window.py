from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QSystemTrayIcon, QMenu
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QIcon

from aethernet.platform import get_platform_adapter
from aethernet.gui.theme_manager import ThemeManager
from aethernet.gui.i18n_manager import I18nManager
from aethernet.gui.components.sidebar import Sidebar

from aethernet.gui.views.dashboard_view import DashboardView
from aethernet.gui.views.wifi_view import WifiView
from aethernet.gui.views.profiles_view import ProfilesView
from aethernet.gui.views.environment_view import EnvironmentView
from aethernet.gui.views.discovery_view import DiscoveryView
from aethernet.gui.views.tools_view import ToolsView
from aethernet.gui.views.security_view import SecurityView
from aethernet.gui.views.pentest_view import PentestView
from aethernet.gui.views.settings_view import SettingsView

class MainWindow(QMainWindow):
    """AetherNet Primary GUI Window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AetherNet - WiFi & Ağ Yönetim Hub'ı")
        self.resize(1280, 800)

        # Platform adapter & i18n
        self.platform_adapter = get_platform_adapter()
        self.i18n = I18nManager("tr")

        # Apply Cyber-Noir QSS Theme
        self.setStyleSheet(ThemeManager.get_theme_stylesheet("cyber_dark"))

        # Central Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar(self.i18n)
        self.sidebar.nav_changed.connect(self._on_navigation)
        main_layout.addWidget(self.sidebar)

        # Stacked Views Container
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Initialize Views
        self.view_dashboard = DashboardView(self.platform_adapter, self.i18n)
        self.view_wifi = WifiView(self.platform_adapter, self.i18n)
        self.view_profiles = ProfilesView(self.platform_adapter, self.i18n)
        self.view_env = EnvironmentView(self.platform_adapter, self.i18n)
        self.view_discovery = DiscoveryView(self.platform_adapter, self.i18n)
        self.view_tools = ToolsView(self.platform_adapter, self.i18n)
        self.view_security = SecurityView(self.platform_adapter, self.i18n)
        self.view_pentest = PentestView(self.platform_adapter, self.i18n)
        self.view_settings = SettingsView(self.i18n)

        self.stacked_widget.addWidget(self.view_dashboard)
        self.stacked_widget.addWidget(self.view_wifi)
        self.stacked_widget.addWidget(self.view_profiles)
        self.stacked_widget.addWidget(self.view_env)
        self.stacked_widget.addWidget(self.view_discovery)
        self.stacked_widget.addWidget(self.view_tools)
        self.stacked_widget.addWidget(self.view_security)
        self.stacked_widget.addWidget(self.view_pentest)
        self.stacked_widget.addWidget(self.view_settings)

        # Setup Refresh Timer (Every 3 seconds)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timer_tick)
        self.timer.start(3000)

        # Initial refresh
        self._on_timer_tick()

    def _on_navigation(self, index: int):
        self.stacked_widget.setCurrentIndex(index)

    def _on_timer_tick(self):
        # Refresh dashboard live metrics
        self.view_dashboard.refresh_data()
