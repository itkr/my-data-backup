"""
Photo Organizer サービス
"""

from pathlib import Path
from typing import Callable, List, Optional, Tuple

from src.core.domain.models import (
    FileInfo,
    FileType,
    OrganizationConfig,
    PhotoPair,
    ProcessResult,
)
from src.core.services.base import FileOrganizerService


class PhotoOrganizerService(FileOrganizerService):
    """
    Photo Organizer のビジネスロジックを実装するサービス

    責任:
    - RAW/JPGファイルの対応関係の判定
    - ファイルの同期処理ロジック
    - 孤立ファイルの管理
    - 処理結果の集計
    """

    def organize_photos(
        self,
        source_dir: Path,
        target_dir: Path,
        config: OrganizationConfig,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> ProcessResult:
        """
        写真整理のメインビジネスロジック

        Args:
            source_dir: ソースディレクトリ
            target_dir: ターゲットディレクトリ
            config: 整理設定
            progress_callback: プログレス更新用コールバック

        Returns:
            ProcessResult: 処理結果
        """
        self.logger.info(f"写真整理を開始: {source_dir} -> {target_dir}")

        # 1. ファイルスキャン
        files = self.file_repository.scan_directory(source_dir)
        self.logger.info(f"スキャン完了: {len(files)} ファイル")

        # 2. RAW/JPGファイルの分類
        raw_files, jpg_files = self._classify_photo_files(files)
        self.logger.info(f"分類完了: RAW={len(raw_files)}, JPG={len(jpg_files)}")

        # 3. 対応関係の分析
        pairs = self._analyze_photo_pairs(raw_files, jpg_files)
        complete_pairs = [p for p in pairs if p.is_complete_pair]
        orphan_raws = [p for p in pairs if p.is_orphan_raw]
        orphan_jpgs = [p for p in pairs if p.is_orphan_jpg]

        self.logger.info(
            f"ペア分析完了: 完全ペア={len(complete_pairs)}, "
            f"孤立RAW={len(orphan_raws)}, 孤立JPG={len(orphan_jpgs)}"
        )

        # 4. ファイル処理
        operations = self._plan_operations(
            complete_pairs, orphan_raws + orphan_jpgs, target_dir
        )

        result = ProcessResult()
        for processed, (file_info, destination) in enumerate(operations, 1):
            self._process_file(file_info, destination, config, result)

            if progress_callback:
                progress_callback(processed, len(operations))

        self.logger.info(
            f"写真整理完了: 成功={result.success_count}, "
            f"スキップ={result.skipped_count}, 失敗={result.error_count}"
        )
        return result

    def _plan_operations(
        self,
        complete_pairs: List[PhotoPair],
        orphan_pairs: List[PhotoPair],
        target_dir: Path,
    ) -> List[Tuple[FileInfo, Path]]:
        """各ファイルの移動先を決める

        完全ペアは ARW/ と JPG/ に、孤立ファイルは orphans/ に振り分ける。
        """
        operations = []

        for pair in complete_pairs:
            operations.append((pair.raw_file, target_dir / "ARW" / pair.raw_file.name))
            operations.append((pair.jpg_file, target_dir / "JPG" / pair.jpg_file.name))

        for pair in orphan_pairs:
            orphan = pair.raw_file or pair.jpg_file
            operations.append((orphan, target_dir / "orphans" / orphan.name))

        return operations

    def _process_file(
        self,
        file_info: FileInfo,
        destination: Path,
        config: OrganizationConfig,
        result: ProcessResult,
    ):
        """1ファイルを処理して結果を result に反映する"""
        # 出力先に同名ファイルがある場合は取り込まず、ソース側に残す
        if self.file_repository.exists(destination):
            self.logger.info(f"スキップ（出力先に同名ファイルあり）: {destination}")
            result.skipped_count += 1
            return

        try:
            if not config.dry_run:
                self.file_repository.create_directory(destination.parent)

            if self._execute_file_operation(file_info.path, destination, config):
                result.success_count += 1
                result.processed_files.append(file_info)
            else:
                result.error_count += 1
                result.errors.append(f"処理失敗: {file_info.name}")

        except Exception as e:
            result.error_count += 1
            result.errors.append(f"処理エラー {file_info.name}: {e}")
            self.logger.error(f"ファイル処理エラー: {e}")

    def _classify_photo_files(
        self, files: List[FileInfo]
    ) -> Tuple[List[FileInfo], List[FileInfo]]:
        """ファイルをRAWとJPGに分類"""
        raw_files = [f for f in files if f.file_type == FileType.RAW]
        jpg_files = [f for f in files if f.file_type == FileType.JPG]
        return raw_files, jpg_files

    def _analyze_photo_pairs(
        self, raw_files: List[FileInfo], jpg_files: List[FileInfo]
    ) -> List[PhotoPair]:
        """RAW/JPGファイルの対応関係を分析"""
        pairs = []
        # FileInfo は dataclass のため hashable ではない。
        # ファイルを一意に識別できる path で対応済みかどうかを管理する。
        matched_jpg_paths = set()

        # RAWファイルベースでペアを探す
        for raw in raw_files:
            raw_base = raw.stem
            matching_jpg = None

            for jpg in jpg_files:
                if jpg.path in matched_jpg_paths:
                    continue

                jpg_base = jpg.stem
                if self._is_matching_pair(raw_base, jpg_base):
                    matching_jpg = jpg
                    matched_jpg_paths.add(jpg.path)
                    break

            pairs.append(PhotoPair(raw_file=raw, jpg_file=matching_jpg))

        # 残りの孤立JPGファイルを追加
        for jpg in jpg_files:
            if jpg.path not in matched_jpg_paths:
                pairs.append(PhotoPair(raw_file=None, jpg_file=jpg))

        return pairs

    def _is_matching_pair(self, raw_base: str, jpg_base: str) -> bool:
        """RAWとJPGのファイル名が対応するかチェック"""
        # 基本的な名前一致
        if raw_base == jpg_base:
            return True

        # カメラによる命名規則の違いを考慮
        # 例: DSC01234.ARW と DSC01234.JPG
        # 例: _DSC1234.ARW と DSC1234.JPG
        raw_normalized = raw_base.lstrip("_").upper()
        jpg_normalized = jpg_base.lstrip("_").upper()

        return raw_normalized == jpg_normalized
