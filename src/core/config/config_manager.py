"""
設定管理システム
"""

import json
import os
from dataclasses import dataclass, asdict, fields
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class AppConfig:
    """アプリケーション設定"""

    # UI設定
    theme: str = "auto"
    window_width: int = 1200
    window_height: int = 900
    log_level: str = "INFO"

    # Photo Organizer設定
    photo_default_dry_run: bool = True
    photo_default_preserve: bool = False
    photo_last_source_dir: str = ""
    photo_last_output_dir: str = ""

    # Move設定
    move_default_dry_run: bool = True
    move_default_date_dirs: bool = True
    move_default_type_dirs: bool = True
    move_last_import_dir: str = ""
    move_last_export_dir: str = ""

    # 最近使用したディレクトリ
    recent_directories: list = None

    # その他設定
    auto_save_config: bool = True
    show_confirmation_dialogs: bool = True
    max_recent_directories: int = 10

    def __post_init__(self):
        if self.recent_directories is None:
            self.recent_directories = []


class ConfigManager:
    """設定管理クラス"""

    def __init__(self, config_dir: Optional[Path] = None):
        """
        設定管理を初期化

        Args:
            config_dir: 設定ファイル保存ディレクトリ（Noneの場合はホームディレクトリ/.my-data-backup）
        """
        if config_dir is None:
            self.config_dir = Path.home() / ".my-data-backup"
        else:
            self.config_dir = config_dir

        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        self.backup_dir = self.config_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)

        self.config = AppConfig()
        self.load_config()

    def load_config(self) -> AppConfig:
        """設定を読み込み"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # データクラスのフィールドのみを更新
                field_names = {field.name for field in fields(AppConfig)}
                filtered_data = {k: v for k, v in data.items() if k in field_names}

                # 既存の設定を更新
                for key, value in filtered_data.items():
                    setattr(self.config, key, value)

                print(f"✅ 設定を読み込みました: {self.config_file}")
            else:
                print(f"📝 デフォルト設定を使用します: {self.config_file}")
                self.save_config()  # デフォルト設定を保存

        except Exception as e:
            print(f"⚠️ 設定読み込みエラー: {e}")
            print("📝 デフォルト設定を使用します")
            self.config = AppConfig()

        return self.config

    def save_config(self, backup: bool = True) -> bool:
        """設定を保存"""
        try:
            # バックアップ作成
            if backup and self.config_file.exists():
                self._create_backup()

            # 設定保存
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(asdict(self.config), f, indent=2, ensure_ascii=False)

            print(f"💾 設定を保存しました: {self.config_file}")
            return True

        except Exception as e:
            print(f"❌ 設定保存エラー: {e}")
            return False

    def _create_backup(self):
        """設定ファイルのバックアップを作成"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"config_backup_{timestamp}.json"

            import shutil

            shutil.copy2(self.config_file, backup_file)

            # 古いバックアップをクリーンアップ（最新10個を保持）
            self._cleanup_old_backups()

        except Exception as e:
            print(f"⚠️ バックアップ作成エラー: {e}")

    def _cleanup_old_backups(self, max_backups: int = 10):
        """古いバックアップファイルを削除"""
        try:
            backup_files = list(self.backup_dir.glob("config_backup_*.json"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            for backup_file in backup_files[max_backups:]:
                backup_file.unlink()

        except Exception as e:
            print(f"⚠️ バックアップクリーンアップエラー: {e}")

    def update_recent_directory(self, directory: str):
        """最近使用したディレクトリを更新"""
        if not directory or not Path(directory).exists():
            return

        # 既存の項目を削除
        if directory in self.config.recent_directories:
            self.config.recent_directories.remove(directory)

        # 先頭に追加
        self.config.recent_directories.insert(0, directory)

        # 最大数を超えた場合は削除
        if len(self.config.recent_directories) > self.config.max_recent_directories:
            self.config.recent_directories = self.config.recent_directories[
                : self.config.max_recent_directories
            ]

        if self.config.auto_save_config:
            self.save_config()

    def get_recent_directories(self, limit: Optional[int] = None) -> list:
        """最近使用したディレクトリを取得"""
        directories = [d for d in self.config.recent_directories if Path(d).exists()]

        # 存在しないディレクトリがあった場合は設定を更新
        if len(directories) != len(self.config.recent_directories):
            self.config.recent_directories = directories
            if self.config.auto_save_config:
                self.save_config()

        return directories[:limit] if limit else directories

    def update_photo_settings(self, **kwargs):
        """Photo Organizer設定を更新"""
        updated = False
        for key, value in kwargs.items():
            if hasattr(self.config, f"photo_{key}"):
                setattr(self.config, f"photo_{key}", value)
                updated = True

        if updated and self.config.auto_save_config:
            self.save_config()

    def update_move_settings(self, **kwargs):
        """Move設定を更新"""
        updated = False
        for key, value in kwargs.items():
            if hasattr(self.config, f"move_{key}"):
                setattr(self.config, f"move_{key}", value)
                updated = True

        if updated and self.config.auto_save_config:
            self.save_config()

    def update_ui_settings(self, **kwargs):
        """UI設定を更新"""
        updated = False
        valid_ui_settings = ["theme", "window_width", "window_height", "log_level"]

        for key, value in kwargs.items():
            if key in valid_ui_settings and hasattr(self.config, key):
                setattr(self.config, key, value)
                updated = True

        if updated and self.config.auto_save_config:
            self.save_config()

    def reset_to_defaults(self) -> bool:
        """設定をデフォルトにリセット"""
        try:
            self._create_backup()
            self.config = AppConfig()
            return self.save_config(backup=False)
        except Exception as e:
            print(f"❌ 設定リセットエラー: {e}")
            return False

    def export_config(self, export_path: Path) -> bool:
        """設定をエクスポート"""
        try:
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(asdict(self.config), f, indent=2, ensure_ascii=False)

            print(f"📤 設定をエクスポートしました: {export_path}")
            return True

        except Exception as e:
            print(f"❌ 設定エクスポートエラー: {e}")
            return False

    def import_config(self, import_path: Path) -> bool:
        """設定をインポート"""
        try:
            if not import_path.exists():
                print(f"❌ ファイルが存在しません: {import_path}")
                return False

            with open(import_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # バックアップ作成
            self._create_backup()

            # データクラスのフィールドのみを更新
            field_names = {field.name for field in fields(AppConfig)}
            filtered_data = {k: v for k, v in data.items() if k in field_names}

            # 新しい設定を適用
            for key, value in filtered_data.items():
                setattr(self.config, key, value)

            # 保存
            self.save_config(backup=False)

            print(f"📥 設定をインポートしました: {import_path}")
            return True

        except Exception as e:
            print(f"❌ 設定インポートエラー: {e}")
            return False

    def get_config_info(self) -> Dict[str, Any]:
        """設定情報を取得"""
        return {
            "config_file": str(self.config_file),
            "config_dir": str(self.config_dir),
            "backup_dir": str(self.backup_dir),
            "config_exists": self.config_file.exists(),
            "config_size": (
                self.config_file.stat().st_size if self.config_file.exists() else 0
            ),
            "last_modified": (
                datetime.fromtimestamp(self.config_file.stat().st_mtime).isoformat()
                if self.config_file.exists()
                else None
            ),
            "backup_count": len(list(self.backup_dir.glob("config_backup_*.json"))),
        }
