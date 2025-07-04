#!/usr/bin/env python3
"""
シンプルなRAWファイル整理ツール GUI
- 検証用のデバッグ機能を除去
- 基本的な機能のみに絞り込み
- クリーンで読みやすいコード
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import subprocess
import threading
import sys
import os


class PhotoOrganizerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_variables()
        self.setup_widgets()
        
    def setup_window(self):
        """ウィンドウの基本設定"""
        self.root.title("RAWファイル整理ツール")
        self.root.geometry("700x650")
        self.root.resizable(True, True)
        
    def setup_variables(self):
        """変数の初期化"""
        self.root_dir = tk.StringVar()
        self.log_path = tk.StringVar()
        self.copy_var = tk.BooleanVar()
        self.isolate_var = tk.BooleanVar()
        self.dryrun_var = tk.BooleanVar()
        
    def setup_widgets(self):
        """ウィジェットの配置"""
        # メインフレーム
        main_frame = tk.Frame(self.root, padx=15, pady=15)
        main_frame.pack(fill="both", expand=True)
        
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
        # ディレクトリ選択
        dir_frame = tk.LabelFrame(parent, text="📁 対象ディレクトリ", padx=10, pady=8)
        dir_frame.pack(fill="x", pady=(0, 10))
        
        # エントリーとボタン
        entry_frame = tk.Frame(dir_frame)
        entry_frame.pack(fill="x")
        
        self.dir_entry = tk.Entry(entry_frame, textvariable=self.root_dir, font=("Arial", 10))
        self.dir_entry.pack(side="left", fill="x", expand=True)
        
        tk.Button(
            entry_frame, 
            text="参照...", 
            command=self.choose_directory,
            padx=10
        ).pack(side="right", padx=(5, 0))
        
        # 統計情報表示
        self.stats_label = tk.Label(dir_frame, text="", font=("Arial", 9), fg="gray")
        self.stats_label.pack(anchor="w", pady=(5, 0))
        
    def create_options_section(self, parent):
        """オプションセクション"""
        options_frame = tk.LabelFrame(parent, text="⚙️ オプション", padx=10, pady=8)
        options_frame.pack(fill="x", pady=(0, 10))
        
        tk.Checkbutton(
            options_frame, 
            text="コピー（移動しない）", 
            variable=self.copy_var,
            font=("Arial", 10)
        ).pack(anchor="w")
        
        tk.Checkbutton(
            options_frame, 
            text="孤立RAWファイルを隔離", 
            variable=self.isolate_var,
            font=("Arial", 10)
        ).pack(anchor="w")
        
        tk.Checkbutton(
            options_frame, 
            text="ドライラン（実行しない）", 
            variable=self.dryrun_var,
            font=("Arial", 10)
        ).pack(anchor="w")
        
    def create_log_section(self, parent):
        """ログファイルセクション"""
        log_frame = tk.LabelFrame(parent, text="📝 ログファイル（任意）", padx=10, pady=8)
        log_frame.pack(fill="x", pady=(0, 10))
        
        entry_frame = tk.Frame(log_frame)
        entry_frame.pack(fill="x")
        
        tk.Entry(entry_frame, textvariable=self.log_path, font=("Arial", 10)).pack(
            side="left", fill="x", expand=True
        )
        
        tk.Button(
            entry_frame, 
            text="選択...", 
            command=self.choose_logfile,
            padx=10
        ).pack(side="right", padx=(5, 0))
        
    def create_execute_button(self, parent):
        """実行ボタン"""
        tk.Button(
            parent,
            text="🚀 処理を実行",
            command=self.execute_process,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2,
            cursor="hand2"
        ).pack(pady=15)
        
    def create_progress_section(self, parent):
        """進捗セクション"""
        progress_frame = tk.Frame(parent)
        progress_frame.pack(fill="x", pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate")
        self.progress_bar.pack(fill="x", pady=(0, 5))
        
        self.status_label = tk.Label(
            progress_frame, 
            text="⏳ 待機中", 
            font=("Arial", 10), 
            fg="#666"
        )
        self.status_label.pack()
        
    def create_output_section(self, parent):
        """出力セクション"""
        output_frame = tk.LabelFrame(parent, text="📄 実行ログ", padx=10, pady=8)
        output_frame.pack(fill="both", expand=True)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            height=15,
            font=("Courier New", 10),
            bg="white",
            fg="black",
            wrap=tk.WORD
        )
        self.output_text.pack(fill="both", expand=True)
        
        # 初期メッセージ
        self.add_log("RAWファイル整理ツール")
        self.add_log("使用方法:")
        self.add_log("1. 対象ディレクトリを選択")
        self.add_log("2. 必要に応じてオプションを設定")
        self.add_log("3. '処理を実行' ボタンをクリック")
        self.add_log("=" * 50)
        
    def add_log(self, message):
        """ログメッセージを追加"""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_log(self):
        """ログをクリア"""
        self.output_text.delete(1.0, tk.END)
        
    def choose_directory(self):
        """ディレクトリを選択"""
        directory = filedialog.askdirectory(title="対象ディレクトリを選択してください")
        if directory:
            self.root_dir.set(directory)
            self.update_file_stats()
            
    def choose_logfile(self):
        """ログファイルを選択"""
        log_file = filedialog.asksaveasfilename(
            title="ログファイルを選択",
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("All files", "*.*")]
        )
        if log_file:
            self.log_path.set(log_file)
            
    def update_file_stats(self):
        """ファイル統計を更新"""
        if not self.root_dir.get():
            self.stats_label.config(text="")
            return
            
        root_path = self.root_dir.get()
        if not os.path.exists(root_path):
            self.stats_label.config(text="⚠️ ディレクトリが存在しません")
            return
            
        # JPG と RAW ファイルをカウント
        jpg_dir = os.path.join(root_path, "JPG")
        raw_dir = os.path.join(root_path, "ARW")
        
        jpg_count = self.count_files(jpg_dir, [".jpg", ".jpeg"])
        raw_count = self.count_files(raw_dir, [".arw"])
        
        self.stats_label.config(text=f"📸 JPG: {jpg_count}個  📷 RAW: {raw_count}個")
        
    def count_files(self, directory, extensions):
        """指定拡張子のファイル数をカウント"""
        if not os.path.exists(directory):
            return 0
            
        count = 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    count += 1
        return count
        
    def validate_inputs(self):
        """入力値を検証"""
        if not self.root_dir.get():
            messagebox.showerror("エラー", "対象ディレクトリを選択してください")
            return False
            
        if not os.path.exists(self.root_dir.get()):
            messagebox.showerror("エラー", "選択されたディレクトリが存在しません")
            return False
            
        # JPG と RAW ディレクトリの存在確認
        jpg_dir = os.path.join(self.root_dir.get(), "JPG")
        raw_dir = os.path.join(self.root_dir.get(), "ARW")
        
        if not os.path.exists(jpg_dir):
            messagebox.showerror("エラー", f"JPGディレクトリが見つかりません:\n{jpg_dir}")
            return False
            
        if not os.path.exists(raw_dir):
            messagebox.showerror("エラー", f"RAWディレクトリが見つかりません:\n{raw_dir}")
            return False
            
        return True
        
    def execute_process(self):
        """処理を実行"""
        if not self.validate_inputs():
            return
            
        # 確認ダイアログ
        mode = "ドライラン" if self.dryrun_var.get() else "実行"
        action = "コピー" if self.copy_var.get() else "移動"
        isolate = "有効" if self.isolate_var.get() else "無効"
        
        confirm_msg = f"""処理を開始しますか？

