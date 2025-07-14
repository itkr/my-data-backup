import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import click

# 共通ログ機構をインポート
sys.path.append(str(Path(__file__).parent.parent))
from common.logger import UnifiedLogger


# 対応ファイル拡張子の定義
SUPPORTED_EXTENSIONS = {
    "images": ["JPEG", "JPG", "PNG", "GIF", "BMP", "HIF", "ARW"],
    "videos": ["MOV", "MP4", "MPG", "MTS", "LRF", "LRV"],
    "documents": ["XML"],
    "audio": ["WAV", "MP3"],
    "design": ["PSD"],
}

# カラーコード
COLORS = {"red": "31", "green": "32", "yellow": "33", "blue": "34"}


class FileMover:
    """ファイルを日付・拡張子ごとに整理するクラス"""

    def __init__(self, path: str):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"File not found: {path}")

    @classmethod
    def get_file_names(cls, suffix: str, import_dir: str = ".") -> List[str]:
        """指定された拡張子のファイル一覧を取得"""
        import_path = Path(import_dir)
        if not import_path.exists():
            raise FileNotFoundError(f"Import directory not found: {import_dir}")

        return [
            f.name
            for f in import_path.iterdir()
            if f.is_file() and f.name.lower().endswith(f".{suffix.lower()}")
        ]

    @property
    def stat(self) -> datetime:
        """ファイルの更新日時を取得"""
        return datetime.fromtimestamp(self.path.stat().st_mtime)

    @property
    def extension(self) -> str:
        """ファイルの拡張子を取得"""
        return self.path.suffix[1:]  # .を除いた拡張子

    def _get_export_dir(self, base_dir: str = ".") -> Path:
        """エクスポート先ディレクトリパスを生成"""
        stat = self.stat
        ymd = f"{stat.year:04d}-{stat.month:02d}-{stat.day:02d}"

        return (
            Path(base_dir)
            / str(stat.year)
            / f"{stat.month:02d}月"
            / ymd
            / self.extension
        )

    def move(
        self,
        export_dir: str = ".",
        dry_run: bool = False,
        logger: Optional[UnifiedLogger] = None,
    ) -> bool:
        """ファイルを移動"""
        dir_name = self._get_export_dir(export_dir)

        if dry_run:
            color_print(
                f"[DRY RUN] Would move: {self.path} -> {dir_name}", COLORS["yellow"]
            )
            return True

        try:
            # ディレクトリ作成
            dir_name.mkdir(parents=True, exist_ok=True)

            # 移動先のファイルパス
            dest_path = self._get_destination_path(dir_name)

            # ファイル移動
            shutil.move(str(self.path), str(dest_path))
            color_print(f"Moved: {self.path} -> {dest_path}", COLORS["green"])

            if logger:
                logger.info(f"Moved: {self.path} -> {dest_path}")

            return True

        except Exception as e:
            error_msg = f"Error moving {self.path}: {e}"
            color_print(error_msg, COLORS["red"])
            if logger:
                logger.error(error_msg)
            return False

    def _get_destination_path(self, dir_name: Path) -> Path:
        """移動先のファイルパスを決定"""
        dest_path = dir_name / self.path.name

        # 既存ファイルがない場合はそのまま返す
        if not dest_path.exists():
            return dest_path

        # ファイルサイズが同じ場合はスキップ（元のパスを返す）
        if dest_path.stat().st_size == self.path.stat().st_size:
            color_print(f"Skipped (already exists): {self.path.name}", COLORS["yellow"])
            return dest_path

        # サイズが異なる場合はリネーム
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return dir_name / f"{self.path.stem}_{timestamp}{self.path.suffix}"


def color_print(text: str, color: str):
    """カラー出力"""
    print(f"\033[{color}m{text}\033[0m")


def get_suffixes() -> List[str]:
    """サポートされているファイル拡張子の一覧を取得"""
    suffixes = []
    for category in SUPPORTED_EXTENSIONS.values():
        suffixes.extend(category)

    # 大文字小文字両方を追加
    all_suffixes = []
    for suffix in suffixes:
        all_suffixes.extend([suffix.lower(), suffix.upper()])

    return sorted(list(set(all_suffixes)))


def setup_logging(log_file: Optional[str] = None) -> UnifiedLogger:
    """ログ設定"""
    return UnifiedLogger(name="file_mover", log_file=log_file, console=False)


