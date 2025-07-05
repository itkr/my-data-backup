#!/usr/bin/env python3
"""
ファイル整理ツール GUI
- ファイルを日付・拡張子ごとに整理
- move/main.pyの機能をGUIで提供
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import subprocess
import threading
import sys
import os
from pathlib import Path


class FileOrganizerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_variables()
        self.setup_widgets()

    def setup_window(self):
        """ウィンドウの基本設定"""
        self.root.title("ファイル整理ツール")
        self.root.geometry("700x700")
        self.root.resizable(True, True)

    def setup_variables(self):
        """変数の初期化"""
        self.import_dir = tk.StringVar(value=".")
        self.export_dir = tk.StringVar(value="export")
        self.suffix = tk.StringVar()
        self.log_path = tk.StringVar()
        self.dry_run_var = tk.BooleanVar(value=True)  # デフォルトでオン
        self.verbose_var = tk.BooleanVar()

    def setup_widgets(self):
        """ウィジェットの配置"""
        # メインフレーム
        main_frame = tk.Frame(self.root, padx=15, pady=15)
        main_frame.pack(fill="both", expand=True)

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
        dir_frame = tk.LabelFrame(parent, text="📁 ディレクトリ設定", padx=10, pady=8)
        dir_frame.pack(fill="x", pady=(0, 10))

        # インポートディレクトリ
        import_frame = tk.Frame(dir_frame)
        import_frame.pack(fill="x", pady=(0, 8))

        tk.Label(import_frame, text="インポート元:", width=12, anchor="w").pack(
            side="left"
        )
        self.import_entry = tk.Entry(
            import_frame, textvariable=self.import_dir, font=("Arial", 10)
        )
        self.import_entry.pack(side="left", fill="x", expand=True, padx=(5, 5))
        tk.Button(
            import_frame, text="参照...", command=self.choose_import_directory
        ).pack(side="right")

        # エクスポートディレクトリ
        export_frame = tk.Frame(dir_frame)
        export_frame.pack(fill="x")

        tk.Label(export_frame, text="エクスポート先:", width=12, anchor="w").pack(
            side="left"
        )
        self.export_entry = tk.Entry(
            export_frame, textvariable=self.export_dir, font=("Arial", 10)
        )
        self.export_entry.pack(side="left", fill="x", expand=True, padx=(5, 5))
        tk.Button(
            export_frame, text="参照...", command=self.choose_export_directory
        ).pack(side="right")

        # ファイル統計
        self.stats_label = tk.Label(dir_frame, text="", font=("Arial", 9), fg="gray")
        self.stats_label.pack(anchor="w", pady=(8, 0))

    def create_extension_section(self, parent):
        """拡張子選択セクション"""
        ext_frame = tk.LabelFrame(parent, text="📄 拡張子設定", padx=10, pady=8)
        ext_frame.pack(fill="x", pady=(0, 10))

        # 拡張子選択
        suffix_frame = tk.Frame(ext_frame)
        suffix_frame.pack(fill="x")

        tk.Label(suffix_frame, text="拡張子:", width=12, anchor="w").pack(side="left")
        self.suffix_entry = tk.Entry(
            suffix_frame, textvariable=self.suffix, font=("Arial", 10)
        )
        self.suffix_entry.pack(side="left", fill="x", expand=True, padx=(5, 5))
        tk.Button(suffix_frame, text="すべて", command=self.clear_suffix).pack(
            side="right"
        )

        # 説明
        tk.Label(
            ext_frame,
            text="※ 空欄の場合、すべての対応拡張子を処理します",
            font=("Arial", 9),
            fg="gray",
        ).pack(anchor="w", pady=(5, 0))

    def create_options_section(self, parent):
        """オプションセクション"""
        options_frame = tk.LabelFrame(parent, text="⚙️ オプション", padx=10, pady=8)
        options_frame.pack(fill="x", pady=(0, 10))

        tk.Checkbutton(
            options_frame,
            text="ドライラン（実行しない）",
            variable=self.dry_run_var,
            font=("Arial", 10),
        ).pack(anchor="w")

        tk.Checkbutton(
            options_frame,
            text="詳細出力",
            variable=self.verbose_var,
            font=("Arial", 10),
        ).pack(anchor="w")

    def create_log_section(self, parent):
        """ログファイルセクション"""
        log_frame = tk.LabelFrame(
            parent, text="📝 ログファイル（任意）", padx=10, pady=8
        )
        log_frame.pack(fill="x", pady=(0, 10))

        entry_frame = tk.Frame(log_frame)
        entry_frame.pack(fill="x")

        tk.Entry(entry_frame, textvariable=self.log_path, font=("Arial", 10)).pack(
            side="left", fill="x", expand=True
        )
        tk.Button(entry_frame, text="選択...", command=self.choose_logfile).pack(
            side="right", padx=(5, 0)
        )

    def create_execute_button(self, parent):
        """実行ボタン"""
        tk.Button(
            parent,
            text="🚀 ファイル整理を実行",
            command=self.execute_process,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2,
            cursor="hand2",
        ).pack(pady=15)

    def create_progress_section(self, parent):
        """進捗セクション"""
        progress_frame = tk.Frame(parent)
        progress_frame.pack(fill="x", pady=(0, 10))

        self.progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate")
        self.progress_bar.pack(fill="x", pady=(0, 5))

        self.status_label = tk.Label(
            progress_frame, text="⏳ 待機中", font=("Arial", 10), fg="#666"
        )
        self.status_label.pack()

    def create_output_section(self, parent):
        """出力セクション"""
        output_frame = tk.LabelFrame(parent, text="📄 実行ログ", padx=10, pady=8)
        output_frame.pack(fill="both", expand=True, pady=(0, 10))

        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            height=12,
            font=("Courier New", 10),
            bg="white",
            fg="black",
            wrap=tk.WORD,
        )
        self.output_text.pack(fill="both", expand=True)

        # 初期メッセージ
        self.add_log("ファイル整理ツール")
        self.add_log("使用方法:")
        self.add_log("1. インポート元とエクスポート先を設定")
        self.add_log("2. 拡張子を指定（任意）")
        self.add_log("3. オプションを設定")
        self.add_log("4. 'ファイル整理を実行' をクリック")
        self.add_log("=" * 50)

    def create_extension_info_section(self, parent):
        """拡張子情報セクション"""
        info_frame = tk.LabelFrame(parent, text="📚 対応拡張子", padx=10, pady=8)
        info_frame.pack(fill="x")

        # 対応拡張子の情報表示
        extensions_text = self.get_supported_extensions_text()
        tk.Label(
            info_frame,
            text=extensions_text,
            font=("Arial", 9),
            fg="gray",
            justify="left",
        ).pack(anchor="w")

    def get_supported_extensions_text(self):
        """対応拡張子のテキストを取得"""
        # main.pyから拡張子情報を読み込む
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
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()

    def clear_log(self):
        """ログをクリア"""
        self.output_text.delete(1.0, tk.END)

    def choose_import_directory(self):
        """インポートディレクトリを選択"""
        directory = filedialog.askdirectory(
            title="インポート元ディレクトリを選択", initialdir=self.import_dir.get()
        )
        if directory:
            self.import_dir.set(directory)
            self.update_file_stats()

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
            self.stats_label.config(text="")
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

            self.stats_label.config(
                text=f"📁 総ファイル数: {total_files}個  主要拡張子: {ext_text}"
            )

        except Exception as e:
            self.stats_label.config(text=f"⚠️ エラー: {str(e)}")

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
            self.progress_bar.start()
            self.status_label.config(text="🔄 処理中...")
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

            # 結果表示
            self.add_log("=" * 50)
            if process.returncode == 0:
                self.add_log("✅ ファイル整理が正常に完了しました")
                self.status_label.config(text="✅ 完了")
                messagebox.showinfo("完了", "ファイル整理が正常に完了しました")
            else:
                self.add_log(
                    f"❌ 処理がエラーで終了しました (終了コード: {process.returncode})"
                )
                self.status_label.config(text="❌ エラー")
                messagebox.showerror(
                    "エラー",
                    f"処理がエラーで終了しました\n終了コード: {process.returncode}",
                )

        except Exception as e:
            self.add_log(f"❌ 実行エラー: {str(e)}")
            self.status_label.config(text="❌ エラー")
            messagebox.showerror("エラー", f"実行エラー:\n{str(e)}")

        finally:
            self.progress_bar.stop()

    def run(self):
        """アプリケーションを起動"""
        self.root.mainloop()


def main():
    """メイン関数"""
    app = FileOrganizerGUI()
    app.run()


if __name__ == "__main__":
    main()
