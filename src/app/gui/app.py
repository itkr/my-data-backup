"""
統一GUIアプリケーション - メインウィンドウ
"""

import customtkinter as ctk
from typing import Optional
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ..modules.photo_organizer.view import PhotoOrganizerTab
from ..modules.move.view import MoveTab
from ...infrastructure.logging import get_logger


# CustomTkinter の外観設定
ctk.set_appearance_mode("auto")  # "dark", "light", "auto"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"


class UnifiedDataBackupApp:
    """
    統一データバックアップアプリケーション

    タブベースのインターフェースで Photo Organizer と Move 機能を統合
    """

    def __init__(self, theme: str = "auto"):
        self.logger = get_logger("UnifiedApp")
        self.theme = theme

        # メインウィンドウの初期化
        self.root = ctk.CTk()
        self.setup_window()
        self.setup_widgets()

        self.logger.info("統一GUIアプリケーション初期化完了")

    def setup_window(self):
        """ウィンドウの基本設定"""
        self.root.title("📁 My Data Backup - 統合ファイル整理ツール")
        self.root.geometry("1000x800")
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

        # フッター（ステータスバー）
        self.setup_footer(main_container)

    def setup_header(self, parent):
        """ヘッダー部分の設定"""
        header_frame = ctk.CTkFrame(parent)
        header_frame.pack(fill="x", padx=5, pady=(5, 10))

        # タイトル
        title_label = ctk.CTkLabel(
            header_frame,
            text="📁 My Data Backup",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.pack(side="left", padx=20, pady=15)

        # サブタイトル
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="RAW/JPGファイル整理 & 日付ベースファイル整理",
            font=ctk.CTkFont(size=14),
        )
        subtitle_label.pack(side="left", padx=(0, 20), pady=15)

        # テーマ切り替えボタン
        theme_button = ctk.CTkButton(
            header_frame, text="🌙/☀️ テーマ", width=100, command=self.toggle_theme
        )
        theme_button.pack(side="right", padx=20, pady=15)

    def setup_tabview(self, parent):
        """タブビューの設定"""
        self.tabview = ctk.CTkTabview(parent)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=5)

        # Photo Organizer タブ
        photo_tab = self.tabview.add("📸 Photo Organizer")
        self.photo_organizer_tab = PhotoOrganizerTab(photo_tab, self.logger)

        # Move タブ
        move_tab = self.tabview.add("📁 Move")
        self.move_tab = MoveTab(move_tab, self.logger)

        # 設定タブ
        settings_tab = self.tabview.add("⚙️ 設定")
        self.setup_settings_tab(settings_tab)

        # ログタブ
        log_tab = self.tabview.add("📋 ログ")
        self.setup_log_tab(log_tab)

    def setup_settings_tab(self, parent):
        """設定タブの設定"""
        settings_frame = ctk.CTkScrollableFrame(parent)
        settings_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 設定項目
        ctk.CTkLabel(
            settings_frame,
            text="⚙️ アプリケーション設定",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(anchor="w", pady=(0, 20))

        # テーマ設定
        theme_frame = ctk.CTkFrame(settings_frame)
        theme_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(theme_frame, text="テーマ:").pack(side="left", padx=10, pady=10)

        self.theme_var = ctk.StringVar(value=self.theme)
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["auto", "light", "dark"],
            variable=self.theme_var,
            command=self.change_theme,
        )
        theme_menu.pack(side="left", padx=10, pady=10)

        # その他の設定項目（将来的に追加）
        ctk.CTkLabel(
            settings_frame, text="その他の設定項目は今後追加予定です", text_color="gray"
        ).pack(anchor="w", pady=20)

    def setup_log_tab(self, parent):
        """ログタブの設定"""
        log_frame = ctk.CTkFrame(parent)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ログ表示用テキストボックス
        self.log_textbox = ctk.CTkTextbox(log_frame)
        self.log_textbox.pack(fill="both", expand=True, padx=10, pady=10)

        # ログクリアボタン
        clear_button = ctk.CTkButton(
            log_frame, text="🗑️ ログクリア", command=self.clear_log
        )
        clear_button.pack(pady=5)

        # 初期ログメッセージ
        self.log_textbox.insert("1.0", "📋 アプリケーションログ\n")
        self.log_textbox.insert(
            "end",
            f"起動時刻: {ctk.datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        )
        self.log_textbox.insert("end", "ログがここに表示されます...\n")

    def setup_footer(self, parent):
        """フッター（ステータスバー）の設定"""
        self.status_frame = ctk.CTkFrame(parent)
        self.status_frame.pack(fill="x", padx=5, pady=(5, 5))

        self.status_label = ctk.CTkLabel(
            self.status_frame, text="✅ 準備完了", font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10, pady=5)

        # バージョン情報
        version_label = ctk.CTkLabel(
            self.status_frame,
            text="v2.0.0 - モジュラー統合版",
            font=ctk.CTkFont(size=10),
            text_color="gray",
        )
        version_label.pack(side="right", padx=10, pady=5)

    def toggle_theme(self):
        """テーマ切り替え"""
        current = ctk.get_appearance_mode()
        new_theme = "light" if current == "Dark" else "dark"
        ctk.set_appearance_mode(new_theme)
        self.theme = new_theme
        self.logger.info(f"テーマ変更: {new_theme}")

    def change_theme(self, theme: str):
        """テーマ変更"""
        ctk.set_appearance_mode(theme)
        self.theme = theme
        self.logger.info(f"テーマ変更: {theme}")

    def clear_log(self):
        """ログクリア"""
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.insert("1.0", "📋 ログクリア済み\n")

    def update_status(self, message: str):
        """ステータス更新"""
        self.status_label.configure(text=message)

    def run(self):
        """アプリケーション開始"""
        try:
            self.logger.info("統一GUIアプリケーション開始")
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"アプリケーション実行エラー: {e}")
            raise


if __name__ == "__main__":
    app = UnifiedDataBackupApp()
    app.run()
