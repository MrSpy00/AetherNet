from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QLineEdit
)
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import Qt

class ProfilesView(QWidget):
    """Saved WiFi Profiles Manager & Password Revealer View"""

    def __init__(self, platform_adapter, i18n, parent=None):
        super().__init__(parent)
        self.adapter = platform_adapter
        self.i18n = i18n

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header_layout = QHBoxLayout()
        lbl_header = QLabel("🔑 Kayıtlı WiFi Profilleri")
        lbl_header.setStyleSheet("font-size: 20px; font-weight: bold; color: #f8fafc;")
        header_layout.addWidget(lbl_header)

        header_layout.addStretch()

        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("🔎 Profil Ara...")
        self.input_search.setFixedWidth(200)
        self.input_search.textChanged.connect(self._filter_table)
        header_layout.addWidget(self.input_search)

        btn_show_passwords = QPushButton("🔑 Kayıtlı Şifreleri Göster")
        btn_show_passwords.setProperty("class", "btn-primary")
        btn_show_passwords.clicked.connect(self._load_profiles_with_passwords)
        header_layout.addWidget(btn_show_passwords)

        layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Profil / SSID", "Güvenlik Tipi", "Otomatik Bağlanma", "Kayıtlı Parola"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.load_profiles(include_passwords=False)

    def load_profiles(self, include_passwords: bool = False):
        profiles = self.adapter.get_saved_profiles(include_passwords=include_passwords)
        self.table.setRowCount(len(profiles))

        for idx, prof in enumerate(profiles):
            self.table.setItem(idx, 0, QTableWidgetItem(f"📶 {prof.name}"))
            self.table.setItem(idx, 1, QTableWidgetItem(prof.security_type))
            self.table.setItem(idx, 2, QTableWidgetItem("🟢 Evet" if prof.auto_connect else "⚪ Hayır"))
            pass_val = prof.password if prof.password else ("••••••••" if not include_passwords else "<Açık Ağ / Şifresiz>")
            self.table.setItem(idx, 3, QTableWidgetItem(pass_val))

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
        QMessageBox.information(self, "Başarılı", "Kayıtlı WiFi şifreleri başarıyla okundu.")
