#!/usr/bin/env python3
"""
My Data Backup - 統一アプリケーションのメインエントリーポイント

モジュラー・コンポーネント構造を採用した統一GUI/CLIアプリケーション
"""

import argparse
import sys


def main():
    """メインエントリーポイント"""
    parser = argparse.ArgumentParser(
        description="My Data Backup - RAW/JPGファイル整理ツール統合版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
利用可能なモード:
  gui                 統一GUIアプリケーションを起動
  cli photo           Photo Organizer CLI
  cli move            Move CLI

例:
  python main.py gui                           # 統一GUIを起動
  python main.py cli photo --help              # Photo Organizer CLIのヘルプ
  python main.py cli move --help               # Move CLIのヘルプ
        """,
    )

    subparsers = parser.add_subparsers(dest="mode", help="実行モード")

    # GUI モード
    gui_parser = subparsers.add_parser("gui", help="統一GUIアプリケーションを起動")
    gui_parser.add_argument(
        "--theme", choices=["auto", "light", "dark"], default="auto", help="UIテーマ"
    )

    # CLI モード
    cli_parser = subparsers.add_parser("cli", help="CLIモード")
    cli_subparsers = cli_parser.add_subparsers(dest="tool", help="使用するツール")

    # Photo Organizer CLI
    photo_parser = cli_subparsers.add_parser("photo", help="Photo Organizer CLI")
    photo_parser.add_argument("--src", required=True, help="ソースディレクトリ")
    photo_parser.add_argument("--dir", required=True, help="出力ディレクトリ")
    photo_parser.add_argument("--dry-run", action="store_true", help="ドライランモード")

    # Move CLI
    move_parser = cli_subparsers.add_parser("move", help="Move CLI")
    move_parser.add_argument(
        "--import-dir", required=True, help="インポートディレクトリ"
    )
    move_parser.add_argument(
        "--export-dir", required=True, help="エクスポートディレクトリ"
    )
    move_parser.add_argument("--dry-run", action="store_true", help="ドライランモード")

    args = parser.parse_args()

    if args.mode == "gui":
        launch_gui(args.theme)
    elif args.mode == "cli":
        if args.tool == "photo":
            launch_photo_cli(args)
        elif args.tool == "move":
            launch_move_cli(args)
        else:
            cli_parser.print_help()
    else:
        parser.print_help()


def launch_gui(theme="auto"):
    """統一GUIアプリケーションを起動"""
    try:
        from app.gui.app import UnifiedDataBackupApp

        print("🚀 統一GUIアプリケーションを起動中...")
        app = UnifiedDataBackupApp()
        app.run()

    except ImportError as e:
        print(f"❌ GUIモジュールのインポートに失敗しました: {e}")
        print("📋 必要な依存関係がインストールされているか確認してください:")
        print("   pip install customtkinter")
        sys.exit(1)
    except Exception as e:
        print(f"❌ GUIアプリケーションの起動に失敗しました: {e}")
        sys.exit(1)


def launch_photo_cli(args):
    """Photo Organizer CLIを起動"""
    try:
        from app.cli.photo_organizer import PhotoOrganizerCLI

        cli = PhotoOrganizerCLI()
        cli.run(src=args.src, dir=args.dir, dry_run=args.dry_run)

    except ImportError as e:
        print(f"❌ Photo Organizer CLIモジュールのインポートに失敗しました: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Photo Organizer CLIの実行に失敗しました: {e}")
        sys.exit(1)


def launch_move_cli(args):
    """Move CLIを起動"""
    try:
        from app.cli.move import MoveCLI

        cli = MoveCLI()
        cli.run(
            import_dir=args.import_dir, export_dir=args.export_dir, dry_run=args.dry_run
        )

    except ImportError as e:
        print(f"❌ Move CLIモジュールのインポートに失敗しました: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Move CLIの実行に失敗しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
