"""
CLI の進捗・結果表示
"""

import typer

from src.core.domain.models import ProcessResult

MAX_LISTED_FILES = 10
MAX_LISTED_ERRORS = 5


def progress_callback(current: int, total: int):
    """進捗表示コールバック"""
    if total > 0:
        typer.echo(f"進捗: {current}/{total} ({current / total * 100:.1f}%)")


def display_result(result: ProcessResult):
    """処理結果を表示"""
    typer.echo("\n実行結果")
    typer.echo(f"  成功:     {result.success_count} ファイル")
    if result.skipped_count:
        typer.echo(f"  スキップ: {result.skipped_count} ファイル（出力先に同名あり）")
    typer.echo(f"  失敗:     {result.error_count} ファイル")
    typer.echo(f"  成功率:   {result.success_rate * 100:.1f}%")

    if result.processed_files:
        typer.echo(f"\n処理済みファイル (最初の{MAX_LISTED_FILES}件):")
        for i, file_info in enumerate(result.processed_files[:MAX_LISTED_FILES], 1):
            typer.echo(f"  {i:2d}. {file_info.name}")

        remaining = len(result.processed_files) - MAX_LISTED_FILES
        if remaining > 0:
            typer.echo(f"  ... 他 {remaining} ファイル")

    if result.errors:
        typer.echo("\nエラー:")
        for error in result.errors[:MAX_LISTED_ERRORS]:
            typer.echo(f"  • {error}")
