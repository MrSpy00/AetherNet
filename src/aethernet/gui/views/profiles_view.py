from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QProgressBar, QMessageBox
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
    """Saved WiFi Profiles Manager & Fast Password Revealer View with Vector Icons & Action Controls"""

    def __init__(self, platform_adapter, i18n, parent=None):
        super().__init__(parent)
        self.adapter = platform_adapter
        self.i18n = i18n
        self.loader_thread = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        header_layout = QHBoxLayout()
        lbl_header = QLabel("Kayıtlı WiFi Profilleri & Şifre Yöneticisi")
        lbl_header.setStyleSheet("font-size: 20px; font-weight: bold; color: #f8fafc;")
        header_layout.addWidget(lbl_header)

        header_layout.addStretch()

        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText(" Profil Ara...")
        self.input_search.setFixedWidth(220)
        self.input_search.setStyleSheet("padding: 6px 10px; background-color: #0d081a; color: white; border: 1px solid #331f54; border-radius: 6px;")
        self.input_search.textChanged.connect(self._filter_table)
        header_layout.addWidget(self.input_search)

        self.btn_show_passwords = QPushButton(" Kayıtlı Şifreleri Göster")
        self.btn_show_passwords.setIcon(IconManager.get_icon("key", color="#ffffff", size=16))
        self.btn_show_passwords.setIconSize(QSize(16, 16))
        self.btn_show_passwords.setStyleSheet("padding: 8px 14px; background-color: #7c3aed; color: white; font-weight: bold; border-radius: 6px;")
        self.btn_show_passwords.clicked.connect(self._load_profiles_with_passwords)
        header_layout.addWidget(self.btn_show_passwords)

        layout.addLayout(header_layout)

        # Sleek progress bar during background load
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(4)
        self.progress.setStyleSheet("QProgressBar { background-color: #0d081a; border: none; } QProgressBar::chunk { background-color: #00f2fe; }")
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Profil / SSID", "Güvenlik Tipi", "Otomatik Bağlanma", "Kayıtlı Parola", "İşlem / Aksiyonlar"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        self.table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        layout.addWidget(self.table)

        self.load_profiles(include_passwords=False)

    def closeEvent(self, event):
        if hasattr(self, 'loader_thread') and self.loader_thread is not None and self.loader_thread.isRunning():
            self.loader_thread.quit()
            self.loader_thread.wait(1000)
        super().closeEvent(event)

    def load_profiles(self, include_passwords: bool = False):
        self.btn_show_passwords.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)  # Indeterminate loading state
        
        self.loader_thread = ProfileLoaderThread(self.adapter, include_passwords)
        self.loader_thread.profiles_loaded.connect(self._on_profiles_loaded)
        self.loader_thread.start()

    def _on_profiles_loaded(self, profiles: list):
        self.progress.setVisible(False)
        self.btn_show_passwords.setEnabled(True)
        self.table.setRowCount(len(profiles))

        for idx, prof in enumerate(profiles):
            self.table.setRowHeight(idx, 44)

            item_name = QTableWidgetItem(prof.name)
            item_name.setIcon(IconManager.get_icon("wifi", color="#a855f7", size=16))
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

            # Rich Action Container with 3 Action Buttons
            cell_action = QWidget()
            action_layout = QHBoxLayout(cell_action)
            action_layout.setContentsMargins(4, 2, 4, 2)
            action_layout.setSpacing(6)

            # 1. Connect Button
            btn_connect = QPushButton(" Bağlan")
            btn_connect.setIcon(IconManager.get_icon("wifi", color="#00f2fe", size=12))
            btn_connect.setIconSize(QSize(12, 12))
            btn_connect.setStyleSheet("padding: 4px 8px; background-color: #1a102b; color: #00f2fe; border: 1px solid #331f54; border-radius: 4px; font-size: 11px;")
            btn_connect.clicked.connect(lambda _, ssid=prof.name: self._connect_to_profile(ssid))
            action_layout.addWidget(btn_connect)

            # 2. Copy Password Button
            btn_copy = QPushButton(" Kopyala")
            btn_copy.setIcon(IconManager.get_icon("copy", color="#a855f7", size=12))
            btn_copy.setIconSize(QSize(12, 12))
            btn_copy.setStyleSheet("padding: 4px 8px; background-color: #1a102b; color: #a855f7; border: 1px solid #331f54; border-radius: 4px; font-size: 11px;")
            btn_copy.clicked.connect(lambda _, p=pass_val: self._copy_password(p))
            action_layout.addWidget(btn_copy)

            # 3. Delete Profile Button
            btn_delete = QPushButton(" Sil")
            btn_delete.setIcon(IconManager.get_icon("trash", color="#f43f5e", size=12))
            btn_delete.setIconSize(QSize(12, 12))
            btn_delete.setStyleSheet("padding: 4px 8px; background-color: #1a102b; color: #f43f5e; border: 1px solid #331f54; border-radius: 4px; font-size: 11px;")
            btn_delete.clicked.connect(lambda _, ssid=prof.name: self._delete_profile(ssid))
            action_layout.addWidget(btn_delete)

            self.table.setCellWidget(idx, 4, cell_action)

    def _connect_to_profile(self, ssid: str):
        if self.adapter.connect_profile(ssid):
            ToastNotification.show_toast(self, f"✓ '{ssid}' Ağında Bağlantı Başlatıldı", is_success=True)
        else:
            ToastNotification.show_toast(self, f"'{ssid}' Bağlantı İsteği Gönderildi", is_success=True)

    def _copy_password(self, password: str):
        if password and not password.startswith("•"):
            QGuiApplication.clipboard().setText(password)
            ToastNotification.show_toast(self, "✓ WiFi Parolası Panoya Kopyalandı!", is_success=True)
        else:
            ToastNotification.show_toast(self, "Önce 'Kayıtlı Şifreleri Göster' Butonuna Tıklayın", is_success=False)

    def _delete_profile(self, ssid: str):
        reply = QMessageBox.question(
            self, "Profil Silinsin mi?",
            f"'{ssid}' WiFi profilini sistemden silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.adapter.delete_profile(ssid):
                ToastNotification.show_toast(self, f"✓ '{ssid}' Profili Başarıyla Silindi", is_success=True)
                self.load_profiles(include_passwords=False)
            else:
                ToastNotification.show_toast(self, f"Profil Silinemedi veya Zaten Yok", is_success=False)

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
