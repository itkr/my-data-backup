"""
Move CLI - 新アーキテクチャ版
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from src.app.cli.base import BaseCLI
from src.core.domain.models import OrganizationConfig
from src.core.services import MoveService
from src.infrastructure.logging import get_logger
from src.infrastructure.repositories import FileSystemRepository


class MoveCLI(BaseCLI):
    """Move CLI実装"""

    def __init__(self):
        self.logger = get_logger("MoveCLI")

    @classmethod
    def get_command_name(cls) -> str:
        """コマンド名を返す"""
        return "move"

    @classmethod
    def get_description(cls) -> str:
        """コマンドの説明を返す"""
        return "Move CLI - 日付ベースファイル整理"

    @classmethod
    def get_argument_spec(cls) -> Dict[str, Any]:
        """argparse用の引数仕様を返す"""
        return {
            "import_dir": {"required": True, "help": "インポートディレクトリ"},
            "export_dir": {"required": True, "help": "エクスポートディレクトリ"},
            "dry_run": {"action": "store_true", "help": "ドライランモード"},
            "suffix": {
                "action": "append",
                "help": "処理対象の拡張子 (複数指定可能: --suffix jpg --suffix arw)",
            },
            "no_recursive": {
                "action": "store_true",
                "help": "再帰検索を無効化（現在のディレクトリのみ検索）",
            },
        }

    def run_from_args(self, args) -> None:
        """argparseで解析された引数から実行"""
        self.run(
            import_dir=args.import_dir,
            export_dir=args.export_dir,
            dry_run=args.dry_run,
            suffixes=args.suffix or [],
            no_recursive=getattr(args, "no_recursive", False),
        )

    def run(
        self,
        import_dir: str,
        export_dir: str,
        dry_run: bool = True,
        suffixes: Optional[List[str]] = None,
        no_recursive: bool = False,
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
            file_extensions = None
            if suffixes:
                # ドット付きの拡張子に変換
                file_extensions = [f".{s.lstrip('.')}" for s in suffixes]

            config = OrganizationConfig(
                dry_run=dry_run,
                create_date_dirs=True,
                create_type_dirs=True,
                handle_duplicates=True,
                log_operations=True,
                preserve_original=False,
                file_extensions=file_extensions,
                recursive=not no_recursive,
            )

            # 実行情報表示
            click.echo("📁 Move CLI - 日付ベースファイル整理")
            click.echo("=" * 50)
            click.echo(f"インポート: {source_path}")
            click.echo(f"エクスポート: {target_path}")
            click.echo(f"モード: {'ドライラン' if dry_run else '実行'}")
            click.echo(
                f"検索: {'再帰的' if not no_recursive else 'カレントディレクトリのみ'}"
            )
            if suffixes:
                click.echo(f"フィルタ: {', '.join(f'*.{s}' for s in suffixes)}")
            else:
                click.echo("フィルタ: デフォルト拡張子 (jpg, arw, mov, mp4, etc.)")
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
        click.echo(f"📈 成功率: {result.success_rate * 100:.1f}%")

        if result.processed_files:
            click.echo("\n処理済みファイル (最初の10件):")
            for i, file_info in enumerate(result.processed_files[:10]):
                click.echo(f"  {i + 1:2d}. {file_info.name}")

            if len(result.processed_files) > 10:
                click.echo(f"  ... 他 {len(result.processed_files) - 10} ファイル")

        if result.errors:
            click.echo("\nエラー:")
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
    "--export-dir",
    required=True,
    type=click.Path(),
    help="エクスポートディレクトリ",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=True,
    help="ドライランモード（実際の操作を行わない）",
)
@click.option(
    "--suffix",
    "suffixes",
    multiple=True,
    type=str,
    help="処理対象の拡張子 (複数指定可能: --suffix jpg --suffix arw)",
)
@click.option(
    "--no-recursive",
    is_flag=True,
    default=False,
    help="再帰検索を無効化（現在のディレクトリのみ検索）",
)
def main(
    import_dir: str, export_dir: str, dry_run: bool, suffixes: tuple, no_recursive: bool
):
    """
    Move CLI - 日付ベースファイル整理

    ファイルを日付・拡張子ごとのディレクトリ構造に整理します
    """

    cli = MoveCLI()
    cli.run(
        import_dir=import_dir,
        export_dir=export_dir,
        dry_run=dry_run,
        suffixes=list(suffixes),
        no_recursive=no_recursive,
    )


if __name__ == "__main__":
    main()
