import os
import sys
import uuid
import json
import time
import psutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

class SessionManager:
    """Manages application execution sessions, system memory metrics, and log records."""

    _current_session: Optional["SessionManager"] = None

    def __init__(self, logs_dir: Path = Path("logs")):
        self.logs_dir = logs_dir
        self.sessions_dir = self.logs_dir / "sessions"
        self.crashes_dir = self.logs_dir / "crashes"

        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.crashes_dir.mkdir(parents=True, exist_ok=True)

        self.session_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        self.start_time = datetime.now()
        self.session_log_path = self.sessions_dir / f"session_{self.session_id}.log"
        self.session_json_path = self.sessions_dir / f"session_{self.session_id}.json"

        self.error_count = 0
        self.warning_count = 0
        self.operation_count = 0
        self.log_entries: List[Dict[str, Any]] = []

        SessionManager._current_session = self

    @classmethod
    def get_current(cls) -> Optional["SessionManager"]:
        return cls._current_session

    def get_system_snapshot(self) -> Dict[str, Any]:
        """Captures live CPU, Memory, and System info."""
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        return {
            "python_version": sys.version,
            "platform": sys.platform,
            "executable": sys.executable,
            "process_id": os.getpid(),
            "cpu_percent": psutil.cpu_percent(interval=None),
            "ram_used_mb": round(mem_info.rss / (1024 * 1024), 2),
            "system_ram_percent": psutil.virtual_memory().percent,
            "active_threads": process.num_threads()
        }

    def record_operation(self, op_name: str, status: str = "SUCCESS", details: str = ""):
        self.operation_count += 1
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": op_name,
            "status": status,
            "details": details
        }
        self.log_entries.append(entry)
        self._save_session_metadata()

    def record_error(self, is_warning: bool = False):
        if is_warning:
            self.warning_count += 1
        else:
            self.error_count += 1
        self._save_session_metadata()

    def record_crash(self, exc_type, exc_value, exc_traceback_str):
        crash_id = f"crash_{self.session_id}"
        crash_file = self.crashes_dir / f"{crash_id}.log"

        sys_snap = self.get_system_snapshot()

        crash_data = (
            f"=======================================================================\n"
            f"⚡ AETHERNET CRASH REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"=======================================================================\n"
            f"Session ID     : {self.session_id}\n"
            f"Exception Type : {exc_type.__name__ if exc_type else 'Unknown'}\n"
            f"Exception Msg  : {exc_value}\n"
            f"Executable     : {sys_snap['executable']}\n"
            f"Python Ver     : {sys_snap['python_version']}\n"
            f"RAM Used       : {sys_snap['ram_used_mb']} MB\n"
            f"CPU Load       : {sys_snap['cpu_percent']} %\n"
            f"Active Threads : {sys_snap['active_threads']}\n"
            f"-----------------------------------------------------------------------\n"
            f"TRACEBACK DETAILS:\n"
            f"{exc_traceback_str}\n"
            f"=======================================================================\n"
        )

        with open(crash_file, "w", encoding="utf-8") as f:
            f.write(crash_data)

        latest_crash = self.crashes_dir / "crash_latest.log"
        with open(latest_crash, "w", encoding="utf-8") as f:
            f.write(crash_data)

        self.record_error(is_warning=False)

    def _save_session_metadata(self):
        metadata = {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "last_updated": datetime.now().isoformat(),
            "duration_seconds": round((datetime.now() - self.start_time).total_seconds(), 1),
            "operation_count": self.operation_count,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "system_snapshot": self.get_system_snapshot(),
            "log_file": str(self.session_log_path.name)
        }
        try:
            with open(self.session_json_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    @classmethod
    def list_past_sessions(cls, logs_dir: Path = Path("logs")) -> List[Dict[str, Any]]:
        sessions_dir = logs_dir / "sessions"
        if not sessions_dir.exists():
            return []

        results = []
        for json_file in sorted(sessions_dir.glob("session_*.json"), reverse=True):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    results.append(data)
            except Exception:
                continue
        return results
