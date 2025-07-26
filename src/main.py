#!/usr/bin/env python3
"""
My Data Backup - 統一アプリケーションのメインエントリーポイント

モジュラー・コンポーネント構造を採用した統一GUI/CLIアプリケーション
オプション定義は各CLIモジュールから自動取得して重複を排除
"""

import argparse
import sys
from typing import Dict, Type

from src.app.cli.base import BaseCLI


def get_available_cli_modules() -> Dict[str, Type[BaseCLI]]:
    """利用可能なCLIモジュールを取得"""
    try:
        from src.app.cli.move import MoveCLI
        from src.app.cli.photo_organizer import PhotoOrganizerCLI

        return {
            PhotoOrganizerCLI.get_command_name(): PhotoOrganizerCLI,
            MoveCLI.get_command_name(): MoveCLI,
        }
    except ImportError as e:
        print(f"❌ CLIモジュールのインポートに失敗しました: {e}")
        return {}


def setup_cli_parsers(cli_subparsers, cli_modules: Dict[str, Type[BaseCLI]]):
    """CLIサブパーサーを自動設定"""
    for command_name, cli_class in cli_modules.items():
        # サブパーサー作成
        cli_parser = cli_subparsers.add_parser(
            command_name, help=cli_class.get_description()
        )

        # 引数仕様を取得して自動設定
        arg_spec = cli_class.get_argument_spec()
        for arg_name, arg_config in arg_spec.items():
            arg_flags = [f"--{arg_name.replace('_', '-')}"]
            cli_parser.add_argument(*arg_flags, **arg_config)


def main():
    """メインエントリーポイント"""
    # 利用可能なCLIモジュールを取得
    cli_modules = get_available_cli_modules()

    parser = argparse.ArgumentParser(
        description="My Data Backup - RAW/JPGファイル整理ツール統合版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
利用可能なモード:
  gui                 統一GUIアプリケーションを起動
  {' '.join([f'cli {name}' for name in cli_modules.keys()])}

例:
  python main.py gui                           # 統一GUIを起動
  {chr(10).join([f'  python main.py cli {name} --help              # {cls.get_description()}のヘルプ' for name, cls in cli_modules.items()])}
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

    # CLIサブコマンドを自動設定
    setup_cli_parsers(cli_subparsers, cli_modules)

    args = parser.parse_args()

    if args.mode == "gui":
        launch_gui(args.theme)
    elif args.mode == "cli":
        if args.tool in cli_modules:
            launch_cli(cli_modules[args.tool], args)
        else:
            cli_parser.print_help()
    else:
        parser.print_help()


def launch_gui(theme="auto"):
    """統一GUIアプリケーションを起動"""
    try:
        from src.app.gui.app import UnifiedDataBackupApp

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


def launch_cli(cli_class: Type[BaseCLI], args):
    """汎用CLI起動関数"""
    try:
        cli = cli_class()
        cli.run_from_args(args)

    except ImportError as e:
        print(
            f"❌ {cli_class.get_command_name()} CLIモジュールのインポートに失敗しました: {e}"
        )
        sys.exit(1)
    except Exception as e:
        print(f"❌ {cli_class.get_command_name()} CLIの実行に失敗しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
