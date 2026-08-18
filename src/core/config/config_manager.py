"""
設定の永続化
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import (
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    THEMES,
    AppConfig,
    UIConfig,
)

MAX_BACKUPS = 10


class ConfigManager:
    """設定ファイルの読み書きを行う"""

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Args:
            config_dir: 設定ファイル保存ディレクトリ
                （Noneの場合はホームディレクトリ/.my-data-backup）
        """
        self.config_dir = config_dir or (Path.home() / ".my-data-backup")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        self.backup_dir = self.config_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)

        self.config = AppConfig()
        self.load_config()

        if self.validate_config() and self.auto_fix_config():
            print("設定の問題を自動修正しました")

    # 読み書き

    def load_config(self):
        """設定を読み込み（ファイルが無ければデフォルトを保存）"""
        if not self.config_file.exists():
            self.save_config()
            return

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.config.update_from_dict(json.load(f))
        except Exception as e:
            print(f"設定読み込みエラー: {e}")
            print("デフォルト設定を使用します")

    def save_config(self, backup: bool = True) -> bool:
        """設定を保存"""
        try:
            if backup and self.config_file.exists():
                self._create_backup()

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config.to_dict(), f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"設定保存エラー: {e}")
            return False

    def update_ui_settings(self, **kwargs):
        """UI設定を更新（自動保存付き）"""
        known_keys = {"theme", "window_width", "window_height", "log_level"}

        updated = False
        for key, value in kwargs.items():
            if key in known_keys:
                setattr(self.config.ui, key, value)
                updated = True

        if updated:
            self.save_config()

    # バックアップ

    def _create_backup(self):
        """設定ファイルのバックアップを作成"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy2(self.config_file, self.backup_dir / f"config_{timestamp}.json")
            self._cleanup_old_backups()
        except Exception as e:
            print(f"バックアップ作成エラー: {e}")

    def _cleanup_old_backups(self):
        """MAX_BACKUPS を超えた古いバックアップを削除"""
        backups = sorted(
            self.backup_dir.glob("config_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for backup in backups[MAX_BACKUPS:]:
            backup.unlink()

    # インポート・エクスポート

    def export_config(self, export_path: Path) -> bool:
        """設定をエクスポート"""
        try:
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(self.config.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"設定エクスポートエラー: {e}")
            return False

    def import_config(self, import_path: Path) -> bool:
        """設定をインポート"""
        try:
            with open(import_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._create_backup()
            self.config.update_from_dict(data)
            return self.save_config(backup=False)

        except Exception as e:
            print(f"設定インポートエラー: {e}")
            return False

    def reset_to_defaults(self) -> bool:
        """設定をデフォルトにリセット（バックアップ付き）"""
        try:
            self._create_backup()
            self.config.reset_to_defaults()
            return self.save_config(backup=False)
        except Exception as e:
            print(f"設定リセットエラー: {e}")
            return False

    # 情報・検証

    def get_config_info(self) -> Dict[str, Any]:
        """設定ファイルの情報を取得"""
        exists = self.config_file.exists()
        return {
            "config_file": str(self.config_file),
            "config_dir": str(self.config_dir),
            "backup_dir": str(self.backup_dir),
            "config_exists": exists,
            "config_size": self.config_file.stat().st_size if exists else 0,
            "last_modified": (
                datetime.fromtimestamp(self.config_file.stat().st_mtime).isoformat()
                if exists
                else None
            ),
            "backup_count": len(list(self.backup_dir.glob("config_*.json"))),
        }

    def validate_config(self) -> List[str]:
        """設定値を検証し、問題があればエラーメッセージを返す"""
        ui = self.config.ui
        errors = []

        if not isinstance(ui.window_width, int) or ui.window_width < MIN_WINDOW_WIDTH:
            errors.append(
                f"ウィンドウ幅は{MIN_WINDOW_WIDTH}以上の整数である必要があります"
            )

        if (
            not isinstance(ui.window_height, int)
            or ui.window_height < MIN_WINDOW_HEIGHT
        ):
            errors.append(
                f"ウィンドウ高さは{MIN_WINDOW_HEIGHT}以上の整数である必要があります"
            )

        if ui.theme not in THEMES:
            errors.append(
                f"テーマは {', '.join(THEMES)} のいずれかである必要があります"
            )

        return errors

    def auto_fix_config(self) -> bool:
        """不正な設定値をデフォルトに戻す"""
        ui = self.config.ui
        defaults = UIConfig()
        fixed = False

        if not isinstance(ui.window_width, int) or ui.window_width < MIN_WINDOW_WIDTH:
            ui.window_width = defaults.window_width
            fixed = True

        if (
            not isinstance(ui.window_height, int)
            or ui.window_height < MIN_WINDOW_HEIGHT
        ):
            ui.window_height = defaults.window_height
            fixed = True

        if ui.theme not in THEMES:
            ui.theme = defaults.theme
            fixed = True

        if fixed:
            self.save_config()

        return fixed
