#!/usr/bin/env python3
"""
Move機能の拡張子大文字・小文字保持テスト
"""

import tempfile
from datetime import datetime
from pathlib import Path

from src.core.domain.models import FileInfo, FileType, OrganizationConfig
from src.core.services.move_service import MoveService
from src.infrastructure.repositories import FileSystemRepository
from src.infrastructure.logging import get_logger


def test_extension_case_preservation():
    """拡張子の大文字・小文字保持テスト"""
    print("🧪 拡張子大文字・小文字保持テスト開始")
    
    # ログ設定
    logger = get_logger("TestMoveExtensionCase")
    
    # サービス初期化
    file_repository = FileSystemRepository(logger.logger)
    move_service = MoveService(file_repository, logger.logger)
    
    # テスト用ファイル情報作成（大文字・小文字混在）
    test_cases = [
        # 大文字拡張子
        FileInfo(
            path=Path("/test/image.JPG"),
            file_type=FileType.JPG,
            created_date=datetime(2024, 1, 15, 10, 30, 0),
            size=1024
        ),
        # 小文字拡張子
        FileInfo(
            path=Path("/test/photo.jpg"),
            file_type=FileType.JPG,
            created_date=datetime(2024, 1, 15, 10, 30, 0),
            size=2048
        ),
        # RAW大文字
        FileInfo(
            path=Path("/test/raw_photo.ARW"),
            file_type=FileType.RAW,
            created_date=datetime(2024, 1, 15, 10, 30, 0),
            size=4096
        ),
        # RAW小文字
        FileInfo(
            path=Path("/test/raw_photo2.arw"),
            file_type=FileType.RAW,
            created_date=datetime(2024, 1, 15, 10, 30, 0),
            size=4096
        ),
    ]
    
    # 設定
    config = OrganizationConfig(
        create_date_dirs=True,
        create_type_dirs=True,
        dry_run=True  # ドライラン
    )
    
    base_dir = Path("/export")
    
    print("📋 テスト対象:")
    for i, file_info in enumerate(test_cases, 1):
        target_path = move_service._generate_target_path(file_info, base_dir, config)
        extension_dir = target_path.parent.name
        
        print(f"  {i}. {file_info.name} (拡張子: {file_info.raw_extension})")
        print(f"     → ディレクトリ: {extension_dir}")
        print(f"     → フルパス: {target_path}")
        
        # 拡張子ディレクトリ名の検証
        expected_ext = file_info.raw_extension.lstrip(".")
        if extension_dir == expected_ext:
            print(f"     ✅ 大文字・小文字が正しく保持されています")
        else:
            print(f"     ❌ 期待値: {expected_ext}, 実際: {extension_dir}")
        print()
    
    print("🎉 拡張子大文字・小文字保持テスト完了")


if __name__ == "__main__":
    test_extension_case_preservation()
