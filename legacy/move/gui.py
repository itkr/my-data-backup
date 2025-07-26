#!/usr/bin/env python3
"""
ファイル整理ツール GUI (CustomTkinter版)
- モダンなUIでファイルを日付・拡張子ごとに整理
- move/main.pyの機能をカスタムtkinterGUIで提供
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import threading
import sys
import os
from pathlib import Path

# CustomTkinter の外観設定
ctk.set_appearance_mode("auto")  # "dark", "light", "auto"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"


class ModernFileOrganizerGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.setup_window()
        self.setup_variables()
        self.setup_widgets()

    def setup_window(self):
        """ウィンドウの基本設定"""
        self.root.title("📁 ファイル整理ツール (Modern)")
        self.root.geometry("800x750")
        self.root.resizable(True, True)

    def setup_variables(self):
        """変数の初期化"""
        self.import_dir = ctk.StringVar(value=".")
        self.export_dir = ctk.StringVar(value="./export")
        self.suffix = ctk.StringVar()
        self.log_path = ctk.StringVar()
        self.dry_run_var = ctk.BooleanVar(value=True)  # デフォルトでオン
        self.verbose_var = ctk.BooleanVar()

        # インポートディレクトリが変更された時にエクスポートディレクトリも更新
        self.import_dir.trace_add("write", self.on_import_dir_changed)

    def setup_widgets(self):
        """ウィジェットの配置"""
        # メインフレーム
        main_frame = ctk.CTkScrollableFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # タイトル
        title_label = ctk.CTkLabel(
            main_frame,
            text="📁 ファイル整理ツール",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.pack(pady=(0, 20))

        # ディレクトリ選択セクション
        self.create_directory_section(main_frame)

        # 拡張子選択セクション
        self.create_extension_section(main_frame)

        # オプションセクション
        self.create_options_section(main_frame)

        # ログファイルセクション
        self.create_log_section(main_frame)

        # 実行ボタン
        self.create_execute_button(main_frame)

        # 進捗セクション
        self.create_progress_section(main_frame)

        # 出力セクション
        self.create_output_section(main_frame)

        # 拡張子情報セクション
        self.create_extension_info_section(main_frame)

    def create_directory_section(self, parent):
        """ディレクトリ選択セクション"""
        dir_frame = ctk.CTkFrame(parent)
        dir_frame.pack(fill="x", pady=(0, 15))

        # セクションタイトル
        ctk.CTkLabel(
            dir_frame,
            text="📂 ディレクトリ設定",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(15, 10))

        # インポートディレクトリ
        import_frame = ctk.CTkFrame(dir_frame)
        import_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(import_frame, text="インポート元:", width=100).pack(
            side="left", padx=(10, 10), pady=10
        )
        self.import_entry = ctk.CTkEntry(import_frame, textvariable=self.import_dir)
        self.import_entry.pack(
            side="left", fill="x", expand=True, padx=(0, 10), pady=10
        )
        ctk.CTkButton(
            import_frame, text="参照...", command=self.choose_import_directory, width=80
        ).pack(side="right", padx=(0, 10), pady=10)

        # エクスポートディレクトリ
        export_frame = ctk.CTkFrame(dir_frame)
        export_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(export_frame, text="エクスポート先:", width=100).pack(
            side="left", padx=(10, 10), pady=10
        )
        self.export_entry = ctk.CTkEntry(export_frame, textvariable=self.export_dir)
        self.export_entry.pack(
            side="left", fill="x", expand=True, padx=(0, 10), pady=10
        )
        ctk.CTkButton(
            export_frame, text="参照...", command=self.choose_export_directory, width=80
        ).pack(side="right", padx=(0, 10), pady=10)

        # ファイル統計
        self.stats_label = ctk.CTkLabel(dir_frame, text="", text_color="gray")
        self.stats_label.pack(anchor="w", padx=20, pady=(0, 15))

    def create_extension_section(self, parent):
        """拡張子選択セクション"""
        ext_frame = ctk.CTkFrame(parent)
        ext_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            ext_frame, text="📄 拡張子設定", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 10))

        # 拡張子選択
        suffix_frame = ctk.CTkFrame(ext_frame)
        suffix_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(suffix_frame, text="拡張子:", width=100).pack(
            side="left", padx=(10, 10), pady=10
        )
        self.suffix_entry = ctk.CTkEntry(suffix_frame, textvariable=self.suffix)
        self.suffix_entry.pack(
            side="left", fill="x", expand=True, padx=(0, 10), pady=10
        )
        ctk.CTkButton(
            suffix_frame, text="すべて", command=self.clear_suffix, width=80
        ).pack(side="right", padx=(0, 10), pady=10)

        # 説明
        ctk.CTkLabel(
            ext_frame,
            text="※ 空欄の場合、すべての対応拡張子を処理します",
            text_color="gray",
        ).pack(anchor="w", padx=20, pady=(0, 15))

    def create_options_section(self, parent):
        """オプションセクション"""
        options_frame = ctk.CTkFrame(parent)
        options_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            options_frame, text="⚙️ オプション", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 10))

        ctk.CTkCheckBox(
            options_frame,
            text="ドライラン（実行しない）",
            variable=self.dry_run_var,
        ).pack(anchor="w", padx=20, pady=5)

        ctk.CTkCheckBox(
            options_frame,
            text="詳細出力",
            variable=self.verbose_var,
        ).pack(anchor="w", padx=20, pady=(5, 15))

    def create_log_section(self, parent):
        """ログファイルセクション"""
        log_frame = ctk.CTkFrame(parent)
        log_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            log_frame,
            text="📝 ログファイル（任意）",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(15, 10))

        entry_frame = ctk.CTkFrame(log_frame)
        entry_frame.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkEntry(entry_frame, textvariable=self.log_path).pack(
            side="left", fill="x", expand=True, padx=(10, 10), pady=10
        )
        ctk.CTkButton(
            entry_frame, text="選択...", command=self.choose_logfile, width=80
        ).pack(side="right", padx=(0, 10), pady=10)

    def create_execute_button(self, parent):
        """実行ボタン"""
        self.execute_btn = ctk.CTkButton(
            parent,
            text="🚀 ファイル整理を実行",
            command=self.execute_process,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
        )
        self.execute_btn.pack(pady=20)

    def create_progress_section(self, parent):
        """進捗セクション"""
        progress_frame = ctk.CTkFrame(parent)
        progress_frame.pack(fill="x", pady=(0, 15))

        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=(15, 5))
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            progress_frame, text="⏳ 待機中", text_color="gray"
        )
        self.status_label.pack(padx=20, pady=(0, 15))

    def create_output_section(self, parent):
        """出力セクション"""
        output_frame = ctk.CTkFrame(parent)
        output_frame.pack(fill="both", expand=True, pady=(0, 15))

        ctk.CTkLabel(
            output_frame, text="📄 実行ログ", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 10))

        self.output_text = ctk.CTkTextbox(output_frame, height=200)
        self.output_text.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # 初期メッセージ
        self.add_log("📁 ファイル整理ツール (Modern UI)")
        self.add_log("使用方法:")
        self.add_log("1. インポート元とエクスポート先を設定")
        self.add_log("2. 拡張子を指定（任意）")
        self.add_log("3. オプションを設定")
        self.add_log("4. 'ファイル整理を実行' をクリック")
        self.add_log("=" * 50)

    def create_extension_info_section(self, parent):
        """拡張子情報セクション"""
        info_frame = ctk.CTkFrame(parent)
        info_frame.pack(fill="x")

        ctk.CTkLabel(
            info_frame, text="📚 対応拡張子", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 10))

        # 対応拡張子の情報表示
        extensions_text = self.get_supported_extensions_text()
        ctk.CTkLabel(
            info_frame,
            text=extensions_text,
            text_color="gray",
            justify="left",
        ).pack(anchor="w", padx=20, pady=(0, 15))

    def get_supported_extensions_text(self):
        """対応拡張子のテキストを取得"""
        extensions = {
            "画像": ["JPEG", "JPG", "PNG", "GIF", "BMP", "HIF", "ARW"],
            "動画": ["MOV", "MP4", "MPG", "MTS", "LRF", "LRV"],
            "文書": ["XML"],
            "音声": ["WAV", "MP3"],
            "デザイン": ["PSD"],
        }

        lines = []
        for category, exts in extensions.items():
            lines.append(f"• {category}: {', '.join(exts[:5])}")
            if len(exts) > 5:
                lines.append(f"  {', '.join(exts[5:])}")

        return "\n".join(lines)

    def add_log(self, message):
        """ログメッセージを追加"""
        self.output_text.insert("end", message + "\n")
        self.output_text.see("end")
        self.root.update_idletasks()

    def clear_log(self):
        """ログをクリア"""
        self.output_text.delete("1.0", "end")

    def choose_import_directory(self):
        """インポートディレクトリを選択"""
        directory = filedialog.askdirectory(
            title="インポート元ディレクトリを選択", initialdir=self.import_dir.get()
        )
        if directory:
            self.import_dir.set(directory)
            self.update_file_stats()

    def on_import_dir_changed(self, *args):
        """インポートディレクトリが変更された時の処理"""
        import_path = self.import_dir.get()
        if import_path and import_path != ".":
            # インポートディレクトリ配下にexportディレクトリを設定
            export_path = os.path.join(import_path, "export")
        else:
            # カレントディレクトリの場合は./export
            export_path = "./export"

        # 現在のエクスポートディレクトリが変更されていない場合のみ更新
        current_export = self.export_dir.get()
        if (
            current_export == "export"
            or current_export == "./export"
            or current_export.endswith("/export")
            or current_export == ""
        ):
            self.export_dir.set(export_path)

    def choose_export_directory(self):
        """エクスポートディレクトリを選択"""
        directory = filedialog.askdirectory(
            title="エクスポート先ディレクトリを選択", initialdir=self.export_dir.get()
        )
        if directory:
            self.export_dir.set(directory)

    def choose_logfile(self):
        """ログファイルを選択"""
        log_file = filedialog.asksaveasfilename(
            title="ログファイルを選択",
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("All files", "*.*")],
        )
        if log_file:
            self.log_path.set(log_file)

    def clear_suffix(self):
        """拡張子をクリア（全拡張子処理）"""
        self.suffix.set("")

    def update_file_stats(self):
        """ファイル統計を更新"""
        if not self.import_dir.get() or not os.path.exists(self.import_dir.get()):
            self.stats_label.configure(text="")
            return

        try:
            import_path = Path(self.import_dir.get())
            total_files = sum(1 for f in import_path.iterdir() if f.is_file())

            # 拡張子別カウント
            ext_counts = {}
            for f in import_path.iterdir():
                if f.is_file():
                    ext = f.suffix.lower()
                    if ext:
                        ext_counts[ext] = ext_counts.get(ext, 0) + 1

            # 上位3拡張子を表示
            top_exts = sorted(ext_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            ext_text = ", ".join([f"{ext}({count})" for ext, count in top_exts])

            self.stats_label.configure(
                text=f"📁 総ファイル数: {total_files}個  主要拡張子: {ext_text}"
            )

        except Exception as e:
            self.stats_label.configure(text=f"⚠️ エラー: {str(e)}")

    def validate_inputs(self):
        """入力値を検証"""
        if not self.import_dir.get():
            messagebox.showerror("エラー", "インポート元ディレクトリを選択してください")
            return False

        if not os.path.exists(self.import_dir.get()):
            messagebox.showerror("エラー", "インポート元ディレクトリが存在しません")
            return False

        if not self.export_dir.get():
            messagebox.showerror(
                "エラー", "エクスポート先ディレクトリを指定してください"
            )
            return False

        return True

    def execute_process(self):
        """処理を実行"""
        if not self.validate_inputs():
            return

        # 確認ダイアログ
        mode = "ドライラン" if self.dry_run_var.get() else "実行"
        suffix_text = self.suffix.get() if self.suffix.get() else "すべての対応拡張子"

        confirm_msg = f"""ファイル整理を開始しますか？

