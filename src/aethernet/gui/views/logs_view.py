import os
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QTextEdit, QFrame, QFileDialog
)
from PySide6.QtCore import Qt, QTimer, QUrl, QSize
from PySide6.QtGui import QGuiApplication, QDesktopServices
from aethernet.utils.session_manager import SessionManager
from aethernet.gui.components.stat_card import StatCard
from aethernet.gui.icon_manager import IconManager

class LogsView(QWidget):
    """Application Logs & Execution Sessions Inspector View with Vector Icons"""

    def __init__(self, i18n, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.logs_dir = Path("logs")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header Title
        header_layout = QHBoxLayout()
        lbl_header = QLabel("Loglar ve Oturum Geçmişi (Session & Error Inspector)")
        lbl_header.setStyleSheet("font-size: 20px; font-weight: bold; color: #f8fafc;")
        header_layout.addWidget(lbl_header)

        header_layout.addStretch()

        btn_open_folder = QPushButton(" Log Klasörünü Aç")
        btn_open_folder.setIcon(IconManager.get_icon("folder", color="#00f2fe", size=16))
        btn_open_folder.setIconSize(QSize(16, 16))
        btn_open_folder.setProperty("class", "btn-secondary")
        btn_open_folder.clicked.connect(self._open_log_folder)
        header_layout.addWidget(btn_open_folder)

        layout.addLayout(header_layout)

        # Session Metrics Banner
        banner_card = QFrame()
        banner_card.setProperty("class", "glass-panel")
        banner_card.setStyleSheet("background-color: #0e131f; border: 1px solid #1a2336; border-radius: 12px; padding: 14px;")
        banner_layout = QHBoxLayout(banner_card)

        self.card_session_id = StatCard("AKTİF OTURUM", "--", "Session ID", "#00f2fe")
        self.card_ram_usage = StatCard("BELLEK (RAM) KULLANIMI", "-- MB", "Sistem RAM", "#38bdf8")
        self.card_ops_count = StatCard("TOPLAM İŞLEM SAYISI", "--", "İşlem Sayacı", "#4ade80")
        self.card_errors_count = StatCard("HATALAR / UYARILAR", "0 / 0", "Hata Durumu", "#f43f5e")

        banner_layout.addWidget(self.card_session_id)
        banner_layout.addWidget(self.card_ram_usage)
        banner_layout.addWidget(self.card_ops_count)
        banner_layout.addWidget(self.card_errors_count)

        layout.addWidget(banner_card)

        # Controls Row: Session Picker + Search + Export
        ctrl_card = QFrame()
        ctrl_card.setProperty("class", "glass-panel")
        ctrl_card.setStyleSheet("background-color: #0e131f; border: 1px solid #1a2336; border-radius: 10px; padding: 12px;")
        ctrl_layout = QHBoxLayout(ctrl_card)

        ctrl_layout.addWidget(QLabel("Oturum Seçin:"))
        self.combo_sessions = QComboBox()
        self.combo_sessions.setMinimumWidth(220)
        self.combo_sessions.currentTextChanged.connect(self._on_session_selected)
        ctrl_layout.addWidget(self.combo_sessions)

        ctrl_layout.addSpacing(16)
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Log Filtrele / Ara...")
        self.input_search.textChanged.connect(self._filter_log_text)
        ctrl_layout.addWidget(self.input_search)

        btn_copy = QPushButton(" Kopyala")
        btn_copy.setIcon(IconManager.get_icon("copy", color="#38bdf8", size=16))
        btn_copy.setIconSize(QSize(16, 16))
        btn_copy.setProperty("class", "btn-secondary")
        btn_copy.clicked.connect(lambda: QGuiApplication.clipboard().setText(self.txt_log.toPlainText()))
        ctrl_layout.addWidget(btn_copy)

        btn_export = QPushButton(" Dışa Aktar")
        btn_export.setIcon(IconManager.get_icon("export", color="#00f2fe", size=16))
        btn_export.setIconSize(QSize(16, 16))
        btn_export.setProperty("class", "btn-secondary")
        btn_export.clicked.connect(self._export_log_file)
        ctrl_layout.addWidget(btn_export)

        layout.addWidget(ctrl_card)

        # Log Output Box
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setProperty("class", "terminal-out")
        layout.addWidget(self.txt_log)

        # Timer for live log updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_log_view)
        self.timer.start(2000)

        self._populate_sessions()
        self.refresh_log_view()

    def _populate_sessions(self):
        self.combo_sessions.blockSignals(True)
        self.combo_sessions.clear()

        sessions = SessionManager.list_past_sessions(self.logs_dir)
        self.combo_sessions.addItem("Aktif Canlı Oturum (latest.log)")

        for sess in sessions:
            sid = sess.get("session_id", "Unknown")
            start = sess.get("start_time", "").split(".")[0].replace("T", " ")
            errs = sess.get("error_count", 0)
            label = f"Oturum: {start} | Hata: {errs}"
            self.combo_sessions.addItem(label, sid)

        self.combo_sessions.blockSignals(False)

    def _on_session_selected(self, text: str):
        self.refresh_log_view()

    def refresh_log_view(self):
        curr_session = SessionManager.get_current()
        if curr_session:
            sys_snap = curr_session.get_system_snapshot()
            self.card_session_id.set_value(curr_session.session_id[:16], "Aktif")
            self.card_ram_usage.set_value(f"{sys_snap['ram_used_mb']} MB", f"CPU: {sys_snap['cpu_percent']}%")
            self.card_ops_count.set_value(str(curr_session.operation_count))
            self.card_errors_count.set_value(f"{curr_session.error_count} Hata / {curr_session.warning_count} Uyarı")

        # Load log content
        sel_idx = self.combo_sessions.currentIndex()
        if sel_idx <= 0:
            target_log = self.logs_dir / "latest.log"
        else:
            sid = self.combo_sessions.currentData()
            target_log = self.logs_dir / "sessions" / f"session_{sid}.log"

        if not target_log.exists() and curr_session:
            target_log = curr_session.session_log_path

        if target_log and target_log.exists():
            try:
                with open(target_log, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                
                query = self.input_search.text().strip().lower()
                if query:
                    lines = [line for line in content.splitlines() if query in line.lower()]
                    content = "\n".join(lines)
                
                self.txt_log.setText(content)
                self.txt_log.verticalScrollBar().setValue(self.txt_log.verticalScrollBar().maximum())
            except Exception as e:
                self.txt_log.setText(f"Log dosyası okunamadı: {e}")

    def _filter_log_text(self, query: str):
        self.refresh_log_view()

    def _open_log_folder(self):
        log_path = self.logs_dir.resolve()
        if sys.platform == "win32":
            os.startfile(log_path)
        else:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(log_path)))

    def _export_log_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Log Dosyasını Dışa Aktar", "aethernet_log_export.txt", "Text Files (*.txt);;All Files (*)")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.txt_log.toPlainText())
