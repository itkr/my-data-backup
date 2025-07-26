"""
リポジトリのテスト
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import sys
import logging

# プロジェクトルートをPythonパスに追加
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.infrastructure.repositories import FileSystemRepository
from src.core.domain.models import FileInfo


class TestFileSystemRepository(unittest.TestCase):
    """FileSystemRepositoryクラスのテスト"""

    def setUp(self):
        """テスト前のセットアップ"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        # テスト用ログ設定
        self.logger = logging.getLogger("test")
        self.logger.setLevel(logging.INFO)

        # リポジトリインスタンス作成
        self.repository = FileSystemRepository(self.logger)

        # テスト用ファイルを作成
        self.test_files = []
        for i, ext in enumerate([".jpg", ".arw", ".txt"], 1):
            test_file = self.temp_path / f"test{i}{ext}"
            test_file.write_text(f"Test content {i}")
            self.test_files.append(test_file)

    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_files_by_extensions(self):
        """拡張子別ファイル取得のテスト"""
        # JPGファイルを取得
        jpg_files = self.repository.get_files_by_extensions(self.temp_path, [".jpg"])

        self.assertEqual(len(jpg_files), 1)
        self.assertEqual(jpg_files[0].extension, ".jpg")
        self.assertEqual(jpg_files[0].name, "test1.jpg")

        # 複数拡張子の取得
        image_files = self.repository.get_files_by_extensions(
            self.temp_path, [".jpg", ".arw"]
        )

        self.assertEqual(len(image_files), 2)
        extensions = {f.extension for f in image_files}
        self.assertEqual(extensions, {".jpg", ".arw"})

    def test_get_files_by_extensions_empty_directory(self):
        """空ディレクトリでのファイル取得テスト"""
        empty_dir = self.temp_path / "empty"
        empty_dir.mkdir()

        files = self.repository.get_files_by_extensions(empty_dir, [".jpg", ".arw"])

        self.assertEqual(len(files), 0)

    def test_get_files_by_extensions_nonexistent_directory(self):
        """存在しないディレクトリでのファイル取得テスト"""
        nonexistent_dir = self.temp_path / "nonexistent"

        files = self.repository.get_files_by_extensions(nonexistent_dir, [".jpg"])

        self.assertEqual(len(files), 0)

    def test_create_directory(self):
        """ディレクトリ作成のテスト"""
        new_dir = self.temp_path / "new_directory"

        # ディレクトリが存在しないことを確認
        self.assertFalse(new_dir.exists())

        # ディレクトリを作成
        success = self.repository.create_directory(new_dir)

        # 作成が成功し、ディレクトリが存在することを確認
        self.assertTrue(success)
        self.assertTrue(new_dir.exists())
        self.assertTrue(new_dir.is_dir())

    def test_create_directory_already_exists(self):
        """既存ディレクトリ作成のテスト"""
        existing_dir = self.temp_path / "existing"
        existing_dir.mkdir()

        # 既存ディレクトリの作成は成功する
        success = self.repository.create_directory(existing_dir)

        self.assertTrue(success)
        self.assertTrue(existing_dir.exists())

    def test_create_nested_directory(self):
        """ネストされたディレクトリ作成のテスト"""
        nested_dir = self.temp_path / "level1" / "level2" / "level3"

        success = self.repository.create_directory(nested_dir)

        self.assertTrue(success)
        self.assertTrue(nested_dir.exists())
        self.assertTrue(nested_dir.is_dir())

    def test_copy_file(self):
        """ファイルコピーのテスト"""
        source_file = self.test_files[0]  # test1.jpg
        target_dir = self.temp_path / "target"
        target_dir.mkdir()
        target_file = target_dir / source_file.name

        success = self.repository.copy_file(source_file, target_file)

        self.assertTrue(success)
        self.assertTrue(target_file.exists())
        self.assertEqual(source_file.read_text(), target_file.read_text())
        # オリジナルファイルが残っていることを確認
        self.assertTrue(source_file.exists())

    def test_copy_file_with_directory_creation(self):
        """ディレクトリ作成付きファイルコピーのテスト"""
        source_file = self.test_files[0]
        target_file = self.temp_path / "new_dir" / "subdir" / source_file.name

        success = self.repository.copy_file(source_file, target_file)

        self.assertTrue(success)
        self.assertTrue(target_file.exists())
        self.assertEqual(source_file.read_text(), target_file.read_text())

    def test_move_file(self):
        """ファイル移動のテスト"""
        source_file = self.test_files[0]  # test1.jpg
        original_content = source_file.read_text()
        target_dir = self.temp_path / "target"
        target_dir.mkdir()
        target_file = target_dir / source_file.name

        success = self.repository.move_file(source_file, target_file)

        self.assertTrue(success)
        self.assertTrue(target_file.exists())
        self.assertEqual(original_content, target_file.read_text())
        # オリジナルファイルが削除されていることを確認
        self.assertFalse(source_file.exists())

    def test_move_file_with_directory_creation(self):
        """ディレクトリ作成付きファイル移動のテスト"""
        source_file = self.test_files[1]  # test2.arw
        original_content = source_file.read_text()
        target_file = self.temp_path / "new_dir" / "subdir" / source_file.name

        success = self.repository.move_file(source_file, target_file)

        self.assertTrue(success)
        self.assertTrue(target_file.exists())
        self.assertEqual(original_content, target_file.read_text())
        self.assertFalse(source_file.exists())

    def test_copy_file_nonexistent_source(self):
        """存在しないソースファイルのコピーテスト"""
        nonexistent_file = self.temp_path / "nonexistent.jpg"
        target_file = self.temp_path / "target.jpg"

        success = self.repository.copy_file(nonexistent_file, target_file)

        self.assertFalse(success)
        self.assertFalse(target_file.exists())

    def test_move_file_nonexistent_source(self):
        """存在しないソースファイルの移動テスト"""
        nonexistent_file = self.temp_path / "nonexistent.jpg"
        target_file = self.temp_path / "target.jpg"

        success = self.repository.move_file(nonexistent_file, target_file)

        self.assertFalse(success)
        self.assertFalse(target_file.exists())


if __name__ == "__main__":
    unittest.main()
