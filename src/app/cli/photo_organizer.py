"""
Photo Organizer CLI - 新アーキテクチャ版
"""

import click
from pathlib import Path
import sys
from typing import Optional

# プロジェクトルートをPythonパスに追加
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.services import PhotoOrganizerService
from src.core.domain.models import OrganizationConfig
from src.infrastructure.repositories import FileSystemRepository
from src.infrastructure.logging import get_logger


class PhotoOrganizerCLI:
    """Photo Organizer CLI実装"""

    def __init__(self):
        self.logger = get_logger("PhotoOrganizerCLI")

    def run(
        self,
        src: str,
        dir: str,
        dry_run: bool = True,
        copy: bool = False,
        isolate: bool = False,
    ):
        """Photo Organizer CLIメイン実行"""

        try:
            # パス検証
            source_path = Path(src)
            target_path = Path(dir)

            if not source_path.exists():
                click.echo(
                    f"❌ エラー: ソースディレクトリが存在しません: {src}", err=True
                )
                sys.exit(1)

            # サービス初期化
            file_repository = FileSystemRepository(self.logger.logger)
            photo_service = PhotoOrganizerService(file_repository, self.logger.logger)

            # 設定作成
            config = OrganizationConfig(
                dry_run=dry_run, preserve_original=copy, log_operations=True
            )

            # 実行情報表示
            click.echo("📸 Photo Organizer CLI")
            click.echo("=" * 50)
            click.echo(f"ソース: {source_path}")
            click.echo(f"出力先: {target_path}")
            click.echo(f"モード: {'ドライラン' if dry_run else '実行'}")
            click.echo(f"操作: {'コピー' if copy else '移動'}")
            click.echo("=" * 50)

            if dry_run:
                click.echo("🧪 ドライランモード - 実際のファイル操作は行いません")

            # 実行
            result = photo_service.organize_photos(
                source_dir=source_path,
                target_dir=target_path,
                config=config,
                progress_callback=self._progress_callback,
            )

            # 結果表示
            self._display_result(result)

        except Exception as e:
            self.logger.error(f"Photo Organizer CLI実行エラー: {e}")
            click.echo(f"❌ エラー: {str(e)}", err=True)
            sys.exit(1)

    def _progress_callback(self, current: int, total: int):
        """進捗表示コールバック"""
        if total > 0:
            progress = current / total * 100
            click.echo(f"進捗: {current}/{total} ({progress:.1f}%)")

    def _display_result(self, result):
        """結果表示"""
        click.echo("\n📊 実行結果")
        click.echo("=" * 30)
        click.echo(f"✅ 成功: {result.success_count} ファイル")
        click.echo(f"❌ 失敗: {result.error_count} ファイル")
        click.echo(f"📈 成功率: {result.success_rate*100:.1f}%")

        if result.processed_files:
            click.echo(f"\n処理済みファイル (最初の10件):")
            for i, file_info in enumerate(result.processed_files[:10]):
                click.echo(f"  {i+1:2d}. {file_info.name}")

            if len(result.processed_files) > 10:
                click.echo(f"  ... 他 {len(result.processed_files) - 10} ファイル")

        if result.errors:
            click.echo(f"\nエラー:")
            for error in result.errors[:5]:
                click.echo(f"  • {error}")


@click.command()
@click.argument("src", type=click.Path(exists=True))
@click.argument("dir", type=click.Path())
@click.option(
    "--dry-run",
    is_flag=True,
    default=True,
    help="ドライランモード（実際の操作を行わない）",
)
@click.option(
    "--copy", is_flag=True, default=False, help="ファイルをコピー（移動ではなく）"
)
@click.option("--isolate", is_flag=True, default=False, help="孤立ファイルを分離")
@click.option(
    "--execute", is_flag=True, default=False, help="実際に実行（ドライランを無効化）"
)
def main(src: str, dir: str, dry_run: bool, copy: bool, isolate: bool, execute: bool):
    """
    Photo Organizer CLI - RAW/JPGファイル同期整理

    SRC: ソースディレクトリ
    DIR: 出力ディレクトリ
    """

    # --execute オプションがある場合はドライランを無効化
    if execute:
        dry_run = False

    cli = PhotoOrganizerCLI()
    cli.run(src=src, dir=dir, dry_run=dry_run, copy=copy, isolate=isolate)


if __name__ == "__main__":
    main()
