"""
構造化された設定クラス
設定項目を分野別に整理し、メンテナンス性を向上
"""

from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class UIConfig:
    """UI関連設定"""

    theme: str = "auto"
    window_width: int = 1200
    window_height: int = 900
    log_level: str = "INFO"


@dataclass
class PhotoOrganizerConfig:
    """Photo Organizer関連設定"""

    default_dry_run: bool = True
    default_preserve: bool = False
    last_source_dir: str = ""
    last_output_dir: str = ""


@dataclass
class MoveConfig:
    """Move機能関連設定"""

    default_dry_run: bool = True
    default_date_dirs: bool = True
    default_type_dirs: bool = True
    last_import_dir: str = ""
    last_export_dir: str = ""


@dataclass
class GeneralConfig:
    """一般設定"""

    auto_save_config: bool = True
    show_confirmation_dialogs: bool = True
    max_recent_directories: int = 10
    recent_directories: List[str] = None

    def __post_init__(self):
        if self.recent_directories is None:
            self.recent_directories = []


class AppConfig:
    """構造化されたアプリケーション設定"""

    def __init__(self):
        self.ui = UIConfig()
        self.photo = PhotoOrganizerConfig()
        self.move = MoveConfig()
        self.general = GeneralConfig()

    def to_dict(self) -> Dict[str, Any]:
        """設定を辞書形式に変換"""
        result = {}

        # 各セクションを辞書に変換
        for section_name, section_obj in self._get_sections().items():
            if hasattr(section_obj, "__dataclass_fields__"):
                # dataclassの場合
                section_dict = {}
                for field in fields(section_obj):
                    value = getattr(section_obj, field.name)
                    section_dict[field.name] = value
                result[section_name] = section_dict
            else:
                # 通常のオブジェクトの場合
                result[section_name] = section_obj.__dict__

        return result

    def update_from_dict(self, data: Dict[str, Any]):
        """辞書から設定を更新"""
        sections = self._get_sections()

        for section_name, section_data in data.items():
            if section_name in sections:
                section_obj = sections[section_name]

                if isinstance(section_data, dict):
                    # セクション内の各フィールドを更新
                    for key, value in section_data.items():
                        if hasattr(section_obj, key):
                            setattr(section_obj, key, value)

    def _get_sections(self) -> Dict[str, Any]:
        """設定セクションの辞書を取得"""
        return {
            "ui": self.ui,
            "photo": self.photo,
            "move": self.move,
            "general": self.general,
        }

    def reset_to_defaults(self):
        """設定をデフォルトにリセット"""
        self.ui = UIConfig()
        self.photo = PhotoOrganizerConfig()
        self.move = MoveConfig()
        self.general = GeneralConfig()

    # ディレクトリ履歴管理メソッド
    def update_recent_directory(self, directory: str):
        """最近使用したディレクトリを更新"""
        if not directory or not Path(directory).exists():
            return

        # 既存の項目を削除
        if directory in self.general.recent_directories:
            self.general.recent_directories.remove(directory)

        # 先頭に追加
        self.general.recent_directories.insert(0, directory)

        # 最大数を超えた場合は削除
        if len(self.general.recent_directories) > self.general.max_recent_directories:
            self.general.recent_directories = self.general.recent_directories[
                : self.general.max_recent_directories
            ]

    def get_recent_directories(self) -> List[str]:
        """最近使用したディレクトリを取得"""
        return self.general.recent_directories.copy()

    def set_recent_directories(self, directories: List[str]):
        """最近使用したディレクトリを設定"""
        self.general.recent_directories = directories.copy()

    # 設定更新メソッド
    def update_photo_settings(self, **kwargs) -> bool:
        """Photo Organizer設定を更新"""
        updated = False
        for key, value in kwargs.items():
            if hasattr(self.photo, key):
                setattr(self.photo, key, value)
                updated = True
        return updated

    def update_move_settings(self, **kwargs) -> bool:
        """Move設定を更新"""
        updated = False
        for key, value in kwargs.items():
            if hasattr(self.move, key):
                setattr(self.move, key, value)
                updated = True
        return updated

    def update_ui_settings(self, **kwargs) -> bool:
        """UI設定を更新"""
        updated = False
        valid_ui_settings = ["theme", "window_width", "window_height", "log_level"]

        for key, value in kwargs.items():
            if key in valid_ui_settings and hasattr(self.ui, key):
                setattr(self.ui, key, value)
                updated = True
        return updated

    def update_general_settings(self, **kwargs) -> bool:
        """一般設定を更新"""
        updated = False
        for key, value in kwargs.items():
            if hasattr(self.general, key):
                setattr(self.general, key, value)
                updated = True
        return updated

    # プロパティアクセス（後方互換性のため）
    @property
    def auto_save_config(self) -> bool:
        return self.general.auto_save_config

    @auto_save_config.setter
    def auto_save_config(self, value: bool):
        self.general.auto_save_config = value

    @property
    def theme(self) -> str:
        return self.ui.theme

    @theme.setter
    def theme(self, value: str):
        self.ui.theme = value

    @property
    def window_width(self) -> int:
        return self.ui.window_width

    @window_width.setter
    def window_width(self, value: int):
        self.ui.window_width = value

    @property
    def window_height(self) -> int:
        return self.ui.window_height

    @window_height.setter
    def window_height(self, value: int):
        self.ui.window_height = value

    # Photo関連プロパティ
    @property
    def photo_default_dry_run(self) -> bool:
        return self.photo.default_dry_run

    @photo_default_dry_run.setter
    def photo_default_dry_run(self, value: bool):
        self.photo.default_dry_run = value

    @property
    def photo_last_source_dir(self) -> str:
        return self.photo.last_source_dir

    @photo_last_source_dir.setter
    def photo_last_source_dir(self, value: str):
        self.photo.last_source_dir = value

    @property
    def photo_last_output_dir(self) -> str:
        return self.photo.last_output_dir

    @photo_last_output_dir.setter
    def photo_last_output_dir(self, value: str):
        self.photo.last_output_dir = value

    # Move関連プロパティ
    @property
    def move_default_dry_run(self) -> bool:
        return self.move.default_dry_run

    @move_default_dry_run.setter
    def move_default_dry_run(self, value: bool):
        self.move.default_dry_run = value

    @property
    def move_last_import_dir(self) -> str:
        return self.move.last_import_dir

    @move_last_import_dir.setter
    def move_last_import_dir(self, value: str):
        self.move.last_import_dir = value

    @property
    def move_last_export_dir(self) -> str:
        return self.move.last_export_dir

    @move_last_export_dir.setter
    def move_last_export_dir(self, value: str):
        self.move.last_export_dir = value

    @property
    def recent_directories(self) -> List[str]:
        return self.general.recent_directories

    @recent_directories.setter
    def recent_directories(self, value: List[str]):
        self.general.recent_directories = value

    @property
    def max_recent_directories(self) -> int:
        return self.general.max_recent_directories

    @max_recent_directories.setter
    def max_recent_directories(self, value: int):
        self.general.max_recent_directories = value
