"""
統合GUIアプリケーション
"""

from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from src.core.config import ConfigManager
from src.infrastructure.logging import get_logger

# CustomTkinter の外観設定
ctk.set_appearance_mode("auto")
ctk.set_default_color_theme("blue")


class UnifiedDataBackupApp:
    """
    統一データバックアップアプリケーション

    設定管理、実機能、ユーザビリティを統合した推奨版
    """

    def __init__(self):
        # 設定管理初期化
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config

        # ロガー初期化（サービスは各タブが生成する）
        self.logger = get_logger("UnifiedDataBackupGUI")

        # メインウィンドウの初期化
        self.root = ctk.CTk()
        self.setup_window()
        self.setup_widgets()

        # 処理状態管理
        self.processing = False

        # ウィンドウクローズイベント
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_window(self):
        """ウィンドウの基本設定"""
        self.root.title("My Data Backup - 統合ファイル整理ツール")
        self.root.geometry(
            f"{self.config.ui.window_width}x{self.config.ui.window_height}"
        )
        self.root.resizable(True, True)

        # テーマ設定
        ctk.set_appearance_mode(self.config.ui.theme)

    def setup_widgets(self):
        """ウィジェットの配置"""
        # メインコンテナ
        main_container = ctk.CTkFrame(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # ヘッダー
        self.setup_header(main_container)

        # タブビュー
        self.setup_tabview(main_container)

        # ステータスバー
        self.setup_status_bar(main_container)

    def setup_header(self, parent):
        """ヘッダーセクションの設定"""
        header_frame = ctk.CTkFrame(parent)
        header_frame.pack(fill="x", pady=(0, 10))

        # タイトル
        title_label = ctk.CTkLabel(
            header_frame,
            text="My Data Backup",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.pack(side="left", padx=20, pady=15)

        # テーマ切り替えボタン
        theme_button = ctk.CTkButton(
            header_frame, text="テーマ切り替え", command=self.toggle_theme, width=120
        )
        theme_button.pack(side="right", padx=20, pady=15)

    def setup_tabview(self, parent):
        """タブビューの設定"""
        self.tabview = ctk.CTkTabview(parent)
        self.tabview.pack(fill="both", expand=True, pady=(0, 10))

        # Moveタブ
        self.move_tab = self.tabview.add("🗂️ Move")
        self.setup_move_tab()

        # 設定タブ
        self.settings_tab = self.tabview.add("⚙️ 設定")
        self.setup_settings_tab()

        # ログタブ
        self.log_tab = self.tabview.add("📋 ログ")
        self.setup_log_tab()

    def setup_move_tab(self):
        """Move タブの設定"""
        from src.app.gui.modules.move.tab import MoveTab

        self.move_tab_instance = MoveTab(parent=self.move_tab, logger=self.logger)

    def setup_settings_tab(self):
        """設定タブの設定"""
        scroll_frame = ctk.CTkScrollableFrame(self.settings_tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # アプリケーション設定
        app_settings_frame = ctk.CTkFrame(scroll_frame)
        app_settings_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            app_settings_frame,
            text="外観設定",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(10, 10))

        # テーマ選択
        theme_frame = ctk.CTkFrame(app_settings_frame)
        theme_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(theme_frame, text="テーマ:").pack(side="left", padx=10)

        self.theme_var = ctk.StringVar(value=self.config.ui.theme)
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["auto", "light", "dark"],
            variable=self.theme_var,
            command=self.change_theme,
        )
        theme_menu.pack(side="left", padx=10)

        # ログ設定
        log_settings_frame = ctk.CTkFrame(scroll_frame)
        log_settings_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            log_settings_frame,
            text="ログ設定",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(10, 10))

        self.log_level_var = ctk.StringVar(value=self.config.ui.log_level)
        log_level_frame = ctk.CTkFrame(log_settings_frame)
        log_level_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(log_level_frame, text="ログレベル:").pack(side="left", padx=10)

        log_level_menu = ctk.CTkOptionMenu(
            log_level_frame,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            variable=self.log_level_var,
            command=self.change_log_level,
        )
        log_level_menu.pack(side="left", padx=10)

        # 設定管理
        config_management_frame = ctk.CTkFrame(scroll_frame)
        config_management_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            config_management_frame,
            text="設定管理",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(10, 10))

        config_buttons_frame = ctk.CTkFrame(config_management_frame)
        config_buttons_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkButton(
            config_buttons_frame,
            text="設定エクスポート",
            command=self.export_config,
            width=120,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            config_buttons_frame,
            text="設定インポート",
            command=self.import_config,
            width=120,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            config_buttons_frame,
            text="設定リセット",
            command=self.reset_config,
            width=120,
        ).pack(side="left", padx=5)

        # 設定情報表示
        info_frame = ctk.CTkFrame(config_management_frame)
        info_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.config_info_text = ctk.CTkTextbox(info_frame, height=100)
        self.config_info_text.pack(fill="x", padx=10, pady=10)
        self.update_config_info()

    def setup_log_tab(self):
        """ログタブの設定"""
        # ログ表示エリア
        self.log_text = ctk.CTkTextbox(self.log_tab)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)

        # ログクリアボタン
        log_button_frame = ctk.CTkFrame(self.log_tab)
        log_button_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkButton(
            log_button_frame, text="ログクリア", command=self.clear_log, width=100
        ).pack(side="right", padx=10, pady=5)

    def setup_status_bar(self, parent):
        """ステータスバーの設定"""
        self.status_frame = ctk.CTkFrame(parent, height=30)
        self.status_frame.pack(fill="x")
        self.status_frame.pack_propagate(False)

        self.status_label = ctk.CTkLabel(self.status_frame, text="準備完了", anchor="w")
        self.status_label.pack(side="left", padx=10, pady=5)

    def toggle_theme(self):
        """テーマを切り替え"""
        current = ctk.get_appearance_mode()
        new_theme = "dark" if current == "Light" else "light"
        ctk.set_appearance_mode(new_theme)
        self.theme_var.set(new_theme)
        self.config_manager.update_ui_settings(theme=new_theme)
        self.log_message(f"テーマを {new_theme} に変更しました")

    def change_theme(self, theme):
        """テーマを変更"""
        ctk.set_appearance_mode(theme)
        self.config_manager.update_ui_settings(theme=theme)
        self.log_message(f"テーマを {theme} に変更しました")

    def change_log_level(self, level):
        """ログレベルを変更"""
        self.config_manager.update_ui_settings(log_level=level)
        self.log_message(f"ログレベルを {level} に変更しました")

    def export_config(self):
        """設定をエクスポート"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="設定ファイルをエクスポート",
        )

        if file_path:
            if self.config_manager.export_config(Path(file_path)):
                messagebox.showinfo("成功", f"設定をエクスポートしました:\n{file_path}")
                self.log_message(f"設定エクスポート: {file_path}")
            else:
                messagebox.showerror("エラー", "設定のエクスポートに失敗しました")

    def import_config(self):
        """設定をインポート"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="設定ファイルをインポート",
        )

        if file_path:
            if self.config_manager.import_config(Path(file_path)):
                messagebox.showinfo(
                    "成功",
                    f"設定をインポートしました:\n{file_path}\n\nアプリケーションを再起動してください",
                )
                self.log_message(f"設定インポート: {file_path}")
                self.update_config_info()
            else:
                messagebox.showerror("エラー", "設定のインポートに失敗しました")

    def reset_config(self):
        """設定をリセット"""
        if messagebox.askyesno(
            "確認",
            "設定をデフォルトにリセットしますか？\n\n現在の設定はバックアップされます。",
        ):
            if self.config_manager.reset_to_defaults():
                messagebox.showinfo(
                    "成功",
                    "設定をリセットしました\n\nアプリケーションを再起動してください",
                )
                self.log_message("設定をリセットしました")
                self.update_config_info()
            else:
                messagebox.showerror("エラー", "設定のリセットに失敗しました")

    def update_config_info(self):
        """設定情報を更新"""
        info = self.config_manager.get_config_info()
        info_text = f"""設定ファイル: {info['config_file']}
設定ディレクトリ: {info['config_dir']}
ファイルサイズ: {info['config_size']} bytes
最終更新: {info['last_modified'] or 'N/A'}
バックアップ数: {info['backup_count']} 個"""

        self.config_info_text.delete("1.0", "end")
        self.config_info_text.insert("1.0", info_text)

    def log_message(self, message: str):
        """ログにメッセージを追加"""
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        self.log_text.insert("end", log_entry)
        self.log_text.see("end")

    def clear_log(self):
        """ログをクリア"""
        self.log_text.delete("1.0", "end")

    def on_closing(self):
        """アプリケーション終了時の処理"""
        # ウィンドウサイズを保存
        geometry = self.root.geometry()
        width, height = geometry.split("+")[0].split("x")
        self.config_manager.update_ui_settings(
            window_width=int(width), window_height=int(height)
        )

        self.log_message("アプリケーションを終了します")
        self.root.destroy()

    def run(self):
        """アプリケーション実行"""
        self.log_message("My Data Backup 起動完了")
        self.root.mainloop()


if __name__ == "__main__":
    app = UnifiedDataBackupApp()
    app.run()