def move_files(
    suffix: str,
    import_dir: str = ".",
    export_dir: str = ".",
    dry_run: bool = False,
    logger: Optional[UnifiedLogger] = None,
) -> tuple:
    """指定した拡張子のファイルを移動"""
    try:
        file_names = FileMover.get_file_names(suffix, import_dir)
        if not file_names:
            return 0, 0  # 成功数, 失敗数

        color_print(
            f"Processing {len(file_names)} files with extension: {suffix}",
            COLORS["blue"],
        )

        success_count = 0
        error_count = 0

        for file_name in file_names:
            success, error = _process_single_file(
                file_name, import_dir, export_dir, dry_run, logger
            )
            success_count += success
            error_count += error

        return success_count, error_count

    except FileNotFoundError as e:
        color_print(f"Directory error: {e}", COLORS["red"])
        if logger:
            logger.error(f"Directory error: {e}")
        return 0, 1


def _process_single_file(
    file_name: str,
    import_dir: str,
    export_dir: str,
    dry_run: bool,
    logger: Optional[UnifiedLogger],
) -> tuple:
    """単一ファイルの処理"""
    try:
        file_path = os.path.join(import_dir, file_name)
        if FileMover(file_path).move(export_dir, dry_run, logger):
            return 1, 0  # 成功, エラー
        else:
            return 0, 1
    except Exception as e:
        color_print(f"Error processing {file_name}: {e}", COLORS["red"])
        if logger:
            logger.error(f"Error processing {file_name}: {e}")
        return 0, 1


@click.command()
@click.option("--import-dir", default=".", help="Import directory")
@click.option("--export-dir", default="export", help="Export directory")
@click.option(
    "--suffix",
    default=None,
    help="File suffix to move (if not specified, all supported extensions will be processed)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without actually moving files",
)
@click.option("--log-file", type=click.Path(), help="Log file path")
@click.option("--verbose", is_flag=True, help="Verbose output")
def main(import_dir, export_dir, suffix, dry_run, log_file, verbose):
    """
    ファイルを日付・拡張子ごとに整理するスクリプト

    ファイルは以下の構造で整理されます:
    export_dir/YYYY/MM月/YYYY-MM-DD/拡張子/ファイル名
    """
    # ログ設定
    logger = setup_logging(log_file) if log_file else None

    # 開始メッセージ
    mode = "DRY RUN" if dry_run else "ACTUAL RUN"
    color_print(f"=== File Organizer ({mode}) ===", COLORS["blue"])
    color_print(f"Import directory: {import_dir}", COLORS["blue"])
    color_print(f"Export directory: {export_dir}", COLORS["blue"])

    if logger:
        logger.start_operation(
            "File Organization", mode=mode, import_dir=import_dir, export_dir=export_dir
        )

    # ディレクトリ存在確認
    if not os.path.exists(import_dir):
        error_msg = f"Import directory not found: {import_dir}"
        color_print(error_msg, COLORS["red"])
        if logger:
            logger.error(error_msg)
        return

    # 拡張子の決定
    suffixes = get_suffixes() if suffix is None else [suffix]

    # 各拡張子について処理
    total_success, total_errors = _process_all_suffixes(
        suffixes, import_dir, export_dir, dry_run, logger, verbose
    )

    # 結果サマリー
    _print_summary(total_success, total_errors, dry_run, logger)


def _process_all_suffixes(
    suffixes: List[str],
    import_dir: str,
    export_dir: str,
    dry_run: bool,
    logger: Optional[UnifiedLogger],
    verbose: bool,
) -> tuple:
    """全ての拡張子について処理を実行"""
    total_success = 0
    total_errors = 0

    for suffix in suffixes:
        if verbose:
            color_print(f"Processing extension: {suffix}", COLORS["blue"])

        success, errors = move_files(suffix, import_dir, export_dir, dry_run, logger)
        total_success += success
        total_errors += errors

    return total_success, total_errors


def _print_summary(
    total_success: int,
    total_errors: int,
    dry_run: bool,
    logger: Optional[UnifiedLogger],
):
    """処理結果のサマリーを表示"""
    color_print(f"\n=== Summary ===", COLORS["blue"])
    color_print(f"Successfully processed: {total_success} files", COLORS["green"])

    if total_errors > 0:
        color_print(f"Errors: {total_errors} files", COLORS["red"])

    if logger:
        logger.end_operation("File Organization", total_success, total_errors)

    if dry_run:
        color_print(
            "Note: This was a dry run. No files were actually moved.", COLORS["yellow"]
        )


if __name__ == "__main__":
    main()


def show_supported_extensions():
    """サポートされている拡張子を表示"""
    print("Supported file extensions:")
    for category, extensions in SUPPORTED_EXTENSIONS.items():
        print(f"  {category.title()}: {', '.join(extensions)}")
    print(f"\nTotal: {len(get_suffixes())} extensions")
