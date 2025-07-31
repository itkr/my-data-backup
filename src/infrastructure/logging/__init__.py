"""
統一ログ機構 - インフラ層での実装
"""

import logging
import sys
from pathlib import Path
from typing import Optional


class Logger:
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
        """成功ログ（特別なメソッド）"""
        self.logger.info(f"✅ {message}")

    def progress(self, message: str):
        """進捗ログ（特別なメソッド）"""
        self.logger.info(f"🔄 {message}")

    def start_operation(self, operation_name: str):
        """操作開始ログ"""
        self.logger.info(f"🚀 開始: {operation_name}")

    def end_operation(self, operation_name: str, success: bool = True):
        """操作終了ログ"""
        if success:
            self.logger.info(f"✅ 完了: {operation_name}")
        else:
            self.logger.error(f"❌ 失敗: {operation_name}")


def get_logger(name: str = "my_data_backup", log_file: Optional[str] = None) -> Logger:
    """ロガーを取得する便利関数"""
    return Logger(name=name, log_file=log_file)
