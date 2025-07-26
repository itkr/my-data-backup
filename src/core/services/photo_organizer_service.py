"""
Photo Organizer サービス
"""

from pathlib import Path
from typing import List, Tuple, Optional, Callable
import logging

from ..domain.models import (
    FileInfo, FileType, ProcessResult, PhotoPair, 
    OrganizationConfig, FileOperation, OperationType
)
from ..domain.repositories import FileRepository


class PhotoOrganizerService:
    """
    Photo Organizer のビジネスロジックを実装するサービス
    
    責任:
    - RAW/JPGファイルの対応関係の判定
    - ファイルの同期処理ロジック
    - 孤立ファイルの管理
    - 処理結果の集計
    """
    
    def __init__(self, file_repository: FileRepository, logger: Optional[logging.Logger] = None):
        self.file_repository = file_repository
        self.logger = logger or logging.getLogger(__name__)
    
    def organize_photos(
        self, 
        source_dir: Path, 
        target_dir: Path,
        config: OrganizationConfig,
        progress_callback: Optional[Callable[[int, int], None]] = None
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
        
        self.logger.info(f"ペア分析完了: 完全ペア={len(complete_pairs)}, 孤立RAW={len(orphan_raws)}, 孤立JPG={len(orphan_jpgs)}")
        
        # 4. ファイル処理
        result = ProcessResult()
        
        total_items = len(complete_pairs) + len(orphan_raws) + len(orphan_jpgs)
        processed = 0
        
        # 完全ペアの処理
        for pair in complete_pairs:
            success = self._process_photo_pair(pair, target_dir, config)
            if success:
                result.success_count += 2
                result.processed_files.extend([pair.raw_file, pair.jpg_file])
            else:
                result.error_count += 2
                result.errors.append(f"ペア処理失敗: {pair.raw_file.name} + {pair.jpg_file.name}")
            
            processed += 1
            if progress_callback:
                progress_callback(processed, total_items)
        
        # 孤立ファイルの処理
        for pair in orphan_raws + orphan_jpgs:
            orphan_file = pair.raw_file or pair.jpg_file
            success = self._process_orphan_file(orphan_file, target_dir, config)
            if success:
                result.success_count += 1
                result.processed_files.append(orphan_file)
            else:
                result.error_count += 1
                result.errors.append(f"孤立ファイル処理失敗: {orphan_file.name}")
            
            processed += 1
            if progress_callback:
                progress_callback(processed, total_items)
        
        self.logger.info(f"写真整理完了: 成功={result.success_count}, 失敗={result.error_count}")
        return result
    
    def _classify_photo_files(self, files: List[FileInfo]) -> Tuple[List[FileInfo], List[FileInfo]]:
        """ファイルをRAWとJPGに分類"""
        raw_files = [f for f in files if f.file_type == FileType.RAW]
        jpg_files = [f for f in files if f.file_type == FileType.JPG]
        return raw_files, jpg_files
    
    def _analyze_photo_pairs(self, raw_files: List[FileInfo], jpg_files: List[FileInfo]) -> List[PhotoPair]:
        """RAW/JPGファイルの対応関係を分析"""
        pairs = []
        matched_jpgs = set()
        
        # RAWファイルベースでペアを探す
        for raw in raw_files:
            raw_base = raw.stem
            matching_jpg = None
            
            for jpg in jpg_files:
                if jpg in matched_jpgs:
                    continue
                    
                jpg_base = jpg.stem
                if self._is_matching_pair(raw_base, jpg_base):
                    matching_jpg = jpg
                    matched_jpgs.add(jpg)
                    break
            
            pairs.append(PhotoPair(raw_file=raw, jpg_file=matching_jpg))
        
        # 残りの孤立JPGファイルを追加
        for jpg in jpg_files:
            if jpg not in matched_jpgs:
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
        raw_normalized = raw_base.lstrip('_').upper()
        jpg_normalized = jpg_base.lstrip('_').upper()
        
        return raw_normalized == jpg_normalized
    
    def _process_photo_pair(self, pair: PhotoPair, target_dir: Path, config: OrganizationConfig) -> bool:
        """ペアファイルの処理"""
        try:
            # ターゲットディレクトリの準備
            raw_target_dir = target_dir / "ARW"
            jpg_target_dir = target_dir / "JPG"
            
            if not config.dry_run:
                self.file_repository.create_directory(raw_target_dir)
                self.file_repository.create_directory(jpg_target_dir)
            
            # RAWファイルの処理
            raw_target = raw_target_dir / pair.raw_file.name
            raw_success = self._execute_file_operation(
                pair.raw_file.path, raw_target, config
            )
            
            # JPGファイルの処理
            jpg_target = jpg_target_dir / pair.jpg_file.name
            jpg_success = self._execute_file_operation(
                pair.jpg_file.path, jpg_target, config
            )
            
            return raw_success and jpg_success
            
        except Exception as e:
            self.logger.error(f"ペア処理エラー: {e}")
            return False
    
    def _process_orphan_file(self, file: FileInfo, target_dir: Path, config: OrganizationConfig) -> bool:
        """孤立ファイルの処理"""
        try:
            # 孤立ファイル用ディレクトリ
            orphan_dir = target_dir / "orphans"
            
            if not config.dry_run:
                self.file_repository.create_directory(orphan_dir)
            
            target = orphan_dir / file.name
            return self._execute_file_operation(file.path, target, config)
            
        except Exception as e:
            self.logger.error(f"孤立ファイル処理エラー: {e}")
            return False
    
    def _execute_file_operation(self, source: Path, destination: Path, config: OrganizationConfig) -> bool:
        """ファイル操作の実行"""
        if config.dry_run:
            self.logger.info(f"[DRY RUN] {source} -> {destination}")
            return True
        
        try:
            if config.preserve_original:
                return self.file_repository.copy_file(source, destination)
            else:
                return self.file_repository.move_file(source, destination)
        except Exception as e:
            self.logger.error(f"ファイル操作エラー: {e}")
            return False
