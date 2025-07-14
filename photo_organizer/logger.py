"""ログ機能 - 共通ログ機構を使用"""

import sys
from pathlib import Path

# 共通ログ機構をインポート
sys.path.append(str(Path(__file__).parent.parent))
from common.logger import UnifiedLogger


class SyncLogger(UnifiedLogger):
    """同期処理用ログクラス - 後方互換性のため"""

    def __init__(self, log_file: str = None, console: bool = True):
        super().__init__(name="sync_logger", log_file=log_file, console=console)
