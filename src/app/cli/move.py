"""
Move CLI - 新アーキテクチャ版
"""

import click
from pathlib import Path
import sys
from typing import Optional

# パッケージインストール後は動的パス追加不要
from src.core.services import MoveService
from src.core.domain.models import OrganizationConfig
from src.infrastructure.repositories import FileSystemRepository
from src.infrastructure.logging import get_logger


class MoveCLI:
    """Move CLI実装"""

    def __init__(self):
        self.logger = get_logger("MoveCLI")

    def run(
        self,
        import_dir: str,
        export_dir: str,
        dry_run: bool = True,
        suffix: Optional[str] = None,
    ):
        """Move CLIメイン実行"""

        try:
            # パス検証
            source_path = Path(import_dir)
            target_path = Path(export_dir)

            if not source_path.exists():
                click.echo(
                    f"❌ エラー: インポートディレクトリが存在しません: {import_dir}",
                    err=True,
                )
                sys.exit(1)

            # サービス初期化
            file_repository = FileSystemRepository(self.logger.logger)
            move_service = MoveService(file_repository, self.logger.logger)

            # 設定作成
            config = OrganizationConfig(
                dry_run=dry_run,
                create_date_dirs=True,
                create_type_dirs=True,
                handle_duplicates=True,
                log_operations=True,
                preserve_original=False,
            )

            # 実行情報表示
            click.echo("📁 Move CLI - 日付ベースファイル整理")
            click.echo("=" * 50)
            click.echo(f"インポート: {source_path}")
            click.echo(f"エクスポート: {target_path}")
            click.echo(f"モード: {'ドライラン' if dry_run else '実行'}")
            if suffix:
                click.echo(f"フィルタ: *.{suffix}")
            click.echo("=" * 50)

            if dry_run:
                click.echo("🧪 ドライランモード - 実際のファイル操作は行いません")

            # 実行
            result = move_service.organize_by_date(
                source_dir=source_path,
                target_dir=target_path,
                config=config,
                progress_callback=self._progress_callback,
            )

            # 結果表示
            self._display_result(result)

        except Exception as e:
            self.logger.error(f"Move CLI実行エラー: {e}")
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
@click.option(
    "--import-dir",
    required=True,
    type=click.Path(exists=True),
    help="インポートディレクトリ",
)
@click.option(
    "--export-dir", required=True, type=click.Path(), help="エクスポートディレクトリ"
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=True,
    help="ドライランモード（実際の操作を行わない）",
)
@click.option("--suffix", type=str, help="特定の拡張子のファイルのみ処理")
@click.option(
    "--execute", is_flag=True, default=False, help="実際に実行（ドライランを無効化）"
)
@click.option("--verbose", is_flag=True, default=False, help="詳細ログを表示")
def main(
    import_dir: str,
    export_dir: str,
    dry_run: bool,
    suffix: Optional[str],
    execute: bool,
    verbose: bool,
):
    """
    Move CLI - 日付ベースファイル整理

    ファイルを日付・拡張子ごとのディレクトリ構造に整理します
    """

    # --execute オプションがある場合はドライランを無効化
    if execute:
        dry_run = False

    cli = MoveCLI()
    cli.run(
        import_dir=import_dir, export_dir=export_dir, dry_run=dry_run, suffix=suffix
    )


if __name__ == "__main__":
    main()
