"""
統一GUIアプリケーション - 簡易版（テスト用）
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
from pathlib import Path


# CustomTkinter の外観設定
ctk.set_appearance_mode("auto")
ctk.set_default_color_theme("blue")


class SimpleUnifiedApp:
    """
    統一データバックアップアプリケーション - 簡易版
    """
    
    def __init__(self, theme: str = "auto"):
        self.theme = theme
        
        # メインウィンドウの初期化
        self.root = ctk.CTk()
        self.setup_window()
        self.setup_widgets()
    
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
        
        # フッター
        self.setup_footer(main_container)
    
    def setup_header(self, parent):
        """ヘッダー部分の設定"""
        header_frame = ctk.CTkFrame(parent)
        header_frame.pack(fill="x", padx=5, pady=(5, 10))
        
        # タイトル
        title_label = ctk.CTkLabel(
            header_frame,
            text="📁 My Data Backup - 統合版",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=20, pady=15)
        
        # サブタイトル
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="モジュラー・コンポーネント構造によるファイル整理ツール",
            font=ctk.CTkFont(size=14)
        )
        subtitle_label.pack(side="left", padx=(0, 20), pady=15)
        
        # テーマ切り替えボタン
        theme_button = ctk.CTkButton(
            header_frame,
            text="🌙/☀️ テーマ",
            width=100,
            command=self.toggle_theme
        )
        theme_button.pack(side="right", padx=20, pady=15)
    
    def setup_tabview(self, parent):
        """タブビューの設定"""
        self.tabview = ctk.CTkTabview(parent)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Photo Organizer タブ
        photo_tab = self.tabview.add("📸 Photo Organizer")
        self.setup_photo_tab(photo_tab)
        
        # Move タブ
        move_tab = self.tabview.add("📁 Move")
        self.setup_move_tab(move_tab)
        
        # 設定タブ
        settings_tab = self.tabview.add("⚙️ 設定")
        self.setup_settings_tab(settings_tab)
        
        # ログタブ
        log_tab = self.tabview.add("📋 ログ")
        self.setup_log_tab(log_tab)
    
    def setup_photo_tab(self, parent):
        """Photo Organizer タブの設定"""
        frame = ctk.CTkScrollableFrame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # タイトル
        ctk.CTkLabel(
            frame,
            text="📸 Photo Organizer",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(0, 20))
        
        # 説明
        ctk.CTkLabel(
            frame,
            text="RAWファイルとJPGファイルの対応関係を分析し、整理します\n（現在は構造確認用の簡易版です）",
            font=ctk.CTkFont(size=12)
        ).pack(pady=(0, 20))
        
        # 仮の実行ボタン
        test_button = ctk.CTkButton(
            frame,
            text="🧪 テスト実行",
            command=lambda: messagebox.showinfo("情報", "Photo Organizer機能は実装中です")
        )
        test_button.pack(pady=10)
        
        # 機能説明
        features_text = """
機能:
• RAW/JPGファイルの対応関係分析
• ペアファイルの同期整理
• 孤立ファイルの管理
• ドライランモード
• ログ記録機能
        """
        
        features_label = ctk.CTkLabel(frame, text=features_text, justify="left")
        features_label.pack(anchor="w", pady=20)
    
    def setup_move_tab(self, parent):
        """Move タブの設定"""
        frame = ctk.CTkScrollableFrame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # タイトル
        ctk.CTkLabel(
            frame,
            text="📁 Move - 日付ベースファイル整理",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(0, 20))
        
        # 説明
        ctk.CTkLabel(
            frame,
            text="ファイルを日付・拡張子ごとに自動整理します\n（現在は構造確認用の簡易版です）",
            font=ctk.CTkFont(size=12)
        ).pack(pady=(0, 20))
        
        # 仮の実行ボタン
        test_button = ctk.CTkButton(
            frame,
            text="🧪 テスト実行",
            command=lambda: messagebox.showinfo("情報", "Move機能は実装中です")
        )
        test_button.pack(pady=10)
        
        # 機能説明
        features_text = """
