"""
CLI基底クラス - オプション定義の統一管理
"""

from abc import ABC, abstractmethod


class BaseCLI(ABC):
    """CLI共通基底クラス"""

    @abstractmethod
    def run_from_args(self, args) -> None:
        """
        argparseで解析された引数から実行

        Args:
            args: argparse.Namespace
        """
