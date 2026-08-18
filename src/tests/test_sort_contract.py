"""
samples/move.sh の契約を固定する回帰テスト

move.sh は各所からシンボリックリンクで参照されており、実ファイルを
dry-run なしで移動する。リファクタリング中にこの挙動が変わっていない
ことを保証するため、モックを使わず実ファイルで end-to-end に検証する。

固定している契約:
  - 出力構造は `<年>/<月>月/<YYYY-MM-DD>/<拡張子>/<ファイル名>`
  - 拡張子ディレクトリは常に大文字（ARW/, JPG/）
  - recursive=False なのでサブディレクトリは走査しない
  - 対象外拡張子のファイルはその場に残る
  - 移動なので元の場所からは消える
"""

import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from src.core.domain.models import OrganizationConfig
from src.core.services.sort_service import SortService
from src.infrastructure.repositories import FileSystemRepository

# 2024-03-05 12:00 に固定したタイムスタンプ
FIXED_MTIME = datetime(2024, 3, 5, 12, 0, 0).timestamp()


class TestMoveShContract(unittest.TestCase):
    """samples/move.sh が依存する SortService の挙動"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.work = Path(self._tmp.name) / "work"
        (self.work / "subdir").mkdir(parents=True)

        self.service = SortService(FileSystemRepository())

    def tearDown(self):
        self._tmp.cleanup()

    def _make_file(self, relative_path: str) -> Path:
        path = self.work / relative_path
        path.write_text(f"data-{relative_path}")
        os.utime(path, (FIXED_MTIME, FIXED_MTIME))
        return path

    def _run_move(self) -> None:
        """move.sh と同じ引数で実行（import 元 == export 先、dry-run なし）"""
        config = OrganizationConfig(
            dry_run=False,
            create_date_dirs=True,
            create_type_dirs=True,
            handle_duplicates=True,
            log_operations=True,
            preserve_original=False,
            file_extensions=None,
            recursive=False,
        )
        self.result = self.service.sort_by_date(self.work, self.work, config)

    def _relative_paths(self) -> set:
        return {
            str(p.relative_to(self.work)) for p in self.work.rglob("*") if p.is_file()
        }

    def test_organizes_into_date_and_extension_directories(self):
        """日付＋拡張子のディレクトリ構造に整理される"""
        self._make_file("b.jpg")
        self._make_file("e.mov")

        self._run_move()

        self.assertIn("2024/03月/2024-03-05/JPG/b.jpg", self._relative_paths())
        self.assertIn("2024/03月/2024-03-05/MOV/e.mov", self._relative_paths())

    def test_moves_rather_than_copies(self):
        """コピーではなく移動（元の場所から消える）"""
        source = self._make_file("b.jpg")

        self._run_move()

        self.assertFalse(source.exists())
        self.assertEqual(self.result.success_count, 1)
        self.assertEqual(self.result.error_count, 0)

    def test_subdirectories_are_not_traversed(self):
        """recursive=False: サブディレクトリのファイルは触らない"""
        nested = self._make_file("subdir/nested.jpg")

        self._run_move()

        self.assertTrue(nested.exists())
        self.assertIn("subdir/nested.jpg", self._relative_paths())

    def test_unsupported_extensions_are_left_in_place(self):
        """対象外拡張子（.png など）はその場に残る"""
        untouched = self._make_file("g.png")

        self._run_move()

        self.assertTrue(untouched.exists())
        self.assertIn("g.png", self._relative_paths())

    def test_extension_directory_is_always_uppercase(self):
        """大文字小文字が混在しても拡張子ディレクトリは常に大文字にまとまる

        元ファイルの綴りをそのまま使うと、macOS のような大文字小文字を
        区別しないファイルシステムでは綴りが処理順に依存して非決定的になる。
        """
        self._make_file("c.ARW")
        self._make_file("d.arw")

        self._run_move()

        self.assertEqual(
            {"2024/03月/2024-03-05/ARW/c.ARW", "2024/03月/2024-03-05/ARW/d.arw"},
            self._relative_paths(),
        )


if __name__ == "__main__":
    unittest.main()
