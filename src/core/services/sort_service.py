"""
sort サービス — 日付・拡張子で仕分け
"""

import logging
from pathlib import Path
from typing import Callable, Dict, List, Optional

from src.core.domain.models import FileInfo, OrganizationConfig, ProcessResult
from src.core.domain.repositories import FileRepository
from src.core.services.base import FileOrganizerService

# 重複ファイル名の連番を試行する上限。
# これを超える同名ファイルは異常とみなし、無限ループさせずにエラーにする。
MAX_DUPLICATE_ATTEMPTS = 1000


class SortService(FileOrganizerService):
    """
    ファイルを日付・拡張子ごとに仕分けるサービス

    責任:
    - ファイルの日付ベース分類
    - 拡張子ベース分類
    - ディレクトリ構造の生成
    - 重複ファイルの処理
    """

    def __init__(
        self, file_repository: FileRepository, logger: Optional[logging.Logger] = None
    ):
        super().__init__(file_repository, logger)
        self._stop_requested = False

    def stop(self):
        """処理の中断を要求する（GUIの停止ボタンから呼ばれる）

        実行中のファイル単位のループが次のファイルに進む前に中断する。
        処理済みのファイルは元に戻さない。
        """
        self._stop_requested = True
        self.logger.info("停止が要求されました")

    def sort_by_date(
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
        self._stop_requested = False

        # 1. ファイルスキャン（recursive設定を使用）
        files = self.file_repository.scan_directory(
            source_dir, recursive=config.recursive
        )
        self.logger.info(
            f"スキャン完了: {len(files)} ファイル (recursive={config.recursive})"
        )

        # 2. 拡張子フィルタリング
        filtered_files = [f for f in files if config.should_process_file(f.path)]
        self.logger.info(
            f"フィルタリング後: {len(filtered_files)} ファイル "
            f"(拡張子: {config.file_extensions})"
        )

        # 3. 日付ベースでグループ化
        date_groups = self._group_by_date(filtered_files)
        self.logger.info(f"日付グループ化完了: {len(date_groups)} グループ")

        # 4. ファイル処理
        result = ProcessResult()
        total_files = len(filtered_files)
        processed = 0

        for date_key, file_group in date_groups.items():
            for file_info in file_group:
                if self._stop_requested:
                    self.logger.info(
                        f"停止要求により中断: {processed}/{total_files} ファイル処理済み"
                    )
                    return result

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

    # def _get_file_extensions(self, config: OrganizationConfig) -> List[str]:
    #     """設定からファイル拡張子のリストを取得"""
    #     return [ext.lower() for ext in config.file_extensions]

    def _group_by_date(self, files: List[FileInfo]) -> Dict[str, List[FileInfo]]:
        """ファイルを日付でグループ化"""
        groups = {}
        for file_info in files:
            date_key = file_info.created_date.strftime("%Y-%m-%d")
            if date_key not in groups:
                groups[date_key] = []
            groups[date_key].append(file_info)
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
            # 大文字に統一する。元ファイルの綴りをそのまま使うと、macOS のような
            # 大文字小文字を区別しないファイルシステムでは .ARW と .arw が同じ
            # ディレクトリに解決され、綴りが処理順に依存して非決定的になるため。
            extension = file_info.extension.lstrip(".").upper()
            path_parts.append(extension)

        path_parts.append(file_info.name)

        return Path(*path_parts)

    def _execute_file_operation(
        self, source: Path, destination: Path, config: OrganizationConfig
    ) -> bool:
        """ファイル操作の実行（移動先が重複する場合は連番を付ける）"""
        if not config.dry_run and config.handle_duplicates:
            try:
                if self.file_repository.exists(destination):
                    destination = self._generate_unique_path(destination)
            except Exception as e:
                self.logger.error(f"ファイル操作エラー: {e}")
                return False

        return super()._execute_file_operation(source, destination, config)

    def _generate_unique_path(self, path: Path) -> Path:
        """重複ファイル用のユニークパスを生成

        Raises:
            RuntimeError: MAX_DUPLICATE_ATTEMPTS 回試しても空きが見つからない場合
        """
        stem = path.stem
        suffix = path.suffix
        parent = path.parent

        for counter in range(1, MAX_DUPLICATE_ATTEMPTS + 1):
            new_path = parent / f"{stem}_{counter:03d}{suffix}"
            if not self.file_repository.exists(new_path):
                return new_path

        raise RuntimeError(
            f"重複回避のファイル名を {MAX_DUPLICATE_ATTEMPTS} 件試しましたが "
            f"空きが見つかりませんでした: {path}"
        )
