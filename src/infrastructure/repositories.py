"""
ファイルシステムリポジトリの具体実装
"""

import hashlib
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from core.domain.models import FileInfo, FileType
from core.domain.repositories import FileRepository


class FileSystemRepository(FileRepository):
    """
    ファイルシステムを使用したFileRepositoryの具体実装
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

    def scan_directory(self, directory: Path, recursive: bool = True) -> List[FileInfo]:
        """
        ディレクトリをスキャンしてファイル情報を取得
        """
        if not directory.exists() or not directory.is_dir():
            self.logger.warning(f"ディレクトリが存在しません: {directory}")
            return []

        files = []
        pattern = "**/*" if recursive else "*"

        try:
            for path in directory.glob(pattern):
                if path.is_file():
                    file_info = self.get_file_info(path)
                    if file_info:
                        files.append(file_info)

        except Exception as e:
            self.logger.error(f"ディレクトリスキャンエラー {directory}: {e}")

        self.logger.info(f"スキャン完了: {len(files)} ファイル in {directory}")
        return files

    def get_file_info(self, file_path: Path) -> Optional[FileInfo]:
        """
        単一ファイルの情報を取得
        """
        try:
            if not file_path.exists() or not file_path.is_file():
                return None

            stat = file_path.stat()

            return FileInfo(
                path=file_path,
                file_type=self._determine_file_type(file_path),
                created_date=datetime.fromtimestamp(stat.st_mtime),
                size=stat.st_size,
                checksum=None,  # 必要に応じて計算
            )

        except Exception as e:
            self.logger.error(f"ファイル情報取得エラー {file_path}: {e}")
            return None

    def move_file(self, source: Path, destination: Path) -> bool:
        """
        ファイルを移動
        """
        try:
            # 移動先ディレクトリを作成
            destination.parent.mkdir(parents=True, exist_ok=True)

            # ファイル移動
            shutil.move(str(source), str(destination))

            self.logger.debug(f"ファイル移動成功: {source} -> {destination}")
            return True

        except Exception as e:
            self.logger.error(f"ファイル移動エラー {source} -> {destination}: {e}")
            return False

    def copy_file(self, source: Path, destination: Path) -> bool:
        """
        ファイルをコピー
        """
        try:
            # コピー先ディレクトリを作成
            destination.parent.mkdir(parents=True, exist_ok=True)

            # ファイルコピー
            shutil.copy2(str(source), str(destination))

            self.logger.debug(f"ファイルコピー成功: {source} -> {destination}")
            return True

        except Exception as e:
            self.logger.error(f"ファイルコピーエラー {source} -> {destination}: {e}")
            return False

    def delete_file(self, file_path: Path) -> bool:
        """
        ファイルを削除
        """
        try:
            if file_path.exists():
                file_path.unlink()
                self.logger.debug(f"ファイル削除成功: {file_path}")
                return True
            else:
                self.logger.warning(f"削除対象ファイルが存在しません: {file_path}")
                return False

        except Exception as e:
            self.logger.error(f"ファイル削除エラー {file_path}: {e}")
            return False

    def create_directory(self, directory: Path) -> bool:
        """
        ディレクトリを作成
        """
        try:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"ディレクトリ作成成功: {directory}")
            return True

        except Exception as e:
            self.logger.error(f"ディレクトリ作成エラー {directory}: {e}")
            return False

    def exists(self, path: Path) -> bool:
        """
        パスが存在するかチェック
        """
        return path.exists()

    def calculate_checksum(self, file_path: Path) -> Optional[str]:
        """
        ファイルのチェックサムを計算
        """
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)

            checksum = hash_md5.hexdigest()
            self.logger.debug(f"チェックサム計算成功 {file_path}: {checksum}")
            return checksum

        except Exception as e:
            self.logger.error(f"チェックサム計算エラー {file_path}: {e}")
            return None

    def _determine_file_type(self, file_path: Path) -> FileType:
        """
        ファイルタイプを判定
        """
        extension = file_path.suffix.lower()

        # 画像ファイル
        if extension in [".arw", ".raw", ".cr2", ".nef", ".dng"]:
            return FileType.RAW
        elif extension in [".jpg", ".jpeg"]:
            return FileType.JPG

        # 動画ファイル
        elif extension in [".mov", ".mp4", ".mpg", ".avi", ".mts", ".lrf", ".lrv"]:
            return FileType.VIDEO

        # 音声ファイル
        elif extension in [".wav", ".mp3", ".aac", ".flac"]:
            return FileType.AUDIO

        # ドキュメント
        elif extension in [".xml", ".txt", ".pdf", ".doc", ".docx"]:
            return FileType.DOCUMENT

        else:
            return FileType.OTHER
