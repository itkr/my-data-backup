"""
ConfigManagerのテスト
"""

import tempfile
from pathlib import Path

from src.core.config.config_manager import ConfigManager


def test_basic_functionality():
    """基本機能のテスト"""
    print("🧪 基本機能テスト開始")

    # 一時ディレクトリでテスト
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / "test_config"
        manager = ConfigManager(config_dir)

        # 設定変更のテスト
        print("⚙️ 設定変更テスト...")
        manager.update_ui_settings(theme="dark", window_width=1400)
        manager.update_move_settings(default_dry_run=False)
        manager.update_photo_settings(default_preserve=True)

        # ディレクトリ履歴のテスト
        print("📂 ディレクトリ履歴テスト...")
        test_dir = Path(temp_dir) / "test_directory"
        test_dir.mkdir()

        manager.update_recent_directory(str(test_dir))
        recent = manager.get_recent_directories()

        assert str(test_dir) in recent, "ディレクトリ履歴の追加に失敗"

        # 設定保存・読み込みのテスト
        print("💾 保存・読み込みテスト...")
        assert manager.save_config(), "設定保存に失敗"

        # 新しいマネージャーで読み込み
        manager2 = ConfigManager(config_dir)
        assert manager2.config.ui.theme == "dark", "設定読み込みに失敗"
        assert manager2.config.ui.window_width == 1400, "UI設定読み込みに失敗"
        assert not manager2.config.move.default_dry_run, "Move設定読み込みに失敗"
        assert manager2.config.photo.default_preserve, "Photo設定読み込みに失敗"

        print("✅ 基本機能テスト完了")


def test_validation_functionality():
    """検証機能のテスト"""
    print("🧪 検証機能テスト開始")

    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / "test_validation"
        manager = ConfigManager(config_dir)

        # 無効な設定を追加
        manager.config.ui.window_width = 500  # 最小値以下
        manager.config.ui.theme = "invalid_theme"  # 無効なテーマ
        manager.config.photo.last_source_dir = "/nonexistent/path"  # 存在しないパス

        # 検証実行
        errors = manager.validate_config()
        print(f"⚠️ 検出されたエラー: {len(errors)} 件")

        assert len(errors) > 0, "検証でエラーが検出されませんでした"

        # 自動修正実行
        fixed = manager.auto_fix_config()
        assert fixed, "自動修正が実行されませんでした"

        # 修正後の検証
        errors_after = manager.validate_config()
        print(f"🔧 修正後のエラー: {len(errors_after)} 件")

        assert manager.config.ui.window_width >= 800, "ウィンドウ幅の修正に失敗"
        assert manager.config.ui.theme == "auto", "テーマの修正に失敗"
        assert manager.config.photo.last_source_dir == "", "パスの修正に失敗"

        print("✅ 検証機能テスト完了")


def test_import_export():
    """インポート・エクスポート機能のテスト"""
    print("🧪 インポート・エクスポート機能テスト開始")

    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / "test_import_export"
        manager = ConfigManager(config_dir)

        # 設定を変更
        manager.update_ui_settings(theme="light", window_width=1600)
        manager.update_move_settings(default_date_dirs=False)

        # エクスポート
        export_path = Path(temp_dir) / "exported_config.json"
        assert manager.export_config(export_path), "エクスポートに失敗"
        assert export_path.exists(), "エクスポートファイルが作成されませんでした"

        # 設定をリセット
        manager.config.reset_to_defaults()
        assert manager.config.ui.theme == "auto", "リセットに失敗"

        # インポート
        assert manager.import_config(export_path), "インポートに失敗"
        assert (
            manager.config.ui.theme == "light"
        ), "インポート後の設定が正しくありません"
        assert (
            manager.config.ui.window_width == 1600
        ), "インポート後のUI設定が正しくありません"
        assert (
            not manager.config.move.default_date_dirs
        ), "インポート後のMove設定が正しくありません"

        print("✅ インポート・エクスポート機能テスト完了")


def demonstrate_structured_access():
    """構造化されたアクセス方法のデモ"""
    print("📋 構造化アクセス デモ")

    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / "demo_structured"
        manager = ConfigManager(config_dir)

        # 構造化されたアクセス
        print("\n🏗️ 構造化された設定アクセス:")
        print(f"UI設定 - テーマ: {manager.config.ui.theme}")
        ui_size = (
            f"{manager.config.ui.window_width}x" f"{manager.config.ui.window_height}"
        )
        print(f"UI設定 - ウィンドウサイズ: {ui_size}")
        print(f"Photo設定 - ドライラン: {manager.config.photo.default_dry_run}")
        print(
            f"Move設定 - 日付ディレクトリ作成: {manager.config.move.default_date_dirs}"
        )
        print(f"一般設定 - 自動保存: {manager.config.general.auto_save_config}")

        # 後方互換性のあるアクセス
        print("\n🔄 後方互換性のあるアクセス:")
        print(f"テーマ (プロパティ): {manager.config.theme}")
        print(f"ウィンドウ幅 (プロパティ): {manager.config.window_width}")
        print(f"Photo ドライラン (プロパティ): {manager.config.photo_default_dry_run}")

        # 一括更新
        print("\n⚙️ 一括設定更新:")
        manager.update_ui_settings(theme="dark", window_width=1920, window_height=1080)

        manager.update_photo_settings(default_dry_run=False, default_preserve=True)

        print("更新後の設定:")
        ui_info = (
            f"{manager.config.ui.theme}, "
            f"{manager.config.ui.window_width}x{manager.config.ui.window_height}"
        )
        print(f"  UI: {ui_info}")
        photo_info = (
            f"dry_run={manager.config.photo.default_dry_run}, "
            f"preserve={manager.config.photo.default_preserve}"
        )
        print(f"  Photo: {photo_info}")


def main():
    """メイン実行関数"""
    print("🚀 新しい設定管理システム テスト・デモ開始")
    print("=" * 60)

    try:
        test_basic_functionality()
        print()

        test_validation_functionality()
        print()

        test_import_export()
        print()

        demonstrate_structured_access()
        print()

        print("\n🎉 全テスト・デモ完了!")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        raise


if __name__ == "__main__":
    main()
