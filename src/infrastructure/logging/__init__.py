"""
ログ設定
"""

import logging
import sys
from pathlib import Path
from typing import Optional

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(
    name: str = "my_data_backup",
    log_file: Optional[str] = None,
    console: bool = True,
    level: int = logging.INFO,
) -> logging.Logger:
    """設定済みのロガーを取得する

    Args:
        name: ロガー名
        log_file: ログファイルパス（Noneの場合はファイル出力なし）
        console: コンソール出力の有無
        level: ログレベル
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 同じ名前で再取得したときにハンドラーが重複しないようにする
    logger.handlers.clear()

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
