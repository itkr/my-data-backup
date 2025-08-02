"""
リファクタリングされた設定管理システム
Mixinパターンを使用してモジュール化
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from .config import AppConfig
from .mixins import (
    ConfigInfoMixin,
    DirectoryHistoryMixin,
    FileOperationsMixin,
    ImportExportMixin,
    ValidatorMixin,
)


class ConfigManagerInterface(ABC):
    """
    設定管理のインターフェース
    設定の読み込み、保存、更新、検証を定義
    """

    @abstractmethod
    def load_config(self):
        """設定を読み込む"""
        raise NotImplementedError("load_config() must be implemented")

    @abstractmethod
    def save_config(self):
        """設定を保存する"""
        raise NotImplementedError("save_config() must be implemented")


class ConfigManager(
    # mixins
    FileOperationsMixin,
    ImportExportMixin,
    DirectoryHistoryMixin,
    ConfigInfoMixin,
    ValidatorMixin,
    # interface
    ConfigManagerInterface,
):
    """
    モジュール化されたConfigManager

    Mixinパターンを使用して機能を分割し、
    メンテナンス性と拡張性を向上させたConfigManager
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        設定管理を初期化

        Args:
            config_dir: 設定ファイル保存ディレクトリ（Noneの場合はホームディレクトリ/.my-data-backup）
        """
        # ディレクトリ初期化
        self.config_dir = config_dir or (Path.home() / ".my-data-backup")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        self.backup_dir = self.config_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)

        # 構造化された設定オブジェクト
        self.config = AppConfig()

        # 設定を読み込み
        self.load_config()

        # 設定の自動検証・修正
        errors = self.validate_config()
        if errors:
            print(f"⚠️ 設定に問題があります: {len(errors)} 件")
            if self.auto_fix_config():
                print("🔧 自動修正を実行しました")

    def update_photo_settings(self, **kwargs):
        """Photo Organizer設定を更新（自動保存付き）"""
        updated = self.config.update_photo_settings(**kwargs)

        if updated and self.config.general.auto_save_config:
            self.save_config()

    def update_move_settings(self, **kwargs):
        """Move設定を更新（自動保存付き）"""
        updated = self.config.update_move_settings(**kwargs)

        if updated and self.config.general.auto_save_config:
            self.save_config()

    def update_ui_settings(self, **kwargs):
        """UI設定を更新（自動保存付き）"""
        updated = self.config.update_ui_settings(**kwargs)

        if updated and self.config.general.auto_save_config:
            self.save_config()

    def update_general_settings(self, **kwargs):
        """一般設定を更新（自動保存付き）"""
        updated = self.config.update_general_settings(**kwargs)

        if updated and self.config.general.auto_save_config:
            self.save_config()
