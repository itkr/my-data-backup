"""
sort CLI
"""

from pathlib import Path
from typing import Annotated, List, Optional

import typer

from src.app.cli.display import display_result, progress_callback
from src.core.domain.models import OrganizationConfig
from src.core.services import SortService
from src.infrastructure.logging import get_logger
from src.infrastructure.repositories import FileSystemRepository

logger = get_logger("SortCLI")


class SortCLI:
    """sort の CLI 実装"""

    def run(
        self,
        import_dir: str,
        export_dir: str,
        dry_run: bool = False,
        copy: bool = False,
        suffixes: Optional[List[str]] = None,
        recursive: bool = False,
    ):
        """sort のメイン実行"""

        logger.info(f"sort 開始: {import_dir} -> {export_dir}")

        # パス検証
        source_path = Path(import_dir)
        target_path = Path(export_dir)

        if not source_path.exists():
            typer.echo(
                f"エラー: インポートディレクトリが存在しません: {import_dir}",
                err=True,
            )
            raise typer.Exit(code=1)

        # サービス初期化
        file_repository = FileSystemRepository(logger)
        sort_service = SortService(file_repository, logger)

        # ドット付きの拡張子に変換
        file_extensions = [f".{s.lstrip('.')}" for s in suffixes] if suffixes else None

        # 設定作成
        config = OrganizationConfig(
            dry_run=dry_run,
            create_date_dirs=True,
            create_type_dirs=True,
            handle_duplicates=True,
            log_operations=True,
            preserve_original=copy,
            file_extensions=file_extensions,
            recursive=recursive,
        )

        self._display_start_info(
            source_path=source_path,
            target_path=target_path,
            config=config,
        )

        if dry_run:
            typer.echo("ドライランモード - 実際のファイル操作は行いません")

        # 実行
        result = sort_service.sort_by_date(
            source_dir=source_path,
            target_dir=target_path,
            config=config,
            progress_callback=progress_callback,
        )

        # 結果表示
        display_result(result)
        logger.info("sort 完了")

    def _display_start_info(
        self, source_path: Path, target_path: Path, config: OrganizationConfig
    ):
        """実行情報表示"""
        typer.echo("sort - 日付・拡張子で仕分け")
        typer.echo(f"- Import:\t{source_path}")
        typer.echo(f"- Export:\t{target_path}")
        typer.echo(f"- Filter:\t{', '.join(config.file_extensions)}")
        typer.echo(
            f"- Search:\t{'Recursive' if config.recursive else 'Current directory'}"
        )
        typer.echo(f"- Action:\t{'COPY' if config.preserve_original else 'MOVE'}")
        typer.echo(f"-   Mode:\t{'DRY RUN' if config.dry_run else 'EXECUTE'}")
        typer.echo("")


def sort(
    source_dir: Annotated[Path, typer.Argument(help="仕分け元ディレクトリ")],
    target_dir: Annotated[Path, typer.Argument(help="仕分け先ディレクトリ")],
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
    """ファイルを撮影日・拡張子ごとに仕分ける

    Examples:
        # ドライランで確認
        my-data-backup sort /import /export --dry-run

        # 特定拡張子のみ処理
        my-data-backup sort /import /export --suffix jpg --suffix arw
    """
    try:
        SortCLI().run(
            import_dir=str(source_dir),
            export_dir=str(target_dir),
            dry_run=dry_run,
            copy=copy,
            suffixes=suffix,
            recursive=recursive,
        )
    except typer.Exit:
        # 意図した終了は握りつぶさずそのまま伝播させる
        raise
    except Exception as e:
        logger.error(f"sort 実行エラー: {e}")
        typer.echo(f"エラー: {str(e)}", err=True)
        raise typer.Exit(code=1)
