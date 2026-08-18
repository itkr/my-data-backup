#!/usr/bin/env python3
"""
My Data Backup - エントリーポイント
"""

import typer

from src.app.cli.extensions import extensions
from src.app.cli.sort import sort
from src.app.cli.sync import sync
from src.infrastructure.logging import get_logger

app = typer.Typer(
    name="my-data-backup",
    help="My Data Backup - RAW/JPGファイル整理ツール",
    rich_markup_mode="markdown",
)

app.command()(sort)
app.command()(sync)
app.command()(extensions)

logger = get_logger("MainApp")


@app.command()
def gui(theme: str = "auto"):
    """統合GUIアプリケーションを起動

    Args:
        theme: UIテーマ (auto, light, dark)
    """
    try:
        from src.app.gui.app import UnifiedDataBackupApp

        logger.info("統合GUIアプリケーション起動開始")
        typer.echo("統合GUIアプリケーションを起動中...")
        UnifiedDataBackupApp().run()

    except ImportError as e:
        logger.error(f"GUIモジュールのインポートに失敗: {e}")
        typer.echo(f"GUIモジュールのインポートに失敗しました: {e}", err=True)
        typer.echo("必要な依存関係がインストールされているか確認してください:")
        typer.echo("   pip install customtkinter")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"GUIアプリケーションの起動に失敗: {e}")
        typer.echo(f"GUIアプリケーションの起動に失敗しました: {e}", err=True)
        raise typer.Exit(1)


def main():
    """コンソールスクリプト（my-data-backup）のエントリーポイント"""
    app()


if __name__ == "__main__":
    main()
