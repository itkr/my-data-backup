"""ログ機能"""

import logging
import sys
from datetime import datetime
from pathlib import Path


class SyncLogger:
    """同期処理用ログクラス"""

    def __init__(self, log_file: str = None, console: bool = True):
        self.logger = logging.getLogger("sync_logger")
        self.logger.setLevel(logging.INFO)

        # ハンドラーをクリア
        self.logger.handlers.clear()

        # フォーマッター
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # コンソールハンドラー
        if console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # ファイルハンドラー
        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def info(self, message: str):
        """情報ログ"""
        self.logger.info(message)

    def warning(self, message: str):
        """警告ログ"""
        self.logger.warning(message)

    def error(self, message: str):
        """エラーログ"""
        self.logger.error(message)

    def success(self, message: str):
        """成功ログ"""
        self.logger.info(f"✅ {message}")

    def progress(self, message: str):
        """進捗ログ"""
        self.logger.info(f"📝 {message}")
