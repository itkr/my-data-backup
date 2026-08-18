"""
対象拡張子の一覧表示
"""

from typing import Annotated, Optional

import typer

from src.core.domain.models import OrganizationConfig


def extensions(
    suffix: Annotated[
        Optional[list[str]],
        typer.Option(
            "--suffix", help="対象拡張子 (複数指定可能: --suffix jpg --suffix arw)"
        ),
    ] = None,
):
    """処理対象になる拡張子を表示する

    --suffix を指定しない場合は既定の対象拡張子をすべて表示します。
    """
    config = OrganizationConfig(file_extensions=suffix or None)
    typer.echo("対象の拡張子:")
    typer.echo(", ".join(config.file_extensions))
