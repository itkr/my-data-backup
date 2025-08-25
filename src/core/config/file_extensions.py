"""
ファイル拡張子定義
アプリケーション全体で使用するファイル拡張子の一元管理
"""

from typing import Dict, List


class FileExtensions:
    """ファイル拡張子の定義クラス"""

    # 拡張子の分類定義
    RAW_EXTENSIONS = [".arw", ".raw", ".cr2", ".nef", ".dng"]
    JPG_EXTENSIONS = [".jpg", ".jpeg"]
    VIDEO_EXTENSIONS = [".mov", ".mp4", ".mpg", ".avi", ".mts", ".lrf", ".lrv"]
    AUDIO_EXTENSIONS = [".wav", ".mp3", ".aac", ".flac"]
    DOCUMENT_EXTENSIONS = [".xml", ".txt", ".pdf", ".doc", ".docx"]

    # GUI用のカテゴリ別拡張子（日本語ラベル付き）
    GUI_CATEGORIES = {
        "画像": RAW_EXTENSIONS + JPG_EXTENSIONS,
        "動画": VIDEO_EXTENSIONS,
        "音声": AUDIO_EXTENSIONS,
    }

    # ファイルタイプ別拡張子マッピング
    TYPE_MAPPING = {
        "RAW": RAW_EXTENSIONS,
        "JPG": JPG_EXTENSIONS,
        "VIDEO": VIDEO_EXTENSIONS,
        "AUDIO": AUDIO_EXTENSIONS,
        "DOCUMENT": DOCUMENT_EXTENSIONS,
    }

    @classmethod
    def get_all_supported_extensions(cls) -> List[str]:
        """サポートされている全拡張子を取得"""
        return (
            cls.RAW_EXTENSIONS
            + cls.JPG_EXTENSIONS
            + cls.VIDEO_EXTENSIONS
            + cls.AUDIO_EXTENSIONS
            + cls.DOCUMENT_EXTENSIONS
        )

    @classmethod
    def get_gui_categories(cls) -> Dict[str, List[str]]:
        """GUI用のカテゴリ別拡張子を取得"""
        return cls.GUI_CATEGORIES.copy()

    @classmethod
    def get_extension_type(cls, extension: str) -> str:
        """拡張子からファイルタイプを判定"""
        extension = extension.lower()

        if extension in cls.RAW_EXTENSIONS:
            return "RAW"
        elif extension in cls.JPG_EXTENSIONS:
            return "JPG"
        elif extension in cls.VIDEO_EXTENSIONS:
            return "VIDEO"
        elif extension in cls.AUDIO_EXTENSIONS:
            return "AUDIO"
        elif extension in cls.DOCUMENT_EXTENSIONS:
            return "DOCUMENT"
        else:
            return "OTHER"

    @classmethod
    def is_supported(cls, extension: str) -> bool:
        """指定された拡張子がサポートされているかチェック"""
        return extension.lower() in cls.get_all_supported_extensions()
