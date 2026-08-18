"""
sync CLI
"""

from pathlib import Path
from typing import Annotated

import typer

from src.app.cli.display import display_result, progress_callback
from src.core.domain.models import OrganizationConfig
from src.core.services import SyncService
from src.infrastructure.logging import get_logger
from src.infrastructure.repositories import FileSystemRepository

logger = get_logger("SyncCLI")


class SyncCLI:
    """sync の CLI 実装"""

    def run(
        self,
        src: str,
        dir: str,
        dry_run: bool = False,
        copy: bool = False,
    ):
        """sync のメイン実行"""

        logger.info(f"sync 開始: {src} -> {dir}")
        # パス検証
        source_path = Path(src)
        target_path = Path(dir)

        if not source_path.exists():
            typer.echo(f"エラー: ソースディレクトリが存在しません: {src}", err=True)
            raise typer.Exit(code=1)

        # サービス初期化
        file_repository = FileSystemRepository(logger)
        photo_service = SyncService(file_repository, logger)

        # 設定作成
        config = OrganizationConfig(
            dry_run=dry_run, preserve_original=copy, log_operations=True
        )

        # 実行情報表示
        typer.echo("sync - RAW/JPG 突き合わせ")
        typer.echo("=" * 50)
        typer.echo(f"ソース: {source_path}")
        typer.echo(f"出力先: {target_path}")
        typer.echo(f"モード: {'ドライラン' if dry_run else '実行'}")
        typer.echo(f"操作: {'コピー' if copy else '移動'}")
        typer.echo("=" * 50)

        if dry_run:
            typer.echo("ドライランモード - 実際のファイル操作は行いません")

        # 実行
        result = photo_service.sync_photos(
            source_dir=source_path,
            target_dir=target_path,
            config=config,
            progress_callback=progress_callback,
        )

        # 結果表示
        display_result(result)
        logger.info("sync 完了")


def sync(
    source_dir: Annotated[Path, typer.Argument(help="ソースディレクトリ")],
    target_dir: Annotated[Path, typer.Argument(help="出力ディレクトリ")],
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="ドライランモード")
    ] = False,
    copy: Annotated[bool, typer.Option("--copy", help="コピーモード")] = False,
):
    """RAW と JPG を突き合わせて振り分ける

    同名の RAW/JPG をペアとして ARW/ と JPG/ に分け、
    対応相手のないファイルは orphans/ に隔離します。
    JPG を手動で取捨選択したあとに実行すると、RAW をその選択に追従させられます。

    Examples:
        # ドライランで確認
        my-data-backup sync /source /dest --dry-run

        # 原本を残してコピー
        my-data-backup sync /source /dest --copy
    """
    try:
        SyncCLI().run(
            src=str(source_dir), dir=str(target_dir), dry_run=dry_run, copy=copy
        )
    except typer.Exit:
        # 意図した終了は握りつぶさずそのまま伝播させる
        raise
    except Exception as e:
        logger.error(f"sync 実行エラー: {e}")
        typer.echo(f"エラー: {str(e)}", err=True)
        raise typer.Exit(code=1)
