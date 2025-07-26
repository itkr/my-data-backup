"""
統合GUIアプリケーション
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import threading
from pathlib import Path
from typing import Optional, Callable

# プロジェクトルートをPythonパスに追加
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.services.photo_organizer_service import PhotoOrganizerService
from src.core.services.move_service import MoveService
from src.core.domain.models import OrganizationConfig
from src.core.config import ConfigManager
from src.infrastructure.repositories import FileSystemRepository
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

        # ロガー初期化
        self.logger = get_logger("UnifiedDataBackupGUI")

        # サービス初期化
        self.file_repository = FileSystemRepository(self.logger.logger)
        self.photo_service = PhotoOrganizerService(
            self.file_repository, self.logger.logger
        )
        self.move_service = MoveService(self.file_repository, self.logger.logger)

        # メインウィンドウの初期化
        self.root = ctk.CTk()
        self.setup_window()
        self.setup_widgets()
        self.load_saved_settings()

        # 処理状態管理
        self.processing = False

        # ウィンドウクローズイベント
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_window(self):
        """ウィンドウの基本設定"""
        self.root.title("📁 My Data Backup v2.0 - 統合ファイル整理ツール")
        self.root.geometry(f"{self.config.window_width}x{self.config.window_height}")
        self.root.resizable(True, True)

        # テーマ設定
        ctk.set_appearance_mode(self.config.theme)

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
            text="📁 My Data Backup v2.0",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.pack(side="left", padx=20, pady=15)

        # テーマ切り替えボタン
        theme_button = ctk.CTkButton(
            header_frame, text="🎨 テーマ切り替え", command=self.toggle_theme, width=120
        )
        theme_button.pack(side="right", padx=20, pady=15)

    def setup_tabview(self, parent):
        """タブビューの設定"""
        self.tabview = ctk.CTkTabview(parent)
        self.tabview.pack(fill="both", expand=True, pady=(0, 10))

        # Photo Organizerタブ
        self.photo_tab = self.tabview.add("📸 Photo Organizer")
        self.setup_photo_organizer_tab()

        # Moveタブ
        self.move_tab = self.tabview.add("🗂️ Move")
        self.setup_move_tab()

        # 設定タブ
        self.settings_tab = self.tabview.add("⚙️ 設定")
        self.setup_settings_tab()

        # ログタブ
        self.log_tab = self.tabview.add("📋 ログ")
        self.setup_log_tab()

    def setup_photo_organizer_tab(self):
        """Photo Organizerタブの設定"""
        # スクロールフレーム
        scroll_frame = ctk.CTkScrollableFrame(self.photo_tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 説明
        description = ctk.CTkLabel(
            scroll_frame,
            text="📸 RAW/JPGファイルの同期処理\n対応関係のないファイルを孤立ファイルとして管理します",
            font=ctk.CTkFont(size=14),
        )
        description.pack(pady=(0, 20))

        # ソースディレクトリ選択
        source_frame = ctk.CTkFrame(scroll_frame)
        source_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            source_frame, text="📂 ソースディレクトリ:", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        source_input_frame = ctk.CTkFrame(source_frame)
        source_input_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.photo_source_entry = ctk.CTkEntry(
            source_input_frame,
            placeholder_text="RAW/JPGファイルのソースディレクトリを選択",
        )
        self.photo_source_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        ctk.CTkButton(
            source_input_frame,
            text="参照",
            command=lambda: self.select_directory(
                self.photo_source_entry, "photo_last_source_dir"
            ),
            width=60,
        ).pack(side="right", padx=(0, 5))

        # 最近使用したディレクトリボタン
        if self.config.recent_directories:
            recent_button = ctk.CTkButton(
                source_input_frame,
                text="📋",
                command=lambda: self.show_recent_directories(self.photo_source_entry),
                width=30,
            )
            recent_button.pack(side="right")

        # 出力ディレクトリ選択
        output_frame = ctk.CTkFrame(scroll_frame)
        output_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            output_frame, text="📁 出力ディレクトリ:", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        output_input_frame = ctk.CTkFrame(output_frame)
        output_input_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.photo_output_entry = ctk.CTkEntry(
            output_input_frame, placeholder_text="整理されたファイルの出力先を選択"
        )
        self.photo_output_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        ctk.CTkButton(
            output_input_frame,
            text="参照",
            command=lambda: self.select_directory(
                self.photo_output_entry, "photo_last_output_dir"
            ),
            width=60,
        ).pack(side="right", padx=(0, 5))

        if self.config.recent_directories:
            recent_button = ctk.CTkButton(
                output_input_frame,
                text="📋",
                command=lambda: self.show_recent_directories(self.photo_output_entry),
                width=30,
            )
            recent_button.pack(side="right")

        # オプション設定
        options_frame = ctk.CTkFrame(scroll_frame)
        options_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            options_frame, text="⚙️ オプション:", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self.photo_dry_run_var = ctk.BooleanVar(value=self.config.photo_default_dry_run)
        dry_run_check = ctk.CTkCheckBox(
            options_frame,
            text="ドライランモード（実際のファイル操作を行わない）",
            variable=self.photo_dry_run_var,
            command=lambda: self.config_manager.update_photo_settings(
                default_dry_run=self.photo_dry_run_var.get()
            ),
        )
        dry_run_check.pack(anchor="w", padx=20, pady=5)

        self.photo_preserve_var = ctk.BooleanVar(
            value=self.config.photo_default_preserve
        )
        preserve_check = ctk.CTkCheckBox(
            options_frame,
            text="オリジナルファイルを保持（コピーモード）",
            variable=self.photo_preserve_var,
            command=lambda: self.config_manager.update_photo_settings(
                default_preserve=self.photo_preserve_var.get()
            ),
        )
        preserve_check.pack(anchor="w", padx=20, pady=(0, 10))

        # 実行ボタン
        self.photo_execute_button = ctk.CTkButton(
            scroll_frame,
            text="🚀 Photo Organizer実行",
            command=self.execute_photo_organizer,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.photo_execute_button.pack(pady=20)

        # 進捗バー
        self.photo_progress = ctk.CTkProgressBar(scroll_frame)
        self.photo_progress.pack(fill="x", padx=20, pady=(0, 10))
        self.photo_progress.set(0)

    def setup_move_tab(self):
        """Moveタブの設定"""
        # スクロールフレーム
        scroll_frame = ctk.CTkScrollableFrame(self.move_tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 説明
        description = ctk.CTkLabel(
            scroll_frame,
            text="🗂️ 日付・拡張子ごとのファイル整理\n画像、動画、音声、ドキュメントファイルを日付別に整理します",
            font=ctk.CTkFont(size=14),
        )
        description.pack(pady=(0, 20))

        # インポートディレクトリ選択
        import_frame = ctk.CTkFrame(scroll_frame)
        import_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            import_frame,
            text="📥 インポートディレクトリ:",
            font=ctk.CTkFont(weight="bold"),
        ).pack(anchor="w", padx=10, pady=(10, 5))

        import_input_frame = ctk.CTkFrame(import_frame)
        import_input_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.move_import_entry = ctk.CTkEntry(
            import_input_frame, placeholder_text="整理するファイルのディレクトリを選択"
        )
        self.move_import_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        ctk.CTkButton(
            import_input_frame,
            text="参照",
            command=lambda: self.select_directory(
                self.move_import_entry, "move_last_import_dir"
            ),
            width=60,
        ).pack(side="right", padx=(0, 5))

        if self.config.recent_directories:
            recent_button = ctk.CTkButton(
                import_input_frame,
                text="📋",
                command=lambda: self.show_recent_directories(self.move_import_entry),
                width=30,
            )
            recent_button.pack(side="right")

        # エクスポートディレクトリ選択
        export_frame = ctk.CTkFrame(scroll_frame)
        export_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            export_frame,
            text="📤 エクスポートディレクトリ:",
            font=ctk.CTkFont(weight="bold"),
        ).pack(anchor="w", padx=10, pady=(10, 5))

        export_input_frame = ctk.CTkFrame(export_frame)
        export_input_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.move_export_entry = ctk.CTkEntry(
            export_input_frame, placeholder_text="整理されたファイルの出力先を選択"
        )
        self.move_export_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        ctk.CTkButton(
            export_input_frame,
            text="参照",
            command=lambda: self.select_directory(
                self.move_export_entry, "move_last_export_dir"
            ),
            width=60,
        ).pack(side="right", padx=(0, 5))

        if self.config.recent_directories:
            recent_button = ctk.CTkButton(
                export_input_frame,
                text="📋",
                command=lambda: self.show_recent_directories(self.move_export_entry),
                width=30,
            )
            recent_button.pack(side="right")

        # オプション設定
        options_frame = ctk.CTkFrame(scroll_frame)
        options_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            options_frame, text="⚙️ オプション:", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self.move_dry_run_var = ctk.BooleanVar(value=self.config.move_default_dry_run)
        dry_run_check = ctk.CTkCheckBox(
            options_frame,
            text="ドライランモード（実際のファイル操作を行わない）",
            variable=self.move_dry_run_var,
            command=lambda: self.config_manager.update_move_settings(
                default_dry_run=self.move_dry_run_var.get()
            ),
        )
        dry_run_check.pack(anchor="w", padx=20, pady=5)

        self.move_date_dirs_var = ctk.BooleanVar(
            value=self.config.move_default_date_dirs
        )
        date_dirs_check = ctk.CTkCheckBox(
            options_frame,
            text="日付ディレクトリを作成",
            variable=self.move_date_dirs_var,
            command=lambda: self.config_manager.update_move_settings(
                default_date_dirs=self.move_date_dirs_var.get()
            ),
        )
        date_dirs_check.pack(anchor="w", padx=20, pady=5)

        self.move_type_dirs_var = ctk.BooleanVar(
            value=self.config.move_default_type_dirs
        )
        type_dirs_check = ctk.CTkCheckBox(
            options_frame,
            text="ファイルタイプディレクトリを作成",
            variable=self.move_type_dirs_var,
            command=lambda: self.config_manager.update_move_settings(
                default_type_dirs=self.move_type_dirs_var.get()
            ),
        )
        type_dirs_check.pack(anchor="w", padx=20, pady=(0, 10))

        # 実行ボタン
        self.move_execute_button = ctk.CTkButton(
            scroll_frame,
            text="🚀 Move実行",
            command=self.execute_move,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.move_execute_button.pack(pady=20)

        # 進捗バー
        self.move_progress = ctk.CTkProgressBar(scroll_frame)
        self.move_progress.pack(fill="x", padx=20, pady=(0, 10))
        self.move_progress.set(0)

    def setup_settings_tab(self):
        """設定タブの設定"""
        scroll_frame = ctk.CTkScrollableFrame(self.settings_tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # アプリケーション設定
        app_settings_frame = ctk.CTkFrame(scroll_frame)
        app_settings_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            app_settings_frame,
            text="🎨 外観設定",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(10, 10))

        # テーマ選択
        theme_frame = ctk.CTkFrame(app_settings_frame)
        theme_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(theme_frame, text="テーマ:").pack(side="left", padx=10)

        self.theme_var = ctk.StringVar(value=self.config.theme)
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
            text="📋 ログ設定",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(10, 10))

        self.log_level_var = ctk.StringVar(value=self.config.log_level)
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
            text="⚙️ 設定管理",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(10, 10))

        config_buttons_frame = ctk.CTkFrame(config_management_frame)
        config_buttons_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkButton(
            config_buttons_frame,
            text="📤 設定エクスポート",
            command=self.export_config,
            width=120,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            config_buttons_frame,
            text="📥 設定インポート",
            command=self.import_config,
            width=120,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            config_buttons_frame,
            text="🔄 設定リセット",
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
            log_button_frame, text="🗑️ ログクリア", command=self.clear_log, width=100
        ).pack(side="right", padx=10, pady=5)

    def setup_status_bar(self, parent):
        """ステータスバーの設定"""
        self.status_frame = ctk.CTkFrame(parent, height=30)
        self.status_frame.pack(fill="x")
        self.status_frame.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            self.status_frame, text="📍 準備完了", anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=5)

    def load_saved_settings(self):
        """保存された設定を読み込み"""
        # 最後に使用したディレクトリを復元
        if self.config.photo_last_source_dir:
            self.photo_source_entry.insert(0, self.config.photo_last_source_dir)
        if self.config.photo_last_output_dir:
            self.photo_output_entry.insert(0, self.config.photo_last_output_dir)
        if self.config.move_last_import_dir:
            self.move_import_entry.insert(0, self.config.move_last_import_dir)
        if self.config.move_last_export_dir:
            self.move_export_entry.insert(0, self.config.move_last_export_dir)

    def select_directory(self, entry_widget, config_key: str):
        """ディレクトリ選択ダイアログ"""
        directory = filedialog.askdirectory()
        if directory:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, directory)

            # 設定を更新
            if config_key.startswith("photo_"):
                self.config_manager.update_photo_settings(
                    **{config_key.replace("photo_", ""): directory}
                )
            elif config_key.startswith("move_"):
                self.config_manager.update_move_settings(
                    **{config_key.replace("move_", ""): directory}
                )

            # 最近使用したディレクトリに追加
            self.config_manager.update_recent_directory(directory)

    def show_recent_directories(self, entry_widget):
        """最近使用したディレクトリを表示"""
        recent_dirs = self.config_manager.get_recent_directories(limit=10)
        if not recent_dirs:
            messagebox.showinfo("情報", "最近使用したディレクトリはありません")
            return

        # 選択ダイアログ作成
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("📋 最近使用したディレクトリ")
        dialog.geometry("600x400")
        dialog.transient(self.root)

        # リストボックス
        listbox_frame = ctk.CTkFrame(dialog)
        listbox_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Tkinterのリストボックスを使用（CustomTkinterにはListboxがない）
        listbox = tk.Listbox(listbox_frame)
        listbox.pack(fill="both", expand=True, padx=10, pady=10)

        for directory in recent_dirs:
            listbox.insert(tk.END, directory)

        # ボタンフレーム
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        def select_directory():
            selection = listbox.curselection()
            if selection:
                selected_dir = recent_dirs[selection[0]]
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, selected_dir)
                dialog.destroy()

        ctk.CTkButton(button_frame, text="選択", command=select_directory).pack(
            side="right", padx=5
        )
        ctk.CTkButton(button_frame, text="キャンセル", command=dialog.destroy).pack(
            side="right", padx=5
        )

    def toggle_theme(self):
        """テーマを切り替え"""
        current = ctk.get_appearance_mode()
        new_theme = "dark" if current == "Light" else "light"
        ctk.set_appearance_mode(new_theme)
        self.theme_var.set(new_theme)
        self.config_manager.update_ui_settings(theme=new_theme)
        self.log_message(f"🎨 テーマを {new_theme} に変更しました")

    def change_theme(self, theme):
        """テーマを変更"""
        ctk.set_appearance_mode(theme)
        self.config_manager.update_ui_settings(theme=theme)
        self.log_message(f"🎨 テーマを {theme} に変更しました")

    def change_log_level(self, level):
        """ログレベルを変更"""
        self.config_manager.update_ui_settings(log_level=level)
        self.log_message(f"📋 ログレベルを {level} に変更しました")

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
                self.log_message(f"📤 設定エクスポート: {file_path}")
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
                self.log_message(f"📥 設定インポート: {file_path}")
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
                self.log_message("🔄 設定をリセットしました")
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

    def execute_photo_organizer(self):
        """Photo Organizerを実行"""
        if self.processing:
            messagebox.showwarning("警告", "別の処理が実行中です")
            return

        source_dir = self.photo_source_entry.get().strip()
        output_dir = self.photo_output_entry.get().strip()

        if not source_dir or not output_dir:
            messagebox.showerror(
                "エラー", "ソースディレクトリと出力ディレクトリを選択してください"
            )
            return

        if not Path(source_dir).exists():
            messagebox.showerror(
                "エラー", f"ソースディレクトリが存在しません: {source_dir}"
            )
            return

        # 設定作成
        config = OrganizationConfig(
            dry_run=self.photo_dry_run_var.get(),
            preserve_original=self.photo_preserve_var.get(),
            log_operations=True,
        )

        # バックグラウンドで実行
        self.processing = True
        self.photo_execute_button.configure(state="disabled", text="🔄 実行中...")
        self.update_status("📸 Photo Organizer実行中...")

        def run_photo_organizer():
            try:
                result = self.photo_service.organize_photos(
                    source_dir=Path(source_dir),
                    target_dir=Path(output_dir),
                    config=config,
                    progress_callback=self.update_photo_progress,
                )

                # 結果表示
                self.root.after(0, lambda: self.show_photo_result(result))

            except Exception as e:
                self.root.after(0, lambda: self.show_error("Photo Organizer", str(e)))
            finally:
                self.root.after(0, self.reset_photo_organizer_ui)

        threading.Thread(target=run_photo_organizer, daemon=True).start()

    def execute_move(self):
        """Moveを実行"""
        if self.processing:
            messagebox.showwarning("警告", "別の処理が実行中です")
            return

        import_dir = self.move_import_entry.get().strip()
        export_dir = self.move_export_entry.get().strip()

        if not import_dir or not export_dir:
            messagebox.showerror(
                "エラー",
                "インポートディレクトリとエクスポートディレクトリを選択してください",
            )
            return

        if not Path(import_dir).exists():
            messagebox.showerror(
                "エラー", f"インポートディレクトリが存在しません: {import_dir}"
            )
            return

        # 設定作成
        config = OrganizationConfig(
            dry_run=self.move_dry_run_var.get(),
            create_date_dirs=self.move_date_dirs_var.get(),
            create_type_dirs=self.move_type_dirs_var.get(),
            log_operations=True,
        )

        # バックグラウンドで実行
        self.processing = True
        self.move_execute_button.configure(state="disabled", text="🔄 実行中...")
        self.update_status("🗂️ Move実行中...")

        def run_move():
            try:
                result = self.move_service.organize_by_date(
                    source_dir=Path(import_dir),
                    target_dir=Path(export_dir),
                    config=config,
                    progress_callback=self.update_move_progress,
                )

                # 結果表示
                self.root.after(0, lambda: self.show_move_result(result))

            except Exception as e:
                self.root.after(0, lambda: self.show_error("Move", str(e)))
            finally:
                self.root.after(0, self.reset_move_ui)

        threading.Thread(target=run_move, daemon=True).start()

    def update_photo_progress(self, current: int, total: int):
        """Photo Organizer進捗更新"""
        if total > 0:
            progress = current / total
            self.root.after(0, lambda: self.photo_progress.set(progress))
            self.root.after(
                0,
                lambda: self.update_status(
                    f"📸 処理中: {current}/{total} ({progress*100:.1f}%)"
                ),
            )

    def update_move_progress(self, current: int, total: int):
        """Move進捗更新"""
        if total > 0:
            progress = current / total
            self.root.after(0, lambda: self.move_progress.set(progress))
            self.root.after(
                0,
                lambda: self.update_status(
                    f"🗂️ 処理中: {current}/{total} ({progress*100:.1f}%)"
                ),
            )

    def show_photo_result(self, result):
        """Photo Organizer結果表示"""
        message = f"""Photo Organizer実行完了！
        
