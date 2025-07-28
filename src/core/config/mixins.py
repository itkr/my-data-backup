"""
設定管理用Mixinクラス群
ConfigManagerの機能を分割してメンテナンス性を向上
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class FileOperationsMixin:
    """ファイル操作関連のMixin"""

    def _create_backup(self):
        """設定ファイルのバックアップを作成"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"config_backup_{timestamp}.json"
            shutil.copy2(self.config_file, backup_file)

            # 古いバックアップをクリーンアップ
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

    def save_config(self, backup: bool = True) -> bool:
        """設定を保存"""
        try:
            # バックアップ作成
            if backup and self.config_file.exists():
                self._create_backup()

            # 設定保存
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config.to_dict(), f, indent=2, ensure_ascii=False)

            print(f"💾 設定を保存しました: {self.config_file}")
            return True

        except Exception as e:
            print(f"❌ 設定保存エラー: {e}")
            return False

    def load_config(self):
        """設定を読み込み"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # 設定を更新
                self.config.update_from_dict(data)
                print(f"✅ 設定を読み込みました: {self.config_file}")
            else:
                print(f"📝 デフォルト設定を使用します: {self.config_file}")
                self.save_config()  # デフォルト設定を保存

        except Exception as e:
            print(f"⚠️ 設定読み込みエラー: {e}")
            print("📝 デフォルト設定を使用します")


class ImportExportMixin:
    """インポート・エクスポート機能のMixin"""

    def export_config(self, export_path: Path) -> bool:
        """設定をエクスポート"""
        try:
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(self.config.to_dict(), f, indent=2, ensure_ascii=False)

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

            # 新しい設定を適用
            self.config.update_from_dict(data)

            # 保存
            self.save_config(backup=False)

            print(f"📥 設定をインポートしました: {import_path}")
            return True

        except Exception as e:
            print(f"❌ 設定インポートエラー: {e}")
            return False


class DirectoryHistoryMixin:
    """ディレクトリ履歴管理のMixin"""

    def update_recent_directory(self, directory: str):
        """最近使用したディレクトリを更新"""
        if not directory or not Path(directory).exists():
            return

        self.config.update_recent_directory(directory)

        if self.config.auto_save_config:
            self.save_config()

    def get_recent_directories(self, limit: Optional[int] = None) -> List[str]:
        """最近使用したディレクトリを取得"""
        directories = self.config.get_recent_directories()

        # 存在しないディレクトリを除外
        valid_directories = [d for d in directories if Path(d).exists()]

        # 変更があった場合は更新
        if len(valid_directories) != len(directories):
            self.config.set_recent_directories(valid_directories)
            if self.config.auto_save_config:
                self.save_config()

        return valid_directories[:limit] if limit else valid_directories


class SettingsUpdateMixin:
    """設定更新機能のMixin"""

    def update_photo_settings(self, **kwargs):
        """Photo Organizer設定を更新"""
        updated = self.config.update_photo_settings(**kwargs)

        if updated and self.config.auto_save_config:
            self.save_config()

    def update_move_settings(self, **kwargs):
        """Move設定を更新"""
        updated = self.config.update_move_settings(**kwargs)

        if updated and self.config.auto_save_config:
            self.save_config()

    def update_ui_settings(self, **kwargs):
        """UI設定を更新"""
        updated = self.config.update_ui_settings(**kwargs)

        if updated and self.config.auto_save_config:
            self.save_config()


class ConfigInfoMixin:
    """設定情報取得のMixin"""

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

    def reset_to_defaults(self) -> bool:
        """設定をデフォルトにリセット"""
        try:
            self._create_backup()
            self.config.reset_to_defaults()
            return self.save_config(backup=False)
        except Exception as e:
            print(f"❌ 設定リセットエラー: {e}")
            return False


class ValidatorMixin:
    """設定値検証のMixin"""

    def validate_config(self) -> List[str]:
        """設定値を検証し、問題があればエラーメッセージを返す"""
        errors = []

        # UI設定の検証
        if (
            not isinstance(self.config.window_width, int)
            or self.config.window_width < 800
        ):
            errors.append("ウィンドウ幅は800以上の整数である必要があります")

        if (
            not isinstance(self.config.window_height, int)
            or self.config.window_height < 600
        ):
            errors.append("ウィンドウ高さは600以上の整数である必要があります")

        if self.config.theme not in ["light", "dark", "auto"]:
            errors.append(
                "テーマは 'light', 'dark', 'auto' のいずれかである必要があります"
            )

        # ディレクトリパスの検証
        for attr_name in [
            "photo_last_source_dir",
            "photo_last_output_dir",
            "move_last_import_dir",
            "move_last_export_dir",
        ]:
            path_value = getattr(self.config, attr_name, "")
            if path_value and not Path(path_value).exists():
                errors.append(f"{attr_name} のパスが存在しません: {path_value}")

        return errors

    def auto_fix_config(self) -> bool:
        """自動修正可能な設定問題を修正"""
        fixed = False

        # ウィンドウサイズの修正
        if self.config.window_width < 800:
            self.config.window_width = 1200
            fixed = True

        if self.config.window_height < 600:
            self.config.window_height = 900
            fixed = True

        # 無効なテーマの修正
        if self.config.theme not in ["light", "dark", "auto"]:
            self.config.theme = "auto"
            fixed = True

        # 存在しないディレクトリパスをクリア
        for attr_name in [
            "photo_last_source_dir",
            "photo_last_output_dir",
            "move_last_import_dir",
            "move_last_export_dir",
        ]:
            path_value = getattr(self.config, attr_name, "")
            if path_value and not Path(path_value).exists():
                setattr(self.config, attr_name, "")
                fixed = True

        if fixed and self.config.auto_save_config:
            self.save_config()

        return fixed
