#!/usr/bin/env python3
"""
My Data Backup - Typer版のメインエントリーポイント

Typerを使ったモダンCLI実装
"""

from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

# CLI モジュールのインポート
from src.app.cli.move import MoveCLI
from src.app.cli.photo_organizer import PhotoOrganizerCLI

# メインアプリケーション
app = typer.Typer(
    name="my-data-backup",
    help="My Data Backup - RAW/JPGファイル整理ツール統合版",
    rich_markup_mode="markdown",
)

# サブアプリケーション
photo_app = typer.Typer(
    name="photo", help="Photo Organizer CLI - RAW/JPGファイル同期整理"
)
move_app = typer.Typer(name="move", help="Move CLI - ファイル移動・整理")

app.add_typer(photo_app, name="photo")
app.add_typer(move_app, name="move")


@app.command()
def gui(theme: Annotated[str, typer.Option(help="UIテーマ")] = "auto"):
    """統一GUIアプリケーションを起動"""
    try:
        from src.app.gui.app import UnifiedDataBackupApp

        typer.echo("🚀 統一GUIアプリケーションを起動中...")
        app = UnifiedDataBackupApp()
        app.run()

    except ImportError as e:
        typer.echo(f"❌ GUIモジュールのインポートに失敗しました: {e}", err=True)
        typer.echo("📋 必要な依存関係がインストールされているか確認してください:")
        typer.echo("   pip install customtkinter")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ GUIアプリケーションの起動に失敗しました: {e}", err=True)
        raise typer.Exit(1)


@photo_app.command("organize")
def photo_organize(
    src: Annotated[Path, typer.Argument(help="ソースディレクトリ")],
    dir: Annotated[Path, typer.Argument(help="出力ディレクトリ")],
    dry_run: Annotated[bool, typer.Option("--dry-run", help="ドライランモード")] = True,
    copy: Annotated[bool, typer.Option("--copy", help="コピーモード")] = False,
    isolate: Annotated[bool, typer.Option("--isolate", help="分離モード")] = False,
):
    """Photo Organizer - RAW/JPGファイル同期整理"""

    # パス検証
    if not src.exists():
        typer.echo(f"❌ エラー: ソースディレクトリが存在しません: {src}", err=True)
        raise typer.Exit(1)

    # CLI実行
    cli = PhotoOrganizerCLI()
    try:
        cli.run(src=str(src), dir=str(dir), dry_run=dry_run, copy=copy, isolate=isolate)
    except Exception as e:
        typer.echo(f"❌ Photo Organizer CLIの実行に失敗しました: {e}", err=True)
        raise typer.Exit(1)


@move_app.command("organize")
def move_organize(
    src: Annotated[Path, typer.Argument(help="ソースディレクトリ")],
    dest: Annotated[Path, typer.Argument(help="出力ディレクトリ")],
    dry_run: Annotated[bool, typer.Option("--dry-run", help="ドライランモード")] = True,
    copy: Annotated[bool, typer.Option("--copy", help="コピーモード")] = False,
    recursive: Annotated[bool, typer.Option("--recursive", help="再帰検索")] = True,
    extensions: Annotated[
        Optional[str], typer.Option("--extensions", help="対象拡張子 (カンマ区切り)")
    ] = None,
):
    """Move - ファイル移動・整理"""

    # パス検証
    if not src.exists():
        typer.echo(f"❌ エラー: ソースディレクトリが存在しません: {src}", err=True)
        raise typer.Exit(1)

    # 拡張子リスト変換
    ext_list = None
    if extensions:
        ext_list = [ext.strip() for ext in extensions.split(",")]

    # CLI実行
    cli = MoveCLI()
    try:
        # MoveCLIのrun_from_args相当の処理
        # argsオブジェクトを模擬
        class Args:
            def __init__(self):
                # self.src = str(src)
                self.import_dir = str(src)
                # self.dest = str(dest)
                self.export_dir = str(dest)

                self.dry_run = dry_run
                self.copy = copy
                self.recursive = recursive
                # self.extensions = ext_list
                self.suffix = ext_list if ext_list else None

        cli.run_from_args(Args())
    except Exception as e:
        typer.echo(f"❌ Move CLIの実行に失敗しました: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
