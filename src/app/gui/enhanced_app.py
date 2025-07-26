"""
統合GUIアプリケーション - フル機能版
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
from src.infrastructure.repositories import FileSystemRepository
from src.infrastructure.logging import get_logger


# CustomTkinter の外観設定
ctk.set_appearance_mode("auto")
ctk.set_default_color_theme("blue")


class UnifiedDataBackupApp:
    """
    統一データバックアップアプリケーション - フル機能版
    """

    def __init__(self, theme: str = "auto"):
        self.theme = theme
        self.logger = get_logger("UnifiedGUI")

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

        # 処理状態管理
        self.processing = False

    def setup_window(self):
        """ウィンドウの基本設定"""
        self.root.title("📁 My Data Backup v2.0 - 統合ファイル整理ツール")
        self.root.geometry("1200x900")
        self.root.resizable(True, True)

        # テーマ設定
        if self.theme != "auto":
            ctk.set_appearance_mode(self.theme)

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
        self.photo_source_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            source_input_frame,
            text="参照",
            command=lambda: self.select_directory(self.photo_source_entry),
            width=80,
        ).pack(side="right")

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
        self.photo_output_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            output_input_frame,
            text="参照",
            command=lambda: self.select_directory(self.photo_output_entry),
            width=80,
        ).pack(side="right")

        # オプション設定
        options_frame = ctk.CTkFrame(scroll_frame)
        options_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            options_frame, text="⚙️ オプション:", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self.photo_dry_run_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            options_frame,
            text="ドライランモード（実際のファイル操作を行わない）",
            variable=self.photo_dry_run_var,
        ).pack(anchor="w", padx=20, pady=5)

        self.photo_preserve_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            options_frame,
            text="オリジナルファイルを保持（コピーモード）",
            variable=self.photo_preserve_var,
        ).pack(anchor="w", padx=20, pady=(0, 10))

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
        self.move_import_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            import_input_frame,
            text="参照",
            command=lambda: self.select_directory(self.move_import_entry),
            width=80,
        ).pack(side="right")

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
        self.move_export_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            export_input_frame,
            text="参照",
            command=lambda: self.select_directory(self.move_export_entry),
            width=80,
        ).pack(side="right")

        # オプション設定
        options_frame = ctk.CTkFrame(scroll_frame)
        options_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            options_frame, text="⚙️ オプション:", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self.move_dry_run_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            options_frame,
            text="ドライランモード（実際のファイル操作を行わない）",
            variable=self.move_dry_run_var,
        ).pack(anchor="w", padx=20, pady=5)

        self.move_date_dirs_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            options_frame,
            text="日付ディレクトリを作成",
            variable=self.move_date_dirs_var,
        ).pack(anchor="w", padx=20, pady=5)

        self.move_type_dirs_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            options_frame,
            text="ファイルタイプディレクトリを作成",
            variable=self.move_type_dirs_var,
        ).pack(anchor="w", padx=20, pady=(0, 10))

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

        self.theme_var = ctk.StringVar(value="auto")
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

        self.log_level_var = ctk.StringVar(value="INFO")
        log_level_frame = ctk.CTkFrame(log_settings_frame)
        log_level_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(log_level_frame, text="ログレベル:").pack(side="left", padx=10)

        log_level_menu = ctk.CTkOptionMenu(
            log_level_frame,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            variable=self.log_level_var,
        )
        log_level_menu.pack(side="left", padx=10)

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

    def select_directory(self, entry_widget):
        """ディレクトリ選択ダイアログ"""
        directory = filedialog.askdirectory()
        if directory:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, directory)

    def toggle_theme(self):
        """テーマを切り替え"""
        current = ctk.get_appearance_mode()
        new_theme = "dark" if current == "Light" else "light"
        ctk.set_appearance_mode(new_theme)
        self.log_message(f"🎨 テーマを {new_theme} に変更しました")

    def change_theme(self, theme):
        """テーマを変更"""
        ctk.set_appearance_mode(theme)
        self.log_message(f"🎨 テーマを {theme} に変更しました")

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

    def run(self):
        """アプリケーション実行"""
        self.log_message("🚀 My Data Backup v2.0 起動完了")
        self.log_message("📋 統合GUIアプリケーションへようこそ！")
        self.root.mainloop()


if __name__ == "__main__":
    app = UnifiedDataBackupApp()
    app.run()
