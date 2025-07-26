"""
ドメインモデル定義
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional


class FileType(Enum):
    """ファイルタイプ列挙型"""
    RAW = "raw"
    JPG = "jpg"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    OTHER = "other"


class OperationType(Enum):
    """操作タイプ列挙型"""
    MOVE = "move"
    COPY = "copy"
    DELETE = "delete"


@dataclass
class FileInfo:
    """ファイル情報のドメインモデル"""
    path: Path
    file_type: FileType
    created_date: datetime
    size: int
    checksum: Optional[str] = None
    
    @property
    def extension(self) -> str:
        """ファイル拡張子を取得"""
        return self.path.suffix.lower()
    
    @property
    def stem(self) -> str:
        """ファイル名（拡張子なし）を取得"""
        return self.path.stem
    
    @property
    def name(self) -> str:
        """ファイル名を取得"""
        return self.path.name


@dataclass
class ProcessResult:
    """処理結果のドメインモデル"""
    success_count: int = 0
    error_count: int = 0
    processed_files: List[FileInfo] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.processed_files is None:
            self.processed_files = []
        if self.errors is None:
            self.errors = []
    
    @property
    def total_count(self) -> int:
        """総処理ファイル数"""
        return self.success_count + self.error_count
    
    @property
    def success_rate(self) -> float:
        """成功率（0.0-1.0）"""
        if self.total_count == 0:
            return 0.0
        return self.success_count / self.total_count


@dataclass
class FileOperation:
    """ファイル操作のドメインモデル"""
    source: Path
    destination: Path
    operation: OperationType
    file_info: FileInfo
    executed: bool = False
    error: Optional[str] = None


@dataclass
class PhotoPair:
    """RAW/JPGペアのドメインモデル"""
    raw_file: Optional[FileInfo] = None
    jpg_file: Optional[FileInfo] = None
    
    @property
    def is_complete_pair(self) -> bool:
        """完全なペアかどうか"""
        return self.raw_file is not None and self.jpg_file is not None
    
    @property
    def is_orphan_raw(self) -> bool:
        """孤立RAWファイルかどうか"""
        return self.raw_file is not None and self.jpg_file is None
    
    @property
    def is_orphan_jpg(self) -> bool:
        """孤立JPGファイルかどうか"""
        return self.raw_file is None and self.jpg_file is not None


@dataclass 
class OrganizationConfig:
    """整理設定のドメインモデル"""
    dry_run: bool = True
    create_date_dirs: bool = True
    create_type_dirs: bool = True
    handle_duplicates: bool = True
    log_operations: bool = True
    preserve_original: bool = False
