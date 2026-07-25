from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QProgressBar
)
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import Qt, QThread, Signal, QSize
from aethernet.gui.icon_manager import IconManager
from aethernet.gui.components.toast import ToastNotification

class ProfileLoaderThread(QThread):
    profiles_loaded = Signal(list)

    def __init__(self, adapter, include_passwords: bool):
        super().__init__()
        self.adapter = adapter
        self.include_passwords = include_passwords

    def run(self):
        profiles = self.adapter.get_saved_profiles(include_passwords=self.include_passwords)
        self.profiles_loaded.emit(profiles)

class ProfilesView(QWidget):
    """Saved WiFi Profiles Manager & Fast Password Revealer View with Vector Icons"""

    def __init__(self, platform_adapter, i18n, parent=None):
        super().__init__(parent)
        self.adapter = platform_adapter
        self.i18n = i18n
        self.loader_thread = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header_layout = QHBoxLayout()
        lbl_header = QLabel("Kayıtlı WiFi Profilleri & Şifre Yöneticisi")
        lbl_header.setStyleSheet("font-size: 20px; font-weight: bold; color: #f8fafc;")
        header_layout.addWidget(lbl_header)

        header_layout.addStretch()

        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText(" Profil Ara...")
        self.input_search.setFixedWidth(200)
        self.input_search.textChanged.connect(self._filter_table)
        header_layout.addWidget(self.input_search)

        self.btn_show_passwords = QPushButton(" Kayıtlı Şifreleri Göster")
        self.btn_show_passwords.setIcon(IconManager.get_icon("key", color="#ffffff", size=16))
        self.btn_show_passwords.setIconSize(QSize(16, 16))
        self.btn_show_passwords.setProperty("class", "btn-primary")
        self.btn_show_passwords.clicked.connect(self._load_profiles_with_passwords)
        header_layout.addWidget(self.btn_show_passwords)

        layout.addLayout(header_layout)

        # Progress bar during background load
        self.progress = QProgressBar()
        self.progress.setValue(100)
        self.progress.setFixedHeight(6)
        layout.addWidget(self.progress)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Profil / SSID", "Güvenlik Tipi", "Otomatik Bağlanma", "Kayıtlı Parola", "İşlem"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        self.load_profiles(include_passwords=False)

    def closeEvent(self, event):
        if hasattr(self, 'loader_thread') and self.loader_thread is not None and self.loader_thread.isRunning():
            self.loader_thread.quit()
            self.loader_thread.wait(1000)
        super().closeEvent(event)

    def load_profiles(self, include_passwords: bool = False):

        self.btn_show_passwords.setEnabled(False)
        self.progress.setValue(30)
        
        self.loader_thread = ProfileLoaderThread(self.adapter, include_passwords)
        self.loader_thread.profiles_loaded.connect(self._on_profiles_loaded)
        self.loader_thread.start()

    def _on_profiles_loaded(self, profiles: list):
        self.progress.setValue(100)
        self.btn_show_passwords.setEnabled(True)
        self.table.setRowCount(len(profiles))

        for idx, prof in enumerate(profiles):
            item_name = QTableWidgetItem(prof.name)
            item_name.setIcon(IconManager.get_icon("wifi", color="#38bdf8", size=16))
            self.table.setItem(idx, 0, item_name)

            self.table.setItem(idx, 1, QTableWidgetItem(prof.security_type))

            auto_text = "Evet" if prof.auto_connect else "Hayır"
            item_auto = QTableWidgetItem(auto_text)
            color_auto = "#4ade80" if prof.auto_connect else "#94a3b8"
            item_auto.setIcon(IconManager.get_icon("wifi", color=color_auto, size=16))
            self.table.setItem(idx, 2, item_auto)

            pass_val = prof.password if prof.password else ("••••••••" if prof.password is None else "<Açık Ağ / Şifresiz>")
            item_pass = QTableWidgetItem(pass_val)
            self.table.setItem(idx, 3, item_pass)

            # Copy button in cell
            btn_copy = QPushButton(" Kopyala")
            btn_copy.setIcon(IconManager.get_icon("copy", color="#00f2fe", size=14))
            btn_copy.setIconSize(QSize(14, 14))
            btn_copy.setProperty("class", "btn-secondary")
            btn_copy.setFixedWidth(90)
            btn_copy.clicked.connect(lambda _, p=pass_val: self._copy_password(p))
            self.table.setCellWidget(idx, 4, btn_copy)

    def _copy_password(self, password: str):
        if password and not password.startswith("•"):
            QGuiApplication.clipboard().setText(password)
            ToastNotification.show_toast(self, "✓ WiFi Parolası Panoya Kopyalandı!", is_success=True)
        else:
            ToastNotification.show_toast(self, "Önce 'Kayıtlı Şifreleri Göster' Butonuna Tıklayın", is_success=False)

    def _on_cell_double_clicked(self, row: int, col: int):
        item = self.table.item(row, col)
        if item and item.text():
            QGuiApplication.clipboard().setText(item.text())
            ToastNotification.show_toast(self, f"✓ '{item.text()}' Panoya Kopyalandı!", is_success=True)

    def _filter_table(self, query: str):
        query = query.lower()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and query in item.text().lower():
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    def _load_profiles_with_passwords(self):
        self.load_profiles(include_passwords=True)
        ToastNotification.show_toast(self, "✓ WiFi Şifreleri Başarıyla Okundu", is_success=True)