機能:
• 日付ベースディレクトリ構造生成
• ファイルタイプ別分類
• 重複ファイル処理
• 進捗表示
• バッチ処理対応
        """
        
        features_label = ctk.CTkLabel(frame, text=features_text, justify="left")
        features_label.pack(anchor="w", pady=20)
    
    def setup_settings_tab(self, parent):
        """設定タブの設定"""
        frame = ctk.CTkScrollableFrame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 設定項目
        ctk.CTkLabel(
            frame,
            text="⚙️ アプリケーション設定",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(0, 20))
        
        # テーマ設定
        theme_frame = ctk.CTkFrame(frame)
        theme_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(theme_frame, text="テーマ:").pack(side="left", padx=10, pady=10)
        
        self.theme_var = ctk.StringVar(value=self.theme)
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["auto", "light", "dark"],
            variable=self.theme_var,
            command=self.change_theme
        )
        theme_menu.pack(side="left", padx=10, pady=10)
        
        # アーキテクチャ情報
        info_text = """
📋 アーキテクチャ情報:
• モジュラー・コンポーネント構造
• サービス層によるビジネスロジック分離
• リポジトリパターンによるデータアクセス抽象化
• 統一ログ機構
• GUI/CLI 両対応
        """
        
        info_label = ctk.CTkLabel(frame, text=info_text, justify="left")
        info_label.pack(anchor="w", pady=20)
    
    def setup_log_tab(self, parent):
        """ログタブの設定"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # ログ表示用テキストボックス
        self.log_textbox = ctk.CTkTextbox(frame)
        self.log_textbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # ログクリアボタン
        clear_button = ctk.CTkButton(
            frame,
            text="🗑️ ログクリア",
            command=self.clear_log
        )
        clear_button.pack(pady=5)
        
        # 初期ログメッセージ
        import datetime
        self.log_textbox.insert("1.0", "📋 アプリケーションログ - 統合版\n")
        self.log_textbox.insert("end", f"起動時刻: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.log_textbox.insert("end", "モジュラー・コンポーネント構造でのGUI統合テスト\n")
        self.log_textbox.insert("end", "ログがここに表示されます...\n")
    
    def setup_footer(self, parent):
        """フッター（ステータスバー）の設定"""
        self.status_frame = ctk.CTkFrame(parent)
        self.status_frame.pack(fill="x", padx=5, pady=(5, 5))
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="✅ 統合GUI準備完了 - モジュラー構造テスト版",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # バージョン情報
        version_label = ctk.CTkLabel(
            self.status_frame,
            text="v2.0.0-alpha - モジュラー統合版",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        version_label.pack(side="right", padx=10, pady=5)
    
    def toggle_theme(self):
        """テーマ切り替え"""
        current = ctk.get_appearance_mode()
        new_theme = "light" if current == "Dark" else "dark"
        ctk.set_appearance_mode(new_theme)
        self.theme = new_theme
        self.update_log(f"テーマ変更: {new_theme}")
    
    def change_theme(self, theme: str):
        """テーマ変更"""
        ctk.set_appearance_mode(theme)
        self.theme = theme
        self.update_log(f"テーマ変更: {theme}")
    
    def clear_log(self):
        """ログクリア"""
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.insert("1.0", "📋 ログクリア済み\n")
    
    def update_log(self, message: str):
        """ログ更新"""
        import datetime
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        self.log_textbox.insert("end", f"[{timestamp}] {message}\n")
        self.log_textbox.see("end")
    
    def run(self):
        """アプリケーション開始"""
        try:
            self.update_log("統合GUIアプリケーション開始")
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("エラー", f"アプリケーション実行エラー: {e}")
            raise


if __name__ == "__main__":
    app = SimpleUnifiedApp()
    app.run()
