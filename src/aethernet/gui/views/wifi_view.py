from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit
)
from PySide6.QtCore import Qt

class WifiView(QWidget):
    """Detailed WiFi Interface & Active Connection Inspector View"""

    def __init__(self, platform_adapter, i18n, parent=None):
        super().__init__(parent)
        self.adapter = platform_adapter
        self.i18n = i18n

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header_layout = QHBoxLayout()
        lbl_header = QLabel("📶 WiFi Adaptör ve Bağlantı Yönetimi")
        lbl_header.setStyleSheet("font-size: 20px; font-weight: bold; color: #f8fafc;")
        header_layout.addWidget(lbl_header)

        header_layout.addStretch()

        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("🔎 Adaptör Ara...")
        self.input_search.setFixedWidth(200)
        self.input_search.textChanged.connect(self._filter_table)
        header_layout.addWidget(self.input_search)

        btn_refresh = QPushButton("🔄 Yenile")
        btn_refresh.setProperty("class", "btn-secondary")
        btn_refresh.clicked.connect(self.refresh_data)
        header_layout.addWidget(btn_refresh)

        layout.addLayout(header_layout)

        # Table of Network Interfaces
        lbl_iface_title = QLabel("Sistemdeki Ağ Adaptörleri")
        lbl_iface_title.setStyleSheet("font-weight: bold; color: #00f2fe;")
        layout.addWidget(lbl_iface_title)

        self.table_interfaces = QTableWidget()
        self.table_interfaces.setColumnCount(6)
        self.table_interfaces.setHorizontalHeaderLabels([
            "Adaptör Adı", "MAC Adresi", "İşletim Durumu", "IPv4 Adresi", "Alt Ağ Maskesi", "WiFi Desteği"
        ])
        self.table_interfaces.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_interfaces)

        # Connection Controls
        ctrl_layout = QHBoxLayout()
        self.btn_disconnect = QPushButton("🔌 Bağlantıyı Kes")
        self.btn_disconnect.setProperty("class", "btn-danger")
        self.btn_disconnect.clicked.connect(self._disconnect)
        ctrl_layout.addWidget(self.btn_disconnect)
        ctrl_layout.addStretch()

        layout.addLayout(ctrl_layout)
        self.refresh_data()

    def refresh_data(self):
        ifaces = self.adapter.get_interfaces()
        self.table_interfaces.setRowCount(len(ifaces))

        for idx, iface in enumerate(ifaces):
            self.table_interfaces.setItem(idx, 0, QTableWidgetItem(iface.name))
            self.table_interfaces.setItem(idx, 1, QTableWidgetItem(iface.mac_address))
            status_item = QTableWidgetItem("🟢 Etkin" if iface.is_enabled else "🔴 Devre Dışı")
            self.table_interfaces.setItem(idx, 2, status_item)
            self.table_interfaces.setItem(idx, 3, QTableWidgetItem(iface.ipv4_address or "---"))
            self.table_interfaces.setItem(idx, 4, QTableWidgetItem(iface.ipv4_subnet or "---"))
            wifi_item = QTableWidgetItem("📶 Evet (WiFi)" if iface.is_wifi else "🔌 Ethernet")
            self.table_interfaces.setItem(idx, 5, wifi_item)

    def _filter_table(self, query: str):
        query = query.lower()
        for row in range(self.table_interfaces.rowCount()):
            item = self.table_interfaces.item(row, 0)
            if item and query in item.text().lower():
                self.table_interfaces.setRowHidden(row, False)
            else:
                self.table_interfaces.setRowHidden(row, True)

    def _disconnect(self):
        self.adapter.disconnect()
        self.refresh_data()