📁 インポート元: {self.import_dir.get()}
📁 エクスポート先: {self.export_dir.get()}
📄 拡張子: {suffix_text}
📝 実行モード: {mode}
🔍 詳細出力: {"有効" if self.verbose_var.get() else "無効"}"""

        if not messagebox.askyesno("確認", confirm_msg):
            return

        # バックグラウンドで実行
        threading.Thread(target=self.run_organize_process, daemon=True).start()

    def run_organize_process(self):
        """ファイル整理処理を実行"""
        try:
            # UI更新
            self.progress_bar.set(0.1)
            self.progress_bar.start()
            self.status_label.configure(text="🔄 処理中...")
            self.execute_btn.configure(state="disabled")
            self.clear_log()

            # コマンド構築
            command = [sys.executable, "main.py"]
            command.extend(["--import-dir", self.import_dir.get()])
            command.extend(["--export-dir", self.export_dir.get()])

            if self.suffix.get().strip():
                command.extend(["--suffix", self.suffix.get().strip()])
            if self.dry_run_var.get():
                command.append("--dry-run")
            if self.verbose_var.get():
                command.append("--verbose")
            if self.log_path.get().strip():
                command.extend(["--log-file", self.log_path.get()])

            self.add_log(f"実行コマンド: {' '.join(command)}")
            self.add_log("=" * 50)

            # プロセス実行
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env,
                cwd=os.path.dirname(os.path.abspath(__file__)),
            )

            # 出力を逐次表示
            for line in iter(process.stdout.readline, ""):
                if line.strip():
                    self.add_log(line.rstrip())

            process.wait()
            self.progress_bar.set(1.0)

            # 結果表示
            self.add_log("=" * 50)
            if process.returncode == 0:
                self.add_log("✅ ファイル整理が正常に完了しました")
                self.status_label.configure(text="✅ 完了")
                messagebox.showinfo("完了", "ファイル整理が正常に完了しました")
            else:
                self.add_log(
                    f"❌ 処理がエラーで終了しました (終了コード: {process.returncode})"
                )
                self.status_label.configure(text="❌ エラー")
                messagebox.showerror(
                    "エラー",
                    f"処理がエラーで終了しました\n終了コード: {process.returncode}",
                )

        except Exception as e:
            self.add_log(f"❌ 実行エラー: {str(e)}")
            self.status_label.configure(text="❌ エラー")
            messagebox.showerror("エラー", f"実行エラー:\n{str(e)}")

        finally:
            self.progress_bar.stop()
            self.execute_btn.configure(state="normal")

    def run(self):
        """アプリケーションを起動"""
        self.root.mainloop()


def main():
    """メイン関数"""
    app = ModernFileOrganizerGUI()
    app.run()


if __name__ == "__main__":
    main()
