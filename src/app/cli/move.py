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
        dry_run: bool = False,
        suffixes: Optional[List[str]] = None,
        recursive: bool = False,
    ):
        """Move CLIメイン実行"""

        logger.info(f"Move開始: {import_dir} -> {export_dir}")

        # パス検証
        source_path = Path(import_dir)
        target_path = Path(export_dir)

        if not source_path.exists():
            typer.echo(
                f"❌ エラー: インポートディレクトリが存在しません: {import_dir}",
                err=True,
            )
            raise typer.Exit(code=1)

        # サービス初期化
        file_repository = FileSystemRepository(logger.logger)
        move_service = MoveService(file_repository, logger.logger)

        # ドット付きの拡張子に変換
        file_extensions = [f".{s.lstrip('.')}" for s in suffixes] if suffixes else None

        # 設定作成
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

        self._display_start_info(
            source_path=source_path,
            target_path=target_path,
            config=config,
        )

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

    def _progress_callback(self, current: int, total: int):
        """進捗表示コールバック"""
        if total > 0:
            progress = current / total * 100
            typer.echo(f"進捗: {current}/{total} ({progress:.1f}%)")

    def _display_start_info(
        self, source_path: Path, target_path: Path, config: OrganizationConfig
    ):
        """実行情報表示"""
        typer.echo("📁 Move CLI - 日付ベースファイル整理")
        typer.echo(f"- Import:\t{source_path}")
        typer.echo(f"- Export:\t{target_path}")
        typer.echo(f"- Filter:\t{', '.join(config.file_extensions)}")
        typer.echo(
            f"- Search:\t{'Recursive' if config.recursive else 'Current directory'}"
        )
        typer.echo(f"-   Mode:\t{'DRY RUN' if config.dry_run else 'EXECUTE'}")
        typer.echo("")

    def _display_result(self, result):
        """結果表示"""
        typer.echo("\n📊 実行結果")
        typer.echo(f"✅   成功:\t{result.success_count} ファイル")
        typer.echo(f"❌   失敗:\t{result.error_count} ファイル")
        typer.echo(f"📈 成功率:\t{result.success_rate * 100:.1f}%")

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
    name="move",
    help="Move CLI - ファイル移動・整理",
    rich_markup_mode="markdown",
)


@app.command("organize")
def organize(
    import_dir: Annotated[Path, typer.Argument(help="インポートディレクトリ")],
    export_dir: Annotated[Path, typer.Argument(help="エクスポートディレクトリ")],
    dry_run: Annotated[bool, typer.Option("--dry-run", help="ドライラン")] = False,
    copy: Annotated[bool, typer.Option("--copy", help="コピーモード")] = False,
    recursive: Annotated[bool, typer.Option("--recursive", help="再帰検索")] = False,
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

    try:
        cli = MoveCLI()
        cli.run(
            import_dir=str(import_dir),
            export_dir=str(export_dir),
            dry_run=dry_run,
            suffixes=suffix,
            recursive=recursive,
        )
    except typer.Exit:
        # 意図した終了は握りつぶさずそのまま伝播させる
        raise
    except Exception as e:
        logger.error(f"Move CLI実行エラー: {e}")
        typer.echo(f"❌ エラー: {str(e)}", err=True)
        raise typer.Exit(code=1)


# 対象の拡張子を取得するサブコマンド
@app.command("get-suffixes")
def get_suffixes(
    suffix: Annotated[
        Optional[list[str]],
        typer.Option(
            "--suffix", help="対象拡張子 (複数指定可能: --suffix jpg --suffix arw)"
        ),
    ] = None,
):
    """Move - 対象拡張子を取得

    対象の拡張子を表示します。
    """
    config: OrganizationConfig = OrganizationConfig(file_extensions=suffix or None)
    typer.echo("対象の拡張子:")
    typer.echo(", ".join(config.file_extensions))


if __name__ == "__main__":
    app()
