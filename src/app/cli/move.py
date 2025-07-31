"""
Move CLI - Typer統合版
"""

from pathlib import Path
from typing import Annotated, List, Optional

import typer

from src.core.domain.models import OrganizationConfig
from src.core.services import MoveService
from src.infrastructure.logging import get_logger
from src.infrastructure.repositories import FileSystemRepository

logger = get_logger("MoveCLI")


class MoveCLI:
    """Move CLI実装"""

    def run(
        self,
        import_dir: str,
        export_dir: str,
        dry_run: bool = True,
        suffixes: Optional[List[str]] = None,
        recursive: bool = True,
    ):
        """Move CLIメイン実行"""

        try:
            logger.info(f"Move開始: {import_dir} -> {export_dir}")
            # パス検証
            source_path = Path(import_dir)
            target_path = Path(export_dir)

            if not source_path.exists():
                typer.echo(
                    f"❌ エラー: インポートディレクトリが存在しません: {import_dir}",
                    err=True,
                )
                typer.Exit(code=1)

            # サービス初期化
            file_repository = FileSystemRepository(logger.logger)
            move_service = MoveService(file_repository, logger.logger)

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
                recursive=recursive,
            )

            # 実行情報表示
            typer.echo("📁 Move CLI - 日付ベースファイル整理")
            typer.echo("=" * 50)
            typer.echo(f"インポート: {source_path}")
            typer.echo(f"エクスポート: {target_path}")
            typer.echo(f"モード: {'ドライラン' if dry_run else '実行'}")
            typer.echo(f"検索: {'再帰的' if recursive else 'カレントディレクトリのみ'}")
            if suffixes:
                typer.echo(f"フィルタ: {', '.join(f'*.{s}' for s in suffixes)}")
            else:
                typer.echo("フィルタ: デフォルト拡張子 (jpg, arw, mov, mp4, etc.)")
            typer.echo("=" * 50)

            if dry_run:
                typer.echo("🧪 ドライランモード - 実際のファイル操作は行いません")

            # 実行
            result = move_service.organize_by_date(
                source_dir=source_path,
                target_dir=target_path,
                config=config,
                progress_callback=self._progress_callback,
            )

            # 結果表示
            self._display_result(result)
            logger.info("Move完了")

        except Exception as e:
            logger.error(f"Move CLI実行エラー: {e}")
            typer.echo(f"❌ エラー: {str(e)}", err=True)
            typer.Exit(code=1)

    def _progress_callback(self, current: int, total: int):
        """進捗表示コールバック"""
        if total > 0:
            progress = current / total * 100
            typer.echo(f"進捗: {current}/{total} ({progress:.1f}%)")

    def _display_result(self, result):
        """結果表示"""
        typer.echo("\n📊 実行結果")
        typer.echo("=" * 30)
        typer.echo(f"✅ 成功: {result.success_count} ファイル")
        typer.echo(f"❌ 失敗: {result.error_count} ファイル")
        typer.echo(f"📈 成功率: {result.success_rate * 100:.1f}%")

        if result.processed_files:
            typer.echo("\n処理済みファイル (最初の10件):")
            for i, file_info in enumerate(result.processed_files[:10]):
                typer.echo(f"  {i + 1:2d}. {file_info.name}")

            if len(result.processed_files) > 10:
                typer.echo(f"  ... 他 {len(result.processed_files) - 10} ファイル")

        if result.errors:
            typer.echo("\nエラー:")
            for error in result.errors[:5]:
                typer.echo(f"  • {error}")


# サブアプリケーション
app = typer.Typer(
    name="move", help="Move CLI - ファイル移動・整理", rich_markup_mode="markdown"
)


@app.command("organize")
def organize(
    import_dir: Annotated[Path, typer.Argument(help="インポートディレクトリ")],
    export_dir: Annotated[Path, typer.Argument(help="エクスポートディレクトリ")],
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="ドライランモード")
    ] = False,
    copy: Annotated[bool, typer.Option("--copy", help="コピーモード")] = False,
    recursive: Annotated[bool, typer.Option("--recursive", help="再帰検索")] = True,
    suffix: Annotated[
        Optional[list[str]],
        typer.Option(
            "--suffix", help="対象拡張子 (複数指定可能: --suffix jpg --suffix arw)"
        ),
    ] = None,
):
    """Move - ファイル移動・整理

    日付ベースでファイルを整理します。

    Examples:
        # ドライランで確認
        python -m src.app.cli.move_typer organize /import /export --dry-run

        # 特定拡張子のみ処理
        python -m src.app.cli.move_typer organize /import /export \\
            --suffix jpg --suffix arw
    """

    # CLI実行
    cli = MoveCLI()
    cli.run(
        import_dir=str(import_dir),
        export_dir=str(export_dir),
        dry_run=dry_run,
        suffixes=suffix,
        recursive=recursive,
    )


if __name__ == "__main__":
    app()
