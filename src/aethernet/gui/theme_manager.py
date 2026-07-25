class ThemeManager:
    """Cyber-Noir / Digital Fortress PySide6 QSS StyleSheet Generator"""

    CYBER_DARK_QSS = """
    QMainWindow {
        background-color: #0b0e14;
        color: #e2e8f0;
        font-family: 'Segoe UI', 'Inter', sans-serif;
    }
    
    QWidget {
        background-color: #0b0e14;
        color: #e2e8f0;
        font-size: 13px;
    }

    /* Sidebar Navigation */
    #Sidebar {
        background-color: #10141d;
        border-right: 1px solid #1e2638;
        min-width: 220px;
        max-width: 220px;
    }

    #SidebarHeader {
        color: #00f2fe;
        font-size: 18px;
        font-weight: bold;
        padding: 16px;
    }

    QPushButton.nav-btn {
        background-color: transparent;
        color: #94a3b8;
        border: none;
        border-radius: 8px;
        padding: 12px 16px;
        text-align: left;
        font-size: 14px;
        font-weight: 500;
    }

    QPushButton.nav-btn:hover {
        background-color: #1a2234;
        color: #00f2fe;
    }

    QPushButton.nav-btn:checked, QPushButton.nav-btn.active {
        background-color: #1e293d;
        color: #00f2fe;
        border-left: 4px solid #00f2fe;
        font-weight: bold;
    }

    /* Stat Cards */
    QFrame.stat-card {
        background-color: #141a26;
        border: 1px solid #1e293d;
        border-radius: 12px;
        padding: 16px;
    }

    QFrame.stat-card:hover {
        border: 1px solid #00f2fe;
    }

    QLabel.stat-title {
        color: #64748b;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
    }

    QLabel.stat-value {
        color: #f8fafc;
        font-size: 22px;
        font-weight: bold;
    }

    /* Primary Buttons */
    QPushButton.btn-primary {
        background-color: #00f2fe;
        color: #0b0e14;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
    }

    QPushButton.btn-primary:hover {
        background-color: #38bdf8;
    }

    /* Secondary / Action Buttons */
    QPushButton.btn-secondary {
        background-color: #1e293d;
        color: #e2e8f0;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 8px 16px;
    }

    QPushButton.btn-secondary:hover {
        background-color: #334155;
        border-color: #00f2fe;
    }

    /* Tables & Trees */
    QTableWidget, QTreeWidget {
        background-color: #141a26;
        border: 1px solid #1e293d;
        border-radius: 8px;
        gridline-color: #1e293d;
        color: #e2e8f0;
    }

    QHeaderView::section {
        background-color: #10141d;
        color: #94a3b8;
        padding: 8px;
        border: none;
        border-bottom: 1px solid #1e293d;
        font-weight: bold;
    }

    QTableWidget::item:selected {
        background-color: #1e293d;
        color: #00f2fe;
    }

    /* Input Fields */
    QLineEdit, QComboBox, QTextEdit {
        background-color: #141a26;
        border: 1px solid #1e293d;
        border-radius: 6px;
        color: #f8fafc;
        padding: 8px;
    }

    QLineEdit:focus, QComboBox:focus {
        border: 1px solid #00f2fe;
    }

    /* Scrollbars */
    QScrollBar:vertical {
        background-color: #0b0e14;
        width: 8px;
    }

    QScrollBar::handle:vertical {
        background-color: #1e293d;
        border-radius: 4px;
    }

    QScrollBar::handle:vertical:hover {
        background-color: #00f2fe;
    }
    """

    @classmethod
    def get_theme_stylesheet(cls, theme_name: str = "cyber_dark") -> str:
        return cls.CYBER_DARK_QSS