✅ 成功: {result.success_count} ファイル
❌ 失敗: {result.error_count} ファイル
📈 成功率: {result.success_rate*100:.1f}%

処理済みファイル: {len(result.processed_files)} 件
"""

        messagebox.showinfo("Photo Organizer完了", message)
        self.log_message(
            f"📸 Photo Organizer完了: 成功 {result.success_count}, 失敗 {result.error_count}"
        )

    def show_move_result(self, result):
        """Move結果表示"""
        message = f"""Move実行完了！
        
✅ 成功: {result.success_count} ファイル
❌ 失敗: {result.error_count} ファイル
📈 成功率: {result.success_rate*100:.1f}%

処理済みファイル: {len(result.processed_files)} 件
"""

        messagebox.showinfo("Move完了", message)
        self.log_message(
            f"🗂️ Move完了: 成功 {result.success_count}, 失敗 {result.error_count}"
        )

    def show_error(self, operation: str, error: str):
        """エラー表示"""
        messagebox.showerror(f"{operation}エラー", f"エラーが発生しました:\n{error}")
        self.log_message(f"❌ {operation}エラー: {error}")

    def reset_photo_organizer_ui(self):
        """Photo Organizer UI リセット"""
        self.processing = False
        self.photo_execute_button.configure(
            state="normal", text="🚀 Photo Organizer実行"
        )
        self.photo_progress.set(0)
        self.update_status("📍 準備完了")

    def reset_move_ui(self):
        """Move UI リセット"""
        self.processing = False
        self.move_execute_button.configure(state="normal", text="🚀 Move実行")
        self.move_progress.set(0)
        self.update_status("📍 準備完了")

    def update_status(self, message: str):
        """ステータス更新"""
        self.status_label.configure(text=message)

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

        self.log_message("👋 アプリケーションを終了します")
        self.root.destroy()

    def run(self):
        """アプリケーション実行"""
        self.log_message("🚀 My Data Backup v2.0 起動完了")
        self.log_message("📋 統合GUIアプリケーションへようこそ！")
        self.root.mainloop()


if __name__ == "__main__":
    app = UnifiedDataBackupApp()
    app.run()
