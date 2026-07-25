class ThemeManager:
    """Cyber-Noir / Digital Fortress / Synthwave PySide6 QSS StyleSheet Generator"""

    CYBER_DARK_QSS = """
    QMainWindow, QStackedWidget, #CentralWidget, #RightContainer {
        background-color: #080b10;
        color: #e2e8f0;
        font-family: 'Segoe UI', 'Inter', system-ui, sans-serif;
    }
    
    QWidget {
        color: #e2e8f0;
        font-size: 13px;
        font-family: 'Segoe UI', 'Inter', system-ui, sans-serif;
    }

    QLabel {
        background: transparent;
        color: #e2e8f0;
    }

    QFrame {
        background-color: transparent;
    }

    /* Top Bar Header */
    #TopBar {
        background-color: #0d121c;
        border-bottom: 1px solid #182234;
        min-height: 56px;
        max-height: 56px;
        padding: 0 16px;
    }

    /* Sidebar Navigation */
    #Sidebar {
        background-color: #0a0e17;
        border-right: 1px solid #182234;
        min-width: 240px;
        max-width: 240px;
    }

    #SidebarHeader {
        color: #00f2fe;
        font-size: 18px;
        font-weight: 800;
        padding: 18px 16px 12px 16px;
        letter-spacing: 0.5px;
    }

    QLabel.section-label {
        color: #475569;
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 12px 16px 4px 16px;
        background: transparent;
    }

    QPushButton.nav-btn {
        background-color: transparent;
        color: #94a3b8;
        border: none;
        border-radius: 8px;
        padding: 10px 14px;
        text-align: left;
        font-size: 13.5px;
        font-weight: 600;
        margin: 2px 8px;
    }

    QPushButton.nav-btn:hover {
        background-color: #141c2e;
        color: #38bdf8;
    }

    QPushButton.nav-btn:checked, QPushButton.nav-btn.active {
        background-color: #16243b;
        color: #00f2fe;
        border-left: 3px solid #00f2fe;
        font-weight: bold;
    }

    /* Stat Cards */
    QFrame.stat-card {
        background-color: #0e131f;
        border: 1px solid #1a2336;
        border-radius: 12px;
        padding: 16px;
    }

    QFrame.stat-card:hover {
        border: 1px solid #00f2fe;
        background-color: #111827;
    }

    QLabel.stat-title {
        color: #64748b;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        background: transparent;
    }

    QLabel.stat-value {
        color: #f8fafc;
        font-size: 24px;
        font-weight: 800;
        background: transparent;
    }

    /* Content Cards & Panels */
    QFrame.glass-panel {
        background-color: #0e131f;
        border: 1px solid #1a2336;
        border-radius: 12px;
    }

    /* Buttons */
    QPushButton {
        border-radius: 7px;
        font-weight: 600;
        padding: 8px 16px;
    }

    QPushButton.btn-primary {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00c6ff, stop:1 #0072ff);
        color: #ffffff;
        border: none;
        padding: 9px 18px;
        font-weight: bold;
    }

    QPushButton.btn-primary:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #38bdf8, stop:1 #0284c7);
    }

    QPushButton.btn-primary:pressed {
        background-color: #0369a1;
    }

    QPushButton.btn-secondary {
        background-color: #141c2e;
        color: #e2e8f0;
        border: 1px solid #222f47;
        padding: 8px 16px;
    }

    QPushButton.btn-secondary:hover {
        background-color: #1a2742;
        border-color: #00f2fe;
        color: #00f2fe;
    }

    QPushButton.btn-danger {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ef4444, stop:1 #b91c1c);
        color: #ffffff;
        border: none;
        padding: 8px 16px;
    }

    QPushButton.btn-danger:hover {
        background-color: #dc2626;
    }

    /* Tables & Trees */
    QTableWidget, QTreeWidget {
        background-color: #0e131f;
        border: 1px solid #1a2336;
        border-radius: 10px;
        gridline-color: #162032;
        color: #e2e8f0;
        selection-background-color: #1a2942;
        selection-color: #00f2fe;
    }

    QTableWidget::item {
        padding: 8px;
        border-bottom: 1px solid #141c2e;
    }

    QTableWidget::item:hover {
        background-color: #131c2d;
    }

    QHeaderView::section {
        background-color: #0a0e17;
        color: #38bdf8;
        padding: 10px;
        border: none;
        border-bottom: 2px solid #1a2336;
        font-weight: 700;
        font-size: 12px;
        text-transform: uppercase;
    }

    /* Input Fields */
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
        background-color: #0a0e17;
        border: 1px solid #1d273c;
        border-radius: 7px;
        color: #f8fafc;
        padding: 8px 12px;
        selection-background-color: #00f2fe;
        selection-color: #080b10;
    }

    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
        border: 1px solid #00f2fe;
        background-color: #0d1320;
    }

    QComboBox::drop-down {
        border: none;
        width: 24px;
    }

    /* Modern Monospace Output Terminal */
    QTextEdit.terminal-out, QPlainTextEdit.terminal-out {
        background-color: #04060a;
        color: #00f2fe;
        border: 1px solid #162032;
        border-radius: 8px;
        font-family: 'Consolas', 'Fira Code', 'Courier New', monospace;
        font-size: 12.5px;
        padding: 12px;
        line-height: 1.5;
    }

    /* Sliders */
    QSlider::groove:horizontal {
        border: none;
        height: 6px;
        background: #141c2e;
        border-radius: 3px;
    }

    QSlider::sub-page:horizontal {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00c6ff, stop:1 #00f2fe);
        border-radius: 3px;
    }

    QSlider::handle:horizontal {
        background: #00f2fe;
        border: 2px solid #ffffff;
        width: 16px;
        height: 16px;
        margin: -5px 0;
        border-radius: 9px;
    }

    QSlider::handle:horizontal:hover {
        background: #38bdf8;
    }

    /* Progress Bar */
    QProgressBar {
        border: 1px solid #1a2336;
        border-radius: 6px;
        background-color: #0a0e17;
        text-align: center;
        color: #ffffff;
        font-weight: bold;
    }

    QProgressBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00c6ff, stop:1 #00f2fe);
        border-radius: 5px;
    }

    /* Tabs */
    QTabWidget::pane {
        border: 1px solid #1a2336;
        border-radius: 10px;
        background-color: #0e131f;
        top: -1px;
    }

    QTabBar::tab {
        background-color: #0a0e17;
        color: #94a3b8;
        border: 1px solid #1a2336;
        border-bottom: none;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        padding: 10px 18px;
        margin-right: 4px;
        font-weight: 600;
    }

    QTabBar::tab:hover {
        background-color: #121929;
        color: #38bdf8;
    }

    QTabBar::tab:selected {
        background-color: #0e131f;
        color: #00f2fe;
        border-top: 2px solid #00f2fe;
        font-weight: bold;
    }

    /* Scrollbars */
    QScrollBar:vertical {
        background-color: #080b10;
        width: 8px;
        margin: 0;
    }

    QScrollBar::handle:vertical {
        background-color: #1d273c;
        border-radius: 4px;
        min-height: 20px;
    }

    QScrollBar::handle:vertical:hover {
        background-color: #00f2fe;
    }

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }

    QScrollBar:horizontal {
        background-color: #080b10;
        height: 8px;
        margin: 0;
    }

    QScrollBar::handle:horizontal {
        background-color: #1d273c;
        border-radius: 4px;
        min-width: 20px;
    }

    QScrollBar::handle:horizontal:hover {
        background-color: #00f2fe;
    }

    /* Tooltips */
    QToolTip {
        background-color: #0f172a;
        color: #38bdf8;
        border: 1px solid #00f2fe;
        border-radius: 6px;
        padding: 6px 10px;
    }
    """

    DIGITAL_FORTRESS_QSS = CYBER_DARK_QSS.replace("#00f2fe", "#10b981").replace("#38bdf8", "#34d399").replace("#00c6ff", "#059669").replace("#0072ff", "#10b981")
    SYNTHWAVE_QSS = CYBER_DARK_QSS.replace("#00f2fe", "#f43f5e").replace("#38bdf8", "#ec4899").replace("#00c6ff", "#8b5cf6").replace("#0072ff", "#d946ef")

    @classmethod
    def get_theme_stylesheet(cls, theme_name: str = "cyber_dark") -> str:
        if theme_name == "digital_fortress":
            return cls.DIGITAL_FORTRESS_QSS
        elif theme_name == "synthwave":
            return cls.SYNTHWAVE_QSS
        return cls.CYBER_DARK_QSS
