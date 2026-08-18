"""
リポジトリインターフェース定義
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from ..models import FileInfo


class FileRepository(ABC):
    """ファイル操作の抽象インターフェース"""

    @abstractmethod
    def scan_directory(self, directory: Path, recursive: bool = True) -> List[FileInfo]:
        """
        ディレクトリをスキャンしてファイル情報を取得

        Args:
            directory: スキャン対象ディレクトリ
            recursive: 再帰的にスキャンするか

        Returns:
            ファイル情報のリスト
        """

    @abstractmethod
    def get_file_info(self, file_path: Path) -> Optional[FileInfo]:
        """
        単一ファイルの情報を取得

        Args:
            file_path: ファイルパス

        Returns:
            ファイル情報、存在しない場合はNone
        """

    @abstractmethod
    def move_file(self, source: Path, destination: Path) -> bool:
        """
        ファイルを移動

        Args:
            source: 移動元パス
            destination: 移動先パス

        Returns:
            成功した場合はTrue
        """

    @abstractmethod
    def copy_file(self, source: Path, destination: Path) -> bool:
        """
        ファイルをコピー

        Args:
            source: コピー元パス
            destination: コピー先パス

        Returns:
            成功した場合はTrue
        """

    @abstractmethod
    def delete_file(self, file_path: Path) -> bool:
        """
        ファイルを削除

        Args:
            file_path: 削除対象ファイルパス

        Returns:
            成功した場合はTrue
        """

    @abstractmethod
    def create_directory(self, directory: Path) -> bool:
        """
        ディレクトリを作成

        Args:
            directory: 作成するディレクトリパス

        Returns:
            成功した場合はTrue
        """

    @abstractmethod
    def exists(self, path: Path) -> bool:
        """
        パスが存在するかチェック

        Args:
            path: チェック対象パス

        Returns:
            存在する場合はTrue
        """

    @abstractmethod
    def calculate_checksum(self, file_path: Path) -> Optional[str]:
        """
        ファイルのチェックサムを計算

        Args:
            file_path: チェックサム計算対象ファイル

        Returns:
            チェックサム文字列、計算できない場合はNone
        """
