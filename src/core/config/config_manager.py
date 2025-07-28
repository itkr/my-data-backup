"""
リファクタリングされた設定管理システム
Mixinパターンを使用してモジュール化
"""

from pathlib import Path
from typing import Optional

from .config import AppConfig
from .mixins import (
    ConfigInfoMixin,
    DirectoryHistoryMixin,
    FileOperationsMixin,
    ImportExportMixin,
    SettingsUpdateMixin,
    ValidatorMixin,
)


class ConfigManager(
    FileOperationsMixin,
    ImportExportMixin,
    DirectoryHistoryMixin,
    SettingsUpdateMixin,
    ConfigInfoMixin,
    ValidatorMixin,
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
        if config_dir is None:
            self.config_dir = Path.home() / ".my-data-backup"
        else:
            self.config_dir = config_dir

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

    def get_version(self) -> str:
        """ConfigManagerのバージョンを取得"""
        return "2.0.0-modular"

    def get_features(self) -> list:
        """利用可能な機能一覧を取得"""
        return [
            "📁 ファイル操作 (保存・読み込み・バックアップ)",
            "📤📥 インポート・エクスポート",
            "📂 ディレクトリ履歴管理",
            "⚙️ 設定更新",
            "📊 設定情報取得",
            "✅ 設定値検証・自動修正",
            "🏗️ 構造化された設定管理",
        ]

    def print_status(self):
        """現在の設定状況を表示"""
        print("=" * 50)
        print("📋 ConfigManager ステータス")
        print("=" * 50)
        print(f"📁 設定ディレクトリ: {self.config_dir}")
        print(f"📄 設定ファイル: {self.config_file}")
        print(
            f"💾 バックアップ数: {len(list(self.backup_dir.glob('config_backup_*.json')))}"
        )
        print(f"📊 最近のディレクトリ: {len(self.config.recent_directories)} 件")

        # 設定セクション別の状況
        print("\n🔧 設定セクション:")
        ui_config = self.config.ui
        size_info = f"{ui_config.window_width}x{ui_config.window_height}"
        print(f"  • UI設定: テーマ={ui_config.theme}, サイズ={size_info}")
        print(f"  • Photo設定: ドライラン={self.config.photo.default_dry_run}")
        print(f"  • Move設定: ドライラン={self.config.move.default_dry_run}")
        print(f"  • 一般設定: 自動保存={self.config.general.auto_save_config}")

        # 検証結果
        errors = self.validate_config()
        if errors:
            print(f"\n⚠️ 設定の問題: {len(errors)} 件")
            for error in errors[:3]:  # 最初の3件のみ表示
                print(f"  • {error}")
        else:
            print("\n✅ 設定に問題はありません")

        print("=" * 50)


# クラス名をConfigManagerに変更したため、エイリアスは不要
