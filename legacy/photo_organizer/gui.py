#!/usr/bin/env python3
"""
RAWファイル整理ツール GUI (CustomTkinter版)
- モダンなUIでRAW/JPGファイルを整理
- photo_organizer/main.pyの機能をカスタムtkinterGUIで提供
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import threading
import sys
import os

# CustomTkinter の外観設定
ctk.set_appearance_mode("auto")  # "dark", "light", "auto"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"


class ModernPhotoOrganizerGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.setup_window()
        self.setup_variables()
        self.setup_widgets()

    def setup_window(self):
        """ウィンドウの基本設定"""
        self.root.title("📸 RAWファイル整理ツール (Modern)")
        self.root.geometry("800x700")
        self.root.resizable(True, True)

    def setup_variables(self):
        """変数の初期化"""
        self.root_dir = ctk.StringVar()
        self.log_path = ctk.StringVar()
        self.copy_var = ctk.BooleanVar()
        self.isolate_var = ctk.BooleanVar()
        self.dryrun_var = ctk.BooleanVar(value=True)  # デフォルトでオン

    def setup_widgets(self):
        """ウィジェットの配置"""
        # メインフレーム
        main_frame = ctk.CTkScrollableFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # タイトル
        title_label = ctk.CTkLabel(
            main_frame,
            text="📸 RAWファイル整理ツール",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.pack(pady=(0, 20))

        # ディレクトリ選択セクション
        self.create_directory_section(main_frame)

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

        # ルートディレクトリ
        root_frame = ctk.CTkFrame(dir_frame)
        root_frame.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(root_frame, text="処理ディレクトリ:", width=120).pack(
            side="left", padx=(10, 10), pady=10
        )
        self.root_entry = ctk.CTkEntry(root_frame, textvariable=self.root_dir)
        self.root_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=10)
        ctk.CTkButton(
            root_frame, text="参照...", command=self.choose_directory, width=80
        ).pack(side="right", padx=(0, 10), pady=10)

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
            variable=self.dryrun_var,
        ).pack(anchor="w", padx=20, pady=5)

        ctk.CTkCheckBox(
            options_frame,
            text="コピーモード（移動ではなくコピー）",
            variable=self.copy_var,
        ).pack(anchor="w", padx=20, pady=5)

        ctk.CTkCheckBox(
            options_frame,
            text="RAWファイル分離モード",
            variable=self.isolate_var,
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
            text="🚀 RAWファイル整理を実行",
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
        self.add_log("📸 RAWファイル整理ツール (Modern UI)")
        self.add_log("使用方法:")
        self.add_log("1. 処理ディレクトリを選択")
        self.add_log("2. オプションを設定")
        self.add_log("3. ログファイルを指定（任意）")
        self.add_log("4. 'RAWファイル整理を実行' をクリック")
        self.add_log("=" * 50)

    def add_log(self, message):
        """ログメッセージを追加"""
        self.output_text.insert("end", message + "\n")
        self.output_text.see("end")
        self.root.update_idletasks()

    def clear_log(self):
        """ログをクリア"""
        self.output_text.delete("1.0", "end")

    def choose_directory(self):
        """ディレクトリを選択"""
        directory = filedialog.askdirectory(
            title="処理ディレクトリを選択",
            initialdir=self.root_dir.get() if self.root_dir.get() else ".",
        )
        if directory:
            self.root_dir.set(directory)

    def choose_logfile(self):
        """ログファイルを選択"""
        log_file = filedialog.asksaveasfilename(
            title="ログファイルを選択",
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("All files", "*.*")],
        )
        if log_file:
            self.log_path.set(log_file)

    def validate_inputs(self):
        """入力値を検証"""
        if not self.root_dir.get():
            messagebox.showerror("エラー", "処理ディレクトリを選択してください")
            return False

        if not os.path.exists(self.root_dir.get()):
            messagebox.showerror("エラー", "指定されたディレクトリが存在しません")
            return False

        return True

    def execute_process(self):
        """処理を実行"""
        if not self.validate_inputs():
            return

        # 確認ダイアログ
        mode = "ドライラン" if self.dryrun_var.get() else "実行"
        copy_mode = "コピー" if self.copy_var.get() else "移動"
        isolate_mode = "有効" if self.isolate_var.get() else "無効"

        confirm_msg = f"""RAWファイル整理を開始しますか？

📁 処理ディレクトリ: {self.root_dir.get()}
📝 実行モード: {mode}
📋 処理方式: {copy_mode}
🎯 RAW分離モード: {isolate_mode}"""

        if not messagebox.askyesno("確認", confirm_msg):
            return

        # バックグラウンドで実行
        threading.Thread(target=self.run_organize_process, daemon=True).start()

    def run_organize_process(self):
        """RAWファイル整理処理を実行"""
        try:
            # UI更新
            self.progress_bar.set(0.1)
            self.progress_bar.start()
            self.status_label.configure(text="🔄 処理中...")
            self.execute_btn.configure(state="disabled")
            self.clear_log()

            # コマンド構築
            command = [sys.executable, "main.py"]
            command.append(self.root_dir.get())
            command.append(self.root_dir.get())  # 出力先は同じディレクトリ

            if self.dryrun_var.get():
                command.append("--dry-run")
            if self.copy_var.get():
                command.append("--copy")
            if self.isolate_var.get():
                command.append("--isolate")
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
                self.add_log("✅ RAWファイル整理が正常に完了しました")
                self.status_label.configure(text="✅ 完了")
                messagebox.showinfo("完了", "RAWファイル整理が正常に完了しました")
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
    app = ModernPhotoOrganizerGUI()
    app.run()


if __name__ == "__main__":
    main()
