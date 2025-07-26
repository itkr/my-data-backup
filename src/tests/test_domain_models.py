"""
ドメインモデルのテスト
"""

import unittest
from datetime import datetime
from pathlib import Path

from src.core.domain.models import (
    FileInfo,
    FileType,
    OrganizationConfig,
    PhotoPair,
    ProcessResult,
)


class TestFileInfo(unittest.TestCase):
    """FileInfoクラスのテスト"""

    def test_file_info_creation(self):
        """FileInfoの作成テスト"""
        file_path = Path("/test/path/image.jpg")
        file_info = FileInfo(
            path=file_path,
            file_type=FileType.JPG,
            created_date=datetime(2024, 1, 15, 10, 30, 0),
            size=1024,
        )

        self.assertEqual(file_info.path, file_path)
        self.assertEqual(file_info.name, "image.jpg")
        self.assertEqual(file_info.size, 1024)
        self.assertEqual(file_info.extension, ".jpg")
        self.assertEqual(file_info.created_date.year, 2024)
        self.assertEqual(file_info.file_type, FileType.JPG)

    def test_file_info_str_representation(self):
        """FileInfoの文字列表現テスト"""
        file_info = FileInfo(
            path=Path("/test/image.jpg"),
            file_type=FileType.JPG,
            created_date=datetime(2024, 1, 15),
            size=1024,
        )

        str_repr = str(file_info)
        self.assertIn("image.jpg", str_repr)
        self.assertIn("1024", str_repr)


class TestProcessResult(unittest.TestCase):
    """ProcessResultクラスのテスト"""

    def test_process_result_creation(self):
        """ProcessResultの作成テスト"""
        file_info = FileInfo(
            path=Path("/test/image.jpg"),
            file_type=FileType.JPG,
            created_date=datetime.now(),
            size=1024,
        )

        result = ProcessResult(
            success_count=5,
            error_count=1,
            processed_files=[file_info],
            errors=["Test error"],
        )

        self.assertEqual(result.success_count, 5)
        self.assertEqual(result.error_count, 1)
        self.assertEqual(len(result.processed_files), 1)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.total_count, 6)
        self.assertAlmostEqual(result.success_rate, 5 / 6, places=2)

    def test_empty_process_result(self):
        """空のProcessResultのテスト"""
        result = ProcessResult()

        self.assertEqual(result.success_count, 0)
        self.assertEqual(result.error_count, 0)
        self.assertEqual(result.total_count, 0)
        self.assertEqual(result.success_rate, 0.0)
        self.assertEqual(len(result.processed_files), 0)
        self.assertEqual(len(result.errors), 0)


class TestPhotoPair(unittest.TestCase):
    """PhotoPairクラスのテスト"""

    def test_photo_pair_creation(self):
        """PhotoPairの作成テスト"""
        raw_file = FileInfo(
            path=Path("/test/image.arw"),
            file_type=FileType.RAW,
            created_date=datetime.now(),
            size=2048,
        )

        jpg_file = FileInfo(
            path=Path("/test/image.jpg"),
            file_type=FileType.JPG,
            created_date=datetime.now(),
            size=1024,
        )

        pair = PhotoPair(raw_file=raw_file, jpg_file=jpg_file)

        self.assertEqual(pair.raw_file, raw_file)
        self.assertEqual(pair.jpg_file, jpg_file)
        self.assertTrue(pair.is_complete_pair)
        self.assertFalse(pair.is_orphan_raw)
        self.assertFalse(pair.is_orphan_jpg)

    def test_orphan_raw_file(self):
        """孤立RAWファイルのテスト"""
        raw_file = FileInfo(
            path=Path("/test/image.arw"),
            file_type=FileType.RAW,
            created_date=datetime.now(),
            size=2048,
        )

        pair = PhotoPair(raw_file=raw_file, jpg_file=None)

        self.assertEqual(pair.raw_file, raw_file)
        self.assertIsNone(pair.jpg_file)
        self.assertFalse(pair.is_complete_pair)
        self.assertTrue(pair.is_orphan_raw)
        self.assertFalse(pair.is_orphan_jpg)

    def test_orphan_jpg_file(self):
        """孤立JPGファイルのテスト"""
        jpg_file = FileInfo(
            path=Path("/test/image.jpg"),
            file_type=FileType.JPG,
            created_date=datetime.now(),
            size=1024,
        )

        pair = PhotoPair(raw_file=None, jpg_file=jpg_file)

        self.assertIsNone(pair.raw_file)
        self.assertEqual(pair.jpg_file, jpg_file)
        self.assertFalse(pair.is_complete_pair)
        self.assertFalse(pair.is_orphan_raw)
        self.assertTrue(pair.is_orphan_jpg)


class TestOrganizationConfig(unittest.TestCase):
    """OrganizationConfigクラスのテスト"""

    def test_default_config(self):
        """デフォルト設定のテスト"""
        config = OrganizationConfig()

        self.assertTrue(config.dry_run)
        self.assertTrue(config.create_date_dirs)
        self.assertTrue(config.create_type_dirs)
        self.assertTrue(config.handle_duplicates)
        self.assertTrue(config.log_operations)
        self.assertFalse(config.preserve_original)

    def test_custom_config(self):
        """カスタム設定のテスト"""
        config = OrganizationConfig(
            dry_run=False, create_date_dirs=False, preserve_original=True
        )

        self.assertFalse(config.dry_run)
        self.assertFalse(config.create_date_dirs)
        self.assertTrue(config.preserve_original)
        # デフォルト値が保持されることを確認
        self.assertTrue(config.create_type_dirs)
        self.assertTrue(config.handle_duplicates)


if __name__ == "__main__":
    unittest.main()
