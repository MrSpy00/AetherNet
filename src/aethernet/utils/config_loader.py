import os
import yaml
from pathlib import Path
from typing import Any, Dict
from loguru import logger

class ConfigManager:
    """YAML tabanlı konfigürasyon yöneticisi"""

    def __init__(self, config_path: str = "config/config.default.yaml"):
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            logger.warning(f"Konfigürasyon dosyası bulunamadı: {self.config_path}. Varsayılan değerler yükleniyor.")
            return {}

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}
            logger.info(f"Konfigürasyon yüklendi: {self.config_path}")
        except Exception as e:
            logger.error(f"Konfigürasyon okuma hatası: {e}")
            self._config = {}
        return self._config

    def get(self, key_path: str, default: Any = None) -> Any:
        """Noktalı sözdizimi ile değer getirme (ör. 'app.language')"""
        keys = key_path.split(".")
        val = self._config
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val

    def set(self, key_path: str, value: Any) -> None:
        """Değeri güncelle ve kaydet"""
        keys = key_path.split(".")
        d = self._config
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value

    def save(self) -> bool:
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(self._config, f, allow_unicode=True, default_flow_style=False)
            return True
        except Exception as e:
            logger.error(f"Konfigürasyon kaydetme hatası: {e}")
            return False