📁 対象ディレクトリ: {self.root_dir.get()}
📝 実行モード: {mode}
🔄 動作: {action}
🔍 孤立RAW隔離: {isolate}"""
        
        if not messagebox.askyesno("確認", confirm_msg):
            return
            
        # バックグラウンドで実行
        threading.Thread(target=self.run_sync_process, daemon=True).start()
        
    def run_sync_process(self):
        """同期処理を実行"""
        try:
            # UI更新
            self.progress_bar.start()
            self.status_label.config(text="🔄 処理中...")
            self.clear_log()
            
            # コマンド構築
            command = [sys.executable, "sync_photos.py"]
            command.extend(["--root-dir", self.root_dir.get()])
            
            if self.copy_var.get():
                command.append("--copy")
            if self.isolate_var.get():
                command.append("--isolate-orphans")
            if self.dryrun_var.get():
                command.append("--dry-run")
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
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            # 出力を逐次表示
            for line in iter(process.stdout.readline, ""):
                if line.strip():
                    self.add_log(line.rstrip())
                    
            process.wait()
            
            # 結果表示
            self.add_log("=" * 50)
            if process.returncode == 0:
                self.add_log("✅ 処理が正常に完了しました")
                self.status_label.config(text="✅ 完了")
                messagebox.showinfo("完了", "処理が正常に完了しました")
            else:
                self.add_log(f"❌ 処理がエラーで終了しました (終了コード: {process.returncode})")
                self.status_label.config(text="❌ エラー")
                messagebox.showerror("エラー", f"処理がエラーで終了しました\n終了コード: {process.returncode}")
                
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
    app = PhotoOrganizerGUI()
    app.run()


if __name__ == "__main__":
    main()
