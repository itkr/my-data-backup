"""
サービス層のテスト
"""

import logging
import shutil
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

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

    def test_analyze_photo_pairs_with_matching_files(self):
        """同名のRAW/JPGが1つのペアとして認識される"""
        pairs = self.service._analyze_photo_pairs([self.raw_file], [self.jpg_file])

        self.assertEqual(len(pairs), 1)
        pair = pairs[0]
        self.assertTrue(pair.is_complete_pair)
        self.assertEqual(pair.raw_file.name, "image.arw")
        self.assertEqual(pair.jpg_file.name, "image.jpg")

    def test_analyze_photo_pairs_with_orphan_raw(self):
        """対応するJPGが無いRAWは孤立RAWになる"""
        orphan_raw = FileInfo(
            path=self.source_dir / "orphan.arw",
            file_type=FileType.RAW,
            created_date=datetime(2024, 1, 15),
            size=2048,
        )

        pairs = self.service._analyze_photo_pairs(
            [self.raw_file, orphan_raw], [self.jpg_file]
        )

        self.assertEqual(len(pairs), 2)

        paired = [p for p in pairs if p.is_complete_pair][0]
        self.assertEqual(paired.raw_file.name, "image.arw")
        self.assertEqual(paired.jpg_file.name, "image.jpg")

        orphan = [p for p in pairs if p.is_orphan_raw][0]
        self.assertEqual(orphan.raw_file.name, "orphan.arw")
        self.assertIsNone(orphan.jpg_file)

    def test_analyze_photo_pairs_with_orphan_jpg(self):
        """対応するRAWが無いJPGは孤立JPGになる"""
        orphan_jpg = FileInfo(
            path=self.source_dir / "orphan.jpg",
            file_type=FileType.JPG,
            created_date=datetime(2024, 1, 15),
            size=1024,
        )

        pairs = self.service._analyze_photo_pairs(
            [self.raw_file], [self.jpg_file, orphan_jpg]
        )

        self.assertEqual(len(pairs), 2)

        paired = [p for p in pairs if p.is_complete_pair][0]
        self.assertEqual(paired.raw_file.name, "image.arw")
        self.assertEqual(paired.jpg_file.name, "image.jpg")

        orphan = [p for p in pairs if p.is_orphan_jpg][0]
        self.assertEqual(orphan.jpg_file.name, "orphan.jpg")
        self.assertIsNone(orphan.raw_file)

    def test_analyze_photo_pairs_ignores_leading_underscore_and_case(self):
        """_DSC1234.ARW と DSC1234.JPG のような命名差を吸収する"""
        raw = FileInfo(
            path=self.source_dir / "_DSC1234.arw",
            file_type=FileType.RAW,
            created_date=datetime(2024, 1, 15),
            size=2048,
        )
        jpg = FileInfo(
            path=self.source_dir / "dsc1234.jpg",
            file_type=FileType.JPG,
            created_date=datetime(2024, 1, 15),
            size=1024,
        )

        pairs = self.service._analyze_photo_pairs([raw], [jpg])

        self.assertEqual(len(pairs), 1)
        self.assertTrue(pairs[0].is_complete_pair)

    def test_organize_photos_dry_run(self):
        """ドライランではファイル操作が実行されない"""
        self.mock_repository.scan_directory.return_value = [
            self.raw_file,
            self.jpg_file,
        ]

        config = OrganizationConfig(dry_run=True)

        result = self.service.organize_photos(
            source_dir=self.source_dir, target_dir=self.target_dir, config=config
        )

        # ドライランではファイル操作もディレクトリ作成も行われない
        self.mock_repository.copy_file.assert_not_called()
        self.mock_repository.move_file.assert_not_called()
        self.mock_repository.create_directory.assert_not_called()

        # 完全ペア1組 = RAW/JPG の2ファイル分が成功として数えられる
        self.assertEqual(result.success_count, 2)
        self.assertEqual(result.error_count, 0)

    def test_organize_photos_moves_pair_into_type_directories(self):
        """完全ペアは ARW/ と JPG/ に振り分けられる"""
        self.mock_repository.scan_directory.return_value = [
            self.raw_file,
            self.jpg_file,
        ]
        self.mock_repository.move_file.return_value = True

        config = OrganizationConfig(dry_run=False, preserve_original=False)

        self.service.organize_photos(
            source_dir=self.source_dir, target_dir=self.target_dir, config=config
        )

        destinations = {
            call.args[1] for call in self.mock_repository.move_file.call_args_list
        }
        self.assertIn(self.target_dir / "ARW" / "image.arw", destinations)
        self.assertIn(self.target_dir / "JPG" / "image.jpg", destinations)

    def test_organize_photos_moves_orphan_into_orphans_directory(self):
        """孤立ファイルは orphans/ に振り分けられる"""
        self.mock_repository.scan_directory.return_value = [self.raw_file]
        self.mock_repository.move_file.return_value = True

        config = OrganizationConfig(dry_run=False, preserve_original=False)

        self.service.organize_photos(
            source_dir=self.source_dir, target_dir=self.target_dir, config=config
        )

        destinations = {
            call.args[1] for call in self.mock_repository.move_file.call_args_list
        }
        self.assertEqual(destinations, {self.target_dir / "orphans" / "image.arw"})


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
        # exists() の戻り値を明示しないと Mock が truthy を返し、
        # 重複回避の _generate_unique_path が無限ループする
        self.mock_repository.exists.return_value = False

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

    def test_generate_target_path(self):
        """ターゲットパス生成のテスト"""
        config = OrganizationConfig(create_date_dirs=True, create_type_dirs=True)

        target_path = self.service._generate_target_path(
            self.test_file, self.target_dir, config
        )

        expected = self.target_dir / "2024/01月/2024-01-15/JPG/test.jpg"
        self.assertEqual(target_path, expected)

    def test_generate_target_path_no_date_dirs(self):
        """日付ディレクトリなしのターゲットパス生成テスト"""
        config = OrganizationConfig(create_date_dirs=False, create_type_dirs=True)

        target_path = self.service._generate_target_path(
            self.test_file, self.target_dir, config
        )

        expected = self.target_dir / "JPG/test.jpg"
        self.assertEqual(target_path, expected)

    def test_generate_target_path_no_type_dirs(self):
        """タイプディレクトリなしのターゲットパス生成テスト"""
        config = OrganizationConfig(create_date_dirs=True, create_type_dirs=False)

        target_path = self.service._generate_target_path(
            self.test_file, self.target_dir, config
        )

        expected = self.target_dir / "2024/01月/2024-01-15/test.jpg"
        self.assertEqual(target_path, expected)

    def test_copy_mode_preserves_the_original(self):
        """preserve_original=True のときは移動ではなくコピーする"""
        self.mock_repository.scan_directory.return_value = [self.test_file]
        self.mock_repository.copy_file.return_value = True

        config = OrganizationConfig(dry_run=False, preserve_original=True)

        self.service.organize_by_date(
            source_dir=self.source_dir, target_dir=self.target_dir, config=config
        )

        self.mock_repository.copy_file.assert_called_once()
        self.mock_repository.move_file.assert_not_called()

    def test_generate_unique_path_skips_existing_files(self):
        """重複時は連番を付けて空いているパスを返す"""
        taken = self.target_dir / "test_001.jpg"
        self.mock_repository.exists.side_effect = lambda p: p == taken

        unique = self.service._generate_unique_path(self.target_dir / "test.jpg")

        self.assertEqual(unique, self.target_dir / "test_002.jpg")

    def test_generate_unique_path_gives_up_instead_of_looping_forever(self):
        """空きが見つからない場合は無限ループせずエラーにする"""
        self.mock_repository.exists.return_value = True

        with self.assertRaises(RuntimeError):
            self.service._generate_unique_path(self.target_dir / "test.jpg")

    def test_stop_interrupts_processing(self):
        """stop() を呼ぶと残りのファイル処理が中断される"""
        second_file = FileInfo(
            path=self.source_dir / "second.jpg",
            file_type=FileType.JPG,
            created_date=datetime(2024, 1, 15, 10, 30, 0),
            size=1024,
        )
        self.mock_repository.scan_directory.return_value = [
            self.test_file,
            second_file,
        ]

        # 1件目の移動が終わった時点で停止を要求する
        def move_then_stop(source, destination):
            self.service.stop()
            return True

        self.mock_repository.move_file.side_effect = move_then_stop

        config = OrganizationConfig(dry_run=False, preserve_original=False)

        result = self.service.organize_by_date(
            source_dir=self.source_dir, target_dir=self.target_dir, config=config
        )

        # 2件目は処理されない
        self.assertEqual(self.mock_repository.move_file.call_count, 1)
        self.assertEqual(result.success_count, 1)

    def test_stop_flag_is_reset_on_next_run(self):
        """停止後に再実行すると最初から処理できる"""
        self.mock_repository.scan_directory.return_value = [self.test_file]
        self.mock_repository.move_file.return_value = True

        self.service.stop()

        config = OrganizationConfig(dry_run=False, preserve_original=False)
        result = self.service.organize_by_date(
            source_dir=self.source_dir, target_dir=self.target_dir, config=config
        )

        self.assertEqual(result.success_count, 1)


if __name__ == "__main__":
    unittest.main()
