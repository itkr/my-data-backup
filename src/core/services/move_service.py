"""
Move サービス
"""

from pathlib import Path
from typing import List, Dict, Optional, Callable
import logging
from datetime import datetime

from ..domain.models import (
    FileInfo,
    FileType,
    ProcessResult,
    OrganizationConfig,
    FileOperation,
    OperationType,
)
from ..domain.repositories import FileRepository


class MoveService:
    """
    Move機能のビジネスロジックを実装するサービス

    責任:
    - ファイルの日付ベース分類
    - 拡張子ベース分類
    - ディレクトリ構造の生成
    - 重複ファイルの処理
    """

    def __init__(
        self, file_repository: FileRepository, logger: Optional[logging.Logger] = None
    ):
        self.file_repository = file_repository
        self.logger = logger or logging.getLogger(__name__)

    def organize_by_date(
        self,
        source_dir: Path,
        target_dir: Path,
        config: OrganizationConfig,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> ProcessResult:
        """
        日付ベースファイル整理のメインビジネスロジック

        Args:
            source_dir: ソースディレクトリ
            target_dir: ターゲットディレクトリ
            config: 整理設定
            progress_callback: プログレス更新用コールバック

        Returns:
            ProcessResult: 処理結果
        """
        self.logger.info(f"日付ベース整理を開始: {source_dir} -> {target_dir}")

        # 1. ファイルスキャン
        files = self.file_repository.scan_directory(source_dir)
        self.logger.info(f"スキャン完了: {len(files)} ファイル")

        # 2. 日付ベースでグループ化
        date_groups = self._group_by_date(files)
        self.logger.info(f"日付グループ化完了: {len(date_groups)} グループ")

        # 3. ファイル処理
        result = ProcessResult()
        total_files = len(files)
        processed = 0

        for date_key, file_group in date_groups.items():
            for file_info in file_group:
                try:
                    target_path = self._generate_target_path(
                        file_info, target_dir, config
                    )

                    # ディレクトリ作成
                    if not config.dry_run:
                        self.file_repository.create_directory(target_path.parent)

                    # ファイル操作実行
                    success = self._execute_file_operation(
                        file_info.path, target_path, config
                    )

                    if success:
                        result.success_count += 1
                        result.processed_files.append(file_info)
                        self.logger.debug(
                            f"処理成功: {file_info.path} -> {target_path}"
                        )
                    else:
                        result.error_count += 1
                        result.errors.append(f"移動失敗: {file_info.name}")

                except Exception as e:
                    result.error_count += 1
                    result.errors.append(f"処理エラー {file_info.name}: {str(e)}")
                    self.logger.error(f"ファイル処理エラー: {e}")

                processed += 1
                if progress_callback:
                    progress_callback(processed, total_files)

        self.logger.info(
            f"日付ベース整理完了: 成功={result.success_count}, 失敗={result.error_count}"
        )
        return result

    def organize_by_type(
        self,
        source_dir: Path,
        target_dir: Path,
        config: OrganizationConfig,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> ProcessResult:
        """
        ファイルタイプベース整理

        Args:
            source_dir: ソースディレクトリ
            target_dir: ターゲットディレクトリ
            config: 整理設定
            progress_callback: プログレス更新用コールバック

        Returns:
            ProcessResult: 処理結果
        """
        self.logger.info(f"タイプベース整理を開始: {source_dir} -> {target_dir}")

        files = self.file_repository.scan_directory(source_dir)
        type_groups = self._group_by_type(files)

        result = ProcessResult()
        total_files = len(files)
        processed = 0

        for file_type, file_group in type_groups.items():
            for file_info in file_group:
                try:
                    # タイプ別ディレクトリに配置
                    type_dir = target_dir / file_type.value.upper()
                    target_path = type_dir / file_info.name

                    if not config.dry_run:
                        self.file_repository.create_directory(type_dir)

                    success = self._execute_file_operation(
                        file_info.path, target_path, config
                    )

                    if success:
                        result.success_count += 1
                        result.processed_files.append(file_info)
                    else:
                        result.error_count += 1
                        result.errors.append(f"移動失敗: {file_info.name}")

                except Exception as e:
                    result.error_count += 1
                    result.errors.append(f"処理エラー {file_info.name}: {str(e)}")

                processed += 1
                if progress_callback:
                    progress_callback(processed, total_files)

        return result

    def _group_by_date(self, files: List[FileInfo]) -> Dict[str, List[FileInfo]]:
        """ファイルを日付でグループ化"""
        groups = {}
        for file_info in files:
            date_key = file_info.created_date.strftime("%Y-%m-%d")
            if date_key not in groups:
                groups[date_key] = []
            groups[date_key].append(file_info)
        return groups

    def _group_by_type(self, files: List[FileInfo]) -> Dict[FileType, List[FileInfo]]:
        """ファイルをタイプでグループ化"""
        groups = {}
        for file_info in files:
            if file_info.file_type not in groups:
                groups[file_info.file_type] = []
            groups[file_info.file_type].append(file_info)
        return groups

    def _generate_target_path(
        self, file_info: FileInfo, base_dir: Path, config: OrganizationConfig
    ) -> Path:
        """ターゲットパスを生成"""
        path_parts = [base_dir]

        if config.create_date_dirs:
            date = file_info.created_date
            year = date.strftime("%Y")
            month = date.strftime("%m月")
            day = date.strftime("%Y-%m-%d")
            path_parts.extend([year, month, day])

        if config.create_type_dirs:
            extension = file_info.extension.lstrip(".").lower()
            path_parts.append(extension)

        path_parts.append(file_info.name)

        return Path(*path_parts)

    def _execute_file_operation(
        self, source: Path, destination: Path, config: OrganizationConfig
    ) -> bool:
        """ファイル操作の実行"""
        if config.dry_run:
            self.logger.info(f"[DRY RUN] {source} -> {destination}")
            return True

        try:
            # 重複ファイルのチェック
            if config.handle_duplicates and self.file_repository.exists(destination):
                destination = self._generate_unique_path(destination)

            if config.preserve_original:
                return self.file_repository.copy_file(source, destination)
            else:
                return self.file_repository.move_file(source, destination)

        except Exception as e:
            self.logger.error(f"ファイル操作エラー: {e}")
            return False

    def _generate_unique_path(self, path: Path) -> Path:
        """重複ファイル用のユニークパスを生成"""
        counter = 1
        stem = path.stem
        suffix = path.suffix
        parent = path.parent

        while True:
            new_name = f"{stem}_{counter:03d}{suffix}"
            new_path = parent / new_name
            if not self.file_repository.exists(new_path):
                return new_path
            counter += 1
