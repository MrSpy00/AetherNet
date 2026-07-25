class ThemeManager:
    """Cyber-Noir / Digital Fortress / Synthwave / Solar Flare / Tokyo Night / Dracula Pro QSS Generator"""

    THEME_COLORS = {
        "cyber_dark": {
            "accent": "#00f2fe",
            "secondary": "#38bdf8",
            "bg_dark": "#080b10",
            "card_bg": "#0e131f",
            "grad_start": "#00c6ff",
            "grad_end": "#0072ff"
        },
        "digital_fortress": {
            "accent": "#10b981",
            "secondary": "#34d399",
            "bg_dark": "#060e0a",
            "card_bg": "#0b1913",
            "grad_start": "#059669",
            "grad_end": "#10b981"
        },
        "synthwave": {
            "accent": "#f43f5e",
            "secondary": "#ec4899",
            "bg_dark": "#0c0812",
            "card_bg": "#160e20",
            "grad_start": "#8b5cf6",
            "grad_end": "#d946ef"
        },
        "solar_flare": {
            "accent": "#f59e0b",
            "secondary": "#fbbf24",
            "bg_dark": "#0f0b06",
            "card_bg": "#1c140a",
            "grad_start": "#d97706",
            "grad_end": "#f59e0b"
        },
        "tokyo_night": {
            "accent": "#6366f1",
            "secondary": "#818cf8",
            "bg_dark": "#090a14",
            "card_bg": "#121428",
            "grad_start": "#4f46e5",
            "grad_end": "#6366f1"
        },
        "dracula_pro": {
            "accent": "#bd93f9",
            "secondary": "#ff79c6",
            "bg_dark": "#0d0d14",
            "card_bg": "#181824",
            "grad_start": "#6272a4",
            "grad_end": "#bd93f9"
        }
    }

    CYBER_DARK_QSS = """
    QMainWindow, QStackedWidget, #CentralWidget, #RightContainer {{
        background-color: {bg_dark};
        color: #e2e8f0;
        font-family: 'Segoe UI', 'Inter', system-ui, sans-serif;
    }}
    
    QWidget {{
        color: #e2e8f0;
        font-size: 13px;
        font-family: 'Segoe UI', 'Inter', system-ui, sans-serif;
    }}

    QLabel {{
        background: transparent;
        color: #e2e8f0;
    }}

    QFrame {{
        background-color: transparent;
    }}

    /* Top Bar Header */
    #TopBar {{
        background-color: {card_bg};
        border-bottom: 1px solid #182234;
        min-height: 56px;
        max-height: 56px;
        padding: 0 16px;
    }}

    /* Sidebar Navigation */
    #Sidebar {{
        background-color: {bg_dark};
        border-right: 1px solid #182234;
        min-width: 240px;
        max-width: 240px;
    }}

    #SidebarHeader {{
        color: {accent};
        font-size: 18px;
        font-weight: 800;
        letter-spacing: 0.5px;
        background: transparent;
    }}

    QLabel.section-label {{
        color: #475569;
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 12px 14px 4px 14px;
        background: transparent;
    }}

    QPushButton.nav-btn {{
        background-color: transparent;
        color: #94a3b8;
        border: none;
        border-radius: 8px;
        padding: 9px 12px;
        text-align: left;
        font-size: 13px;
        font-weight: 600;
        margin: 2px 6px;
    }}

    QPushButton.nav-btn:hover {{
        background-color: #141c2e;
        color: {secondary};
    }}

    QPushButton.nav-btn:checked, QPushButton.nav-btn.active {{
        background-color: #16243b;
        color: {accent};
        border-left: 3px solid {accent};
        font-weight: bold;
    }}

    /* Stat Cards */
    QFrame.stat-card {{
        background-color: {card_bg};
        border: 1px solid #1a2336;
        border-radius: 12px;
        padding: 14px;
    }}

    QFrame.stat-card:hover {{
        border: 1px solid {accent};
    }}

    QLabel.stat-title {{
        color: #64748b;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        background: transparent;
    }}

    QLabel.stat-value {{
        color: #f8fafc;
        font-size: 22px;
        font-weight: 800;
        background: transparent;
    }}

    /* Content Cards & Panels */
    QFrame.glass-panel {{
        background-color: {card_bg};
        border: 1px solid #1a2336;
        border-radius: 12px;
    }}

    /* Buttons */
    QPushButton {{
        border-radius: 7px;
        font-weight: 600;
        padding: 7px 14px;
        outline: none;
    }}

    QPushButton.btn-primary {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {grad_start}, stop:1 {grad_end});
        color: #ffffff;
        border: none;
        padding: 8px 16px;
        font-weight: bold;
    }}

    QPushButton.btn-primary:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {secondary}, stop:1 {accent});
    }}

    QPushButton.btn-secondary {{
        background-color: #141c2e;
        color: #e2e8f0;
        border: 1px solid #222f47;
        padding: 7px 14px;
    }}

    QPushButton.btn-secondary:hover {{
        background-color: #1a2742;
        border-color: {accent};
        color: {accent};
    }}

    /* Tables & Trees */
    QTableWidget, QTreeWidget {{
        background-color: {card_bg};
        border: 1px solid #1a2336;
        border-radius: 10px;
        gridline-color: #162032;
        color: #e2e8f0;
        outline: none;
        font-size: 12.5px;
    }}

    QTableWidget::item {{
        padding: 8px 12px;
        border-bottom: 1px solid #141c2e;
        outline: none;
        border: none;
    }}

    QTableWidget::item:focus, QTableWidget::item:selected {{
        outline: none;
        border: none;
        background-color: #16243b;
        color: {accent};
    }}

    QHeaderView::section {{
        background-color: {bg_dark};
        color: {secondary};
        padding: 9px 12px;
        border: none;
        border-bottom: 2px solid #1a2336;
        font-weight: 700;
        font-size: 11.5px;
        text-transform: uppercase;
        outline: none;
    }}

    /* Form Input Controls */
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
        background-color: #0a0e17;
        border: 1px solid #1d273c;
        border-radius: 6px;
        color: #f8fafc;
        padding: 6px 12px;
        min-height: 28px;
        selection-background-color: {accent};
        selection-color: #080b10;
    }}

    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
        border: 1px solid {accent};
        background-color: #0e131f;
    }}

    QComboBox QAbstractItemView {{
        background-color: #0e131f;
        border: 1px solid {accent};
        selection-background-color: #16243b;
        selection-color: {accent};
        color: #f8fafc;
        padding: 4px;
    }}

    /* Modern Monospace Output Terminal */
    QTextEdit.terminal-out, QPlainTextEdit.terminal-out {{
        background-color: #04060a;
        color: {accent};
        border: 1px solid #162032;
        border-radius: 8px;
        font-family: 'Consolas', 'Fira Code', 'Courier New', monospace;
        font-size: 12.5px;
        padding: 12px;
        line-height: 1.5;
    }}

    /* Sliders */
    QSlider::groove:horizontal {{
        border: none;
        height: 6px;
        background: #141c2e;
        border-radius: 3px;
    }}

    QSlider::sub-page:horizontal {{
        background: {accent};
        border-radius: 3px;
    }}

    QSlider::handle:horizontal {{
        background: {accent};
        border: 2px solid #ffffff;
        width: 14px;
        height: 14px;
        margin: -4px 0;
        border-radius: 7px;
    }}

    /* Tabs */
    QTabWidget::pane {{
        border: 1px solid #1a2336;
        border-radius: 10px;
        background-color: {card_bg};
        top: -1px;
    }}

    QTabBar::tab {{
        background-color: {bg_dark};
        color: #94a3b8;
        border: 1px solid #1a2336;
        border-bottom: none;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        padding: 9px 16px;
        margin-right: 4px;
        font-weight: 600;
    }}

    QTabBar::tab:selected {{
        background-color: {card_bg};
        color: {accent};
        border-top: 2px solid {accent};
        font-weight: bold;
    }}

    /* Scrollbars */
    QScrollBar:vertical {{
        background-color: {bg_dark};
        width: 8px;
        margin: 0;
    }}

    QScrollBar::handle:vertical {{
        background-color: #1d273c;
        border-radius: 4px;
        min-height: 20px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: {accent};
    }}
    """

    @classmethod
    def get_theme_stylesheet(cls, theme_name: str = "cyber_dark") -> str:
        palette = cls.THEME_COLORS.get(theme_name, cls.THEME_COLORS["cyber_dark"])
        return cls.CYBER_DARK_QSS.format(**palette)

    @classmethod
    def get_accent_color(cls, theme_name: str = "cyber_dark") -> str:
        palette = cls.THEME_COLORS.get(theme_name, cls.THEME_COLORS["cyber_dark"])
        return palette["accent"]
