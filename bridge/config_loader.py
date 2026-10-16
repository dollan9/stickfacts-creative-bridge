import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.json"

class ConfigLoader:
    _instance: Optional["ConfigLoader"] = None
    _config_data: Dict[str, Any] = {}

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or CONFIG_PATH
        self.load()

    @classmethod
    def get_instance(cls) -> "ConfigLoader":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as f:
            self._config_data = json.load(f)
        return self._config_data

    @property
    def data(self) -> Dict[str, Any]:
        if not self._config_data:
            self.load()
        return self._config_data

    def get_app(self, app_key: str) -> Dict[str, Any]:
        apps = self.data.get("applications", {})
        if app_key not in apps:
            raise KeyError(f"Application '{app_key}' not found in config.json. Available: {list(apps.keys())}")
        return apps[app_key]

    def get_output_dir(self) -> Path:
        out_dir = PROJECT_ROOT / "output"
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir

def get_config() -> ConfigLoader:
    return ConfigLoader.get_instance()
