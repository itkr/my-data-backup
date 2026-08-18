"""
ConfigManagerのテスト
"""

import json
import tempfile
import unittest
from pathlib import Path

from src.core.config import ConfigManager


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._tmp.name)
        self.config_dir = self.tmp_path / "config"

    def tearDown(self):
        self._tmp.cleanup()

    def test_settings_survive_reload(self):
        """保存した設定が新しいインスタンスで読み込める"""
        manager = ConfigManager(self.config_dir)
        manager.update_ui_settings(theme="dark", window_width=1400)

        reloaded = ConfigManager(self.config_dir)

        self.assertEqual(reloaded.config.ui.theme, "dark")
        self.assertEqual(reloaded.config.ui.window_width, 1400)

    def test_unknown_ui_keys_are_ignored(self):
        """未知のキーを渡しても無視される"""
        manager = ConfigManager(self.config_dir)
        manager.update_ui_settings(theme="dark", nonexistent_key="x")

        self.assertEqual(manager.config.ui.theme, "dark")
        self.assertFalse(hasattr(manager.config.ui, "nonexistent_key"))

    def test_old_config_file_with_removed_sections_still_loads(self):
        """削除済みセクションを含む古い設定ファイルでも読み込める"""
        self.config_dir.mkdir(parents=True)
        (self.config_dir / "config.json").write_text(
            json.dumps(
                {
                    "ui": {"theme": "light", "window_width": 1600},
                    "photo": {"default_dry_run": True},
                    "move": {"last_import_dir": "/tmp"},
                    "general": {"auto_save_config": True},
                }
            ),
            encoding="utf-8",
        )

        manager = ConfigManager(self.config_dir)

        self.assertEqual(manager.config.ui.theme, "light")
        self.assertEqual(manager.config.ui.window_width, 1600)

    def test_broken_config_file_falls_back_to_defaults(self):
        """壊れた設定ファイルでも例外にせずデフォルトで起動する"""
        self.config_dir.mkdir(parents=True)
        (self.config_dir / "config.json").write_text("{ not json", encoding="utf-8")

        manager = ConfigManager(self.config_dir)

        self.assertEqual(manager.config.ui.theme, "auto")

    def test_validate_detects_invalid_values(self):
        """不正な設定値を検出する"""
        manager = ConfigManager(self.config_dir)
        manager.config.ui.window_width = 500
        manager.config.ui.theme = "invalid_theme"

        errors = manager.validate_config()

        self.assertEqual(len(errors), 2)

    def test_auto_fix_restores_defaults(self):
        """不正な設定値をデフォルトに戻す"""
        manager = ConfigManager(self.config_dir)
        manager.config.ui.window_width = 500
        manager.config.ui.theme = "invalid_theme"

        self.assertTrue(manager.auto_fix_config())
        self.assertEqual(manager.config.ui.window_width, 1200)
        self.assertEqual(manager.config.ui.theme, "auto")
        self.assertEqual(manager.validate_config(), [])

    def test_invalid_values_are_fixed_on_startup(self):
        """起動時に不正な設定が自動修正される"""
        self.config_dir.mkdir(parents=True)
        (self.config_dir / "config.json").write_text(
            json.dumps({"ui": {"theme": "invalid", "window_width": 100}}),
            encoding="utf-8",
        )

        manager = ConfigManager(self.config_dir)

        self.assertEqual(manager.config.ui.theme, "auto")
        self.assertEqual(manager.config.ui.window_width, 1200)

    def test_export_and_import_roundtrip(self):
        """エクスポートした設定をインポートで復元できる"""
        manager = ConfigManager(self.config_dir)
        manager.update_ui_settings(theme="light", window_width=1600)

        export_path = self.tmp_path / "exported.json"
        self.assertTrue(manager.export_config(export_path))

        manager.reset_to_defaults()
        self.assertEqual(manager.config.ui.theme, "auto")

        self.assertTrue(manager.import_config(export_path))
        self.assertEqual(manager.config.ui.theme, "light")
        self.assertEqual(manager.config.ui.window_width, 1600)

    def test_import_missing_file_returns_false(self):
        """存在しないファイルのインポートは False を返す"""
        manager = ConfigManager(self.config_dir)

        self.assertFalse(manager.import_config(self.tmp_path / "missing.json"))

    def test_config_info_reports_file_state(self):
        """設定ファイルの情報を取得できる"""
        manager = ConfigManager(self.config_dir)

        info = manager.get_config_info()

        self.assertTrue(info["config_exists"])
        self.assertEqual(info["config_file"], str(manager.config_file))
        self.assertGreater(info["config_size"], 0)


if __name__ == "__main__":
    unittest.main()
