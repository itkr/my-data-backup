"""
CLI基底クラス - オプション定義の統一管理
"""

from abc import ABC, abstractmethod


class BaseCLI(ABC):
    """CLI共通基底クラス"""

    # バックアップでしか使っていないのでコメントアウト
    # @classmethod
    # @abstractmethod
    # def get_argument_spec(cls) -> Dict[str, Any]:
    #     """
    #     argparse用の引数仕様を返す

    #     Returns:
    #         Dict: argparse.add_argument()に渡すパラメータ
    #     """

    @classmethod
    @abstractmethod
    def get_command_name(cls) -> str:
        """コマンド名を返す"""

    @classmethod
    @abstractmethod
    def get_description(cls) -> str:
        """コマンドの説明を返す"""

    @abstractmethod
    def run_from_args(self, args) -> None:
        """
        argparseで解析された引数から実行

        Args:
            args: argparse.Namespace
        """
