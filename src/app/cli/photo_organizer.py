"""
Photo Organizer CLI - Typer統合版
"""

from pathlib import Path
from typing import Annotated

import typer

from src.core.domain.models import OrganizationConfig
from src.core.services import PhotoOrganizerService
from src.infrastructure.logging import get_logger
from src.infrastructure.repositories import FileSystemRepository

logger = get_logger("PhotoOrganizerCLI")


class PhotoOrganizerCLI:
    """Photo Organizer CLI実装"""

    def run(
        self,
        src: str,
        dir: str,
        dry_run: bool = False,
        copy: bool = False,
        isolate: bool = False,
    ):
        """Photo Organizer CLIメイン実行"""

        logger.info(f"Photo Organizer開始: {src} -> {dir}")
        # パス検証
        source_path = Path(src)
        target_path = Path(dir)

        if not source_path.exists():
            typer.echo(f"❌ エラー: ソースディレクトリが存在しません: {src}", err=True)
            raise typer.Exit(code=1)

        # サービス初期化
        file_repository = FileSystemRepository(logger.logger)
        photo_service = PhotoOrganizerService(file_repository, logger.logger)

        # 設定作成
        config = OrganizationConfig(
            dry_run=dry_run, preserve_original=copy, log_operations=True
        )

        # 実行情報表示
        typer.echo("📸 Photo Organizer CLI")
        typer.echo("=" * 50)
        typer.echo(f"ソース: {source_path}")
        typer.echo(f"出力先: {target_path}")
        typer.echo(f"モード: {'ドライラン' if dry_run else '実行'}")
        typer.echo(f"操作: {'コピー' if copy else '移動'}")
        typer.echo("=" * 50)

        if dry_run:
            typer.echo("🧪 ドライランモード - 実際のファイル操作は行いません")

        # 実行
        result = photo_service.organize_photos(
            source_dir=source_path,
            target_dir=target_path,
            config=config,
            progress_callback=self._progress_callback,
        )

        # 結果表示
        self._display_result(result)
        logger.info("Photo Organizer完了")

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
    name="photo",
    help="Photo Organizer CLI - RAW/JPGファイル同期整理",
    rich_markup_mode="markdown",
)


@app.command("organize")
def organize(
    src: Annotated[Path, typer.Argument(help="ソースディレクトリ")],
    dir: Annotated[Path, typer.Argument(help="出力ディレクトリ")],
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="ドライランモード")
    ] = False,
    copy: Annotated[bool, typer.Option("--copy", help="コピーモード")] = False,
    isolate: Annotated[bool, typer.Option("--isolate", help="分離モード")] = False,
):
    """Photo Organizer - RAW/JPGファイル同期整理

    RAWとJPGファイルの同期処理を行います。

    Examples:
        # ドライランで確認
        python -m src.app.cli.photo_organizer_typer organize /source /dest --dry-run

        # 実際に実行
        python -m src.app.cli.photo_organizer_typer organize /source /dest --no-dry-run
    """

    # CLI実行
    try:
        cli = PhotoOrganizerCLI()
        cli.run(src=str(src), dir=str(dir), dry_run=dry_run, copy=copy, isolate=isolate)
    except typer.Exit:
        # 意図した終了は握りつぶさずそのまま伝播させる
        raise
    except Exception as e:
        logger.error(f"Photo Organizer CLI実行エラー: {e}")
        typer.echo(f"❌ エラー: {str(e)}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
