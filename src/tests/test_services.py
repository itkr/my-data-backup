"""
サービス層のテスト
"""

import logging
import shutil
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

from src.core.domain.models import FileInfo, FileType, OrganizationConfig
from src.core.services.move_service import MoveService
from src.core.services.photo_organizer_service import PhotoOrganizerService


class TestPhotoOrganizerService(unittest.TestCase):
    """PhotoOrganizerServiceクラスのテスト"""

    def setUp(self):
        """テスト前のセットアップ"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        # テスト用ログ設定
        self.logger = logging.getLogger("test")
        self.logger.setLevel(logging.INFO)

        # モックリポジトリを作成
        self.mock_repository = Mock()

        # サービスインスタンス作成
        self.service = PhotoOrganizerService(self.mock_repository, self.logger)

        # テストデータ準備
        self.source_dir = self.temp_path / "source"
        self.target_dir = self.temp_path / "target"

        self.raw_file = FileInfo(
            path=self.source_dir / "image.arw",
            file_type=FileType.RAW,
            created_date=datetime(2024, 1, 15),
            size=2048,
        )

        self.jpg_file = FileInfo(
            path=self.source_dir / "image.jpg",
            file_type=FileType.JPG,
            created_date=datetime(2024, 1, 15),
            size=1024,
        )

    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_find_photo_pairs_with_matching_files(self):
        """マッチングするファイルペアの検索テスト"""
        # モックの設定
        self.mock_repository.get_files_by_extensions.side_effect = [
            [self.raw_file],  # RAWファイル
            [self.jpg_file],  # JPGファイル
        ]

        pairs = self.service.find_photo_pairs(self.source_dir)

        self.assertEqual(len(pairs), 1)
        pair = pairs[0]
        self.assertTrue(pair.has_both)
        self.assertEqual(pair.raw_file.name, "image.arw")
        self.assertEqual(pair.jpg_file.name, "image.jpg")

    def test_find_photo_pairs_with_orphan_raw(self):
        """孤立RAWファイルの検索テスト"""
        orphan_raw = FileInfo(
            path=self.source_dir / "orphan.arw",
            file_type=FileType.RAW,
            created_date=datetime(2024, 1, 15),
            size=2048,
        )

        # モックの設定
        self.mock_repository.get_files_by_extensions.side_effect = [
            [self.raw_file, orphan_raw],  # RAWファイル
            [self.jpg_file],  # JPGファイル
        ]

        pairs = self.service.find_photo_pairs(self.source_dir)

        self.assertEqual(len(pairs), 2)

        # ペアになったファイル
        paired = [p for p in pairs if p.is_complete_pair][0]
        self.assertEqual(paired.raw_file.name, "image.arw")
        self.assertEqual(paired.jpg_file.name, "image.jpg")

        # 孤立RAWファイル
        orphan = [p for p in pairs if p.is_orphan_raw][0]
        self.assertEqual(orphan.raw_file.name, "orphan.arw")
        self.assertIsNone(orphan.jpg_file)

    def test_find_photo_pairs_with_orphan_jpg(self):
        """孤立JPGファイルの検索テスト"""
        orphan_jpg = FileInfo(
            path=self.source_dir / "orphan.jpg",
            file_type=FileType.JPG,
            created_date=datetime(2024, 1, 15),
            size=1024,
        )

        # モックの設定
        self.mock_repository.get_files_by_extensions.side_effect = [
            [self.raw_file],  # RAWファイル
            [self.jpg_file, orphan_jpg],  # JPGファイル
        ]

        pairs = self.service.find_photo_pairs(self.source_dir)

        self.assertEqual(len(pairs), 2)

        # ペアになったファイル
        paired = [p for p in pairs if p.is_complete_pair][0]
        self.assertEqual(paired.raw_file.name, "image.arw")
        self.assertEqual(paired.jpg_file.name, "image.jpg")

        # 孤立JPGファイル
        orphan = [p for p in pairs if p.is_orphan_jpg][0]
        self.assertEqual(orphan.jpg_file.name, "orphan.jpg")
        self.assertIsNone(orphan.raw_file)

    @patch("src.core.services.PhotoOrganizerService.find_photo_pairs")
    def test_organize_photos_dry_run(self, mock_find_pairs):
        """ドライランモードでの写真整理テスト"""
        # テスト用のフォトペアを設定
        from src.core.domain.models import PhotoPair

        test_pair = PhotoPair(raw_file=self.raw_file, jpg_file=self.jpg_file)
        mock_find_pairs.return_value = [test_pair]

        config = OrganizationConfig(dry_run=True)

        result = self.service.organize_photos(
            source_dir=self.source_dir, target_dir=self.target_dir, config=config
        )

        # ドライランではファイル操作が実行されない
        self.mock_repository.copy_file.assert_not_called()
        self.mock_repository.move_file.assert_not_called()

        # 結果の検証
        self.assertEqual(result.success_count, 1)
        self.assertEqual(result.error_count, 0)


class TestMoveService(unittest.TestCase):
    """MoveServiceクラスのテスト"""

    def setUp(self):
        """テスト前のセットアップ"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        # テスト用ログ設定
        self.logger = logging.getLogger("test")
        self.logger.setLevel(logging.INFO)

        # モックリポジトリを作成
        self.mock_repository = Mock()

        # サービスインスタンス作成
        self.service = MoveService(self.mock_repository, self.logger)

        # テストデータ準備
        self.source_dir = self.temp_path / "source"
        self.target_dir = self.temp_path / "target"

        self.test_file = FileInfo(
            path=self.source_dir / "test.jpg",
            file_type=FileType.JPG,
            created_date=datetime(2024, 1, 15, 10, 30, 0),
            size=1024,
        )

    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_date_path(self):
        """日付パス生成のテスト"""
        file_date = datetime(2024, 1, 15, 10, 30, 0)

        date_path = self.service._generate_date_path(file_date)

        self.assertEqual(date_path, Path("2024/01月/2024-01-15"))

    def test_generate_date_path_different_months(self):
        """異なる月の日付パス生成テスト"""
        test_cases = [
            (datetime(2024, 3, 5), "2024/03月/2024-03-05"),
            (datetime(2024, 12, 25), "2024/12月/2024-12-25"),
            (datetime(2023, 7, 1), "2023/07月/2023-07-01"),
        ]

        for file_date, expected in test_cases:
            with self.subTest(date=file_date):
                result = self.service._generate_date_path(file_date)
                self.assertEqual(result, Path(expected))

    def test_organize_by_date_dry_run(self):
        """ドライランモードでの日付別整理テスト"""
        # モックの設定
        self.service.file_repository.scan_directory = Mock(
            return_value=[self.test_file]
        )

        config = OrganizationConfig(dry_run=True)

        result = self.service.organize_by_date(
            source_dir=self.source_dir, target_dir=self.target_dir, config=config
        )

        # ドライランではファイル操作が実行されない
        self.mock_repository.create_directory.assert_not_called()
        self.mock_repository.move_file.assert_not_called()

        # 結果の検証
        self.assertEqual(result.success_count, 1)
        self.assertEqual(result.error_count, 0)

    def test_get_target_path(self):
        """ターゲットパス取得のテスト"""
        config = OrganizationConfig(create_date_dirs=True, create_type_dirs=True)

        target_path = self.service._get_target_path(
            self.test_file, self.target_dir, config
        )

        expected = self.target_dir / "2024/01月/2024-01-15/JPG/test.jpg"
        self.assertEqual(target_path, expected)

    def test_get_target_path_no_date_dirs(self):
        """日付ディレクトリなしのターゲットパス取得テスト"""
        config = OrganizationConfig(create_date_dirs=False, create_type_dirs=True)

        target_path = self.service._get_target_path(
            self.test_file, self.target_dir, config
        )

        expected = self.target_dir / "JPG/test.jpg"
        self.assertEqual(target_path, expected)

    def test_get_target_path_no_type_dirs(self):
        """タイプディレクトリなしのターゲットパス取得テスト"""
        config = OrganizationConfig(create_date_dirs=True, create_type_dirs=False)

        target_path = self.service._get_target_path(
            self.test_file, self.target_dir, config
        )

        expected = self.target_dir / "2024/01月/2024-01-15/test.jpg"
        self.assertEqual(target_path, expected)


if __name__ == "__main__":
    unittest.main()
