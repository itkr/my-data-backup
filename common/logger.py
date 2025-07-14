"""統一ログ機構"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class UnifiedLogger:
    """統一ログクラス - 全ツール共通で使用"""

    def __init__(
        self,
        name: str = "unified_logger",
        log_file: Optional[str] = None,
        console: bool = True,
        level: int = logging.INFO,
    ):
        """
        Args:
            name: ロガー名
            log_file: ログファイルパス（Noneの場合はファイル出力なし）
            console: コンソール出力の有無
            level: ログレベル
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # 既存のハンドラーをクリア（重複を防ぐ）
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
            # ログファイルのディレクトリを作成
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message: str):
        """デバッグログ"""
        self.logger.debug(message)

    def info(self, message: str):
        """情報ログ"""
        self.logger.info(message)

    def warning(self, message: str):
        """警告ログ"""
        self.logger.warning(message)

    def error(self, message: str):
        """エラーログ"""
        self.logger.error(message)

    def critical(self, message: str):
        """重大エラーログ"""
        self.logger.critical(message)

    def success(self, message: str):
        """成功ログ（情報レベル + 絵文字）"""
        self.logger.info(f"✅ {message}")

    def progress(self, message: str):
        """進捗ログ（情報レベル + 絵文字）"""
        self.logger.info(f"📝 {message}")

    def start_operation(self, operation_name: str, **kwargs):
        """操作開始ログ"""
        self.logger.info(f"🚀 Started: {operation_name}")
        for key, value in kwargs.items():
            self.logger.info(f"   {key}: {value}")

    def end_operation(
        self, operation_name: str, success_count: int = 0, error_count: int = 0
    ):
        """操作終了ログ"""
        self.logger.info(f"🏁 Completed: {operation_name}")
        if success_count > 0 or error_count > 0:
            self.logger.info(f"   Success: {success_count}, Errors: {error_count}")

    def separator(self, char: str = "=", length: int = 50):
        """区切り線ログ"""
        self.logger.info(char * length)


# 便利な関数
def create_logger(
    name: str,
    log_file: Optional[str] = None,
    console: bool = True,
    level: int = logging.INFO,
) -> UnifiedLogger:
    """統一ログインスタンスを作成"""
    return UnifiedLogger(name=name, log_file=log_file, console=console, level=level)


def create_file_logger(name: str, log_file: str, console: bool = True) -> UnifiedLogger:
    """ファイル出力付きログインスタンスを作成"""
    return UnifiedLogger(name=name, log_file=log_file, console=console)


def create_console_logger(name: str) -> UnifiedLogger:
    """コンソール出力のみのログインスタンスを作成"""
    return UnifiedLogger(name=name, console=True)


# 後方互換性のためのエイリアス
SyncLogger = UnifiedLogger  # photo_organizerとの互換性
