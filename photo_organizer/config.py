"""設定ファイル管理"""

import json
import os
from typing import Dict, List, Any


class Config:
    """設定管理クラス"""

    DEFAULT_CONFIG = {
        "raw_dir": "ARW",
        "jpg_dir": "JPG",
        "raw_extensions": [".arw"],
        "jpg_extensions": [".jpg", ".jpeg"],
        "orphan_dir": "orphans",
        "default_copy": False,
        "default_isolate_orphans": False,
        "default_dry_run": False,
    }

    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込む"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                # デフォルト値とマージ
                return {**self.DEFAULT_CONFIG, **config}
            except (json.JSONDecodeError, IOError):
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()

    def save_config(self) -> None:
        """設定をファイルに保存"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"設定保存エラー: {e}")

    def get(self, key: str, default=None):
        """設定値を取得"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """設定値を設定"""
        self.config[key] = value
