"""
ファイル整理サービスの基底クラス
"""

import logging
from pathlib import Path
from typing import Optional

from src.core.domain.models import OrganizationConfig
from src.core.domain.repositories import FileRepository


class FileOrganizerService:
    """ファイル整理サービスに共通する処理"""

    def __init__(
        self, file_repository: FileRepository, logger: Optional[logging.Logger] = None
    ):
        self.file_repository = file_repository
        self.logger = logger or logging.getLogger(__name__)

    def _execute_file_operation(
        self, source: Path, destination: Path, config: OrganizationConfig
    ) -> bool:
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
