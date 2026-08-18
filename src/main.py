#!/usr/bin/env python3
"""
My Data Backup - Typer版のメインエントリーポイント（改良版）

統一されたTyper CLI実装 - 二重管理解消版
"""

import typer

from src.app.cli.move import app as move_app
from src.app.cli.photo_organizer import app as photo_app
from src.infrastructure.logging import get_logger

# メインアプリケーション
app = typer.Typer(
    name="my-data-backup",
    help="My Data Backup - RAW/JPGファイル整理ツール統合版",
    rich_markup_mode="markdown",
)

# サブアプリケーション登録
app.add_typer(photo_app, name="photo")
app.add_typer(move_app, name="move")

logger = get_logger("MainApp")


@app.command()
def gui(theme: str = "auto"):
    """統一GUIアプリケーションを起動

    Args:
        theme: UIテーマ (auto, light, dark)
    """
    try:
        from src.app.gui.app import UnifiedDataBackupApp

        logger.info("統一GUIアプリケーション起動開始")
        typer.echo("統一GUIアプリケーションを起動中...")
        app = UnifiedDataBackupApp()
        app.run()

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
