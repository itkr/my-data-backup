"""
設定管理システム初期化

モジュール化されたConfigManagerを提供
"""

from .config import (
    AppConfig,
    GeneralConfig,
    MoveConfig,
    PhotoOrganizerConfig,
    UIConfig,
)

# モジュール化されたConfigManager
from .config_manager import ConfigManager

# 拡張子定義とMixinも利用可能にする
from .file_extensions import FileExtensions

__all__ = [
    # メインのConfigManager
    "ConfigManager",
    # 拡張子定義
    "FileExtensions",
    # 構造化された設定クラス
    "AppConfig",
    "UIConfig",
    "PhotoOrganizerConfig",
    "MoveConfig",
    "GeneralConfig",
]
