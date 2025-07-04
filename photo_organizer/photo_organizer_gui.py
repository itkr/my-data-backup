import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import subprocess
import threading
import sys
import os


def run_script_with_progress():
    # 入力値検証
    if not root_dir.get():
        messagebox.showerror("エラー", "ルートディレクトリを選択してください。")
        return

    if not os.path.exists(root_dir.get()):
        messagebox.showerror("エラー", "指定されたディレクトリが存在しません。")
        return

    # 事前チェック
    jpg_dir = os.path.join(root_dir.get(), "JPG")
    raw_dir_path = os.path.join(root_dir.get(), "ARW")

    if not os.path.exists(jpg_dir):
        messagebox.showerror("エラー", f"JPGディレクトリが存在しません: {jpg_dir}")
        return

    if not os.path.exists(raw_dir_path):
        messagebox.showerror("エラー", f"RAWディレクトリが存在しません: {raw_dir_path}")
        return

    # ファイル数の事前カウント
    total_jpg_files = sum(
        1
        for root, dirs, files in os.walk(jpg_dir)
        for file in files
        if file.lower().endswith(".jpg")
    )
    total_raw_files = sum(
        1
        for root, dirs, files in os.walk(raw_dir_path)
        for file in files
        if file.lower().endswith(".arw")
    )

    if total_jpg_files == 0:
        messagebox.showwarning(
            "警告", "JPGファイルが見つかりません。処理を中止します。"
        )
        return

    if total_raw_files == 0:
        messagebox.showwarning(
            "警告", "RAWファイルが見つかりません。処理を中止します。"
        )
        return

    # 処理前の確認メッセージ
    confirm_msg = f"処理を開始しますか？\n\n"
    confirm_msg += f"📁 対象ディレクトリ: {root_dir.get()}\n"
    confirm_msg += f"📸 JPGファイル: {total_jpg_files} 個\n"
    confirm_msg += f"📷 RAWファイル: {total_raw_files} 個\n"

    if copy_var.get():
        confirm_msg += "📋 モード: コピー\n"
    else:
        confirm_msg += "📦 モード: 移動\n"

    if isolate_var.get():
        confirm_msg += "🔍 孤立RAWファイルを隔離します\n"

    if dryrun_var.get():
        confirm_msg += "🔍 ドライラン（実際の処理は行いません）\n"

    if not messagebox.askyesno("確認", confirm_msg):
        return

    options = []

    if copy_var.get():
        options.append("--copy")
    if isolate_var.get():
        options.append("--isolate-orphans")
    if dryrun_var.get():
        options.append("--dry-run")
    if log_path.get():
        options.extend(["--log-file", log_path.get()])
    if root_dir.get():
        options.extend(["--root-dir", root_dir.get()])

    command = [sys.executable, "sync_photos.py"] + options

    # 進捗バーの最大値を設定
    progress_bar["maximum"] = total_jpg_files
    progress_bar["value"] = 0

    def run():
        output_text.delete("1.0", tk.END)
        progress_bar["value"] = 0
        status_label.config(text="🔄 処理中...")

        # 処理統計用変数
        stats = {
            "total_moved": 0,
            "total_copied": 0,
            "orphan_files": 0,
            "errors": 0,
            "warnings": 0,
        }

        try:
            output_text.insert(tk.END, f"🚀 実行コマンド: {' '.join(command)}\n")
            output_text.insert(tk.END, f"📁 対象ディレクトリ: {root_dir.get()}\n")
            output_text.insert(tk.END, "=" * 60 + "\n")
            output_text.see(tk.END)

            proc = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__)),
            )

            moved_count = 0
            for line in proc.stdout:
                output_text.insert(tk.END, line)
                output_text.see(tk.END)
                app.update_idletasks()

                # 統計情報を更新
                if "📝 Moving" in line or "📝 Would move" in line:
                    stats["total_moved"] += 1
                    moved_count += 1
                elif "📝 Copying" in line or "📝 Would copy" in line:
                    stats["total_copied"] += 1
                    moved_count += 1
                elif "⚠️" in line:
                    stats["warnings"] += 1
                elif "❌" in line:
                    stats["errors"] += 1
                elif "orphan" in line.lower():
                    stats["orphan_files"] += 1

                # 進捗バーを更新
                progress_bar["value"] = min(moved_count, total_jpg_files)
                if moved_count > 0:
                    status_label.config(
                        text=f"🔄 処理中... ({moved_count}/{total_jpg_files})"
                    )

            err = proc.stderr.read()
            if err:
                output_text.insert(tk.END, "\n⚠️ エラー出力:\n" + err)
                output_text.see(tk.END)
                stats["errors"] += err.count("Error")

            proc.wait()

            # 結果サマリーを表示
            output_text.insert(tk.END, "\n" + "=" * 60 + "\n")
            output_text.insert(tk.END, "📊 処理結果サマリー\n")
            output_text.insert(tk.END, f"✅ 移動したファイル: {stats['total_moved']}\n")
            output_text.insert(
                tk.END, f"📋 コピーしたファイル: {stats['total_copied']}\n"
            )
            output_text.insert(tk.END, f"🔍 孤立RAWファイル: {stats['orphan_files']}\n")
            output_text.insert(tk.END, f"⚠️ 警告: {stats['warnings']}\n")
            output_text.insert(tk.END, f"❌ エラー: {stats['errors']}\n")
            output_text.insert(tk.END, "=" * 60 + "\n")
            output_text.see(tk.END)

            if proc.returncode == 0:
                progress_bar["value"] = total_jpg_files
                status_label.config(text="✅ 処理完了")

                # 詳細な完了メッセージ
                success_msg = f"処理が正常に完了しました！\n\n"
                success_msg += f"移動: {stats['total_moved']} ファイル\n"
                success_msg += f"コピー: {stats['total_copied']} ファイル\n"
                if stats["orphan_files"] > 0:
                    success_msg += f"孤立RAW: {stats['orphan_files']} ファイル\n"
                if stats["warnings"] > 0:
                    success_msg += f"⚠️ 警告: {stats['warnings']} 件\n"

                messagebox.showinfo("完了", success_msg)
            else:
                status_label.config(text="❌ 処理失敗")
                messagebox.showerror(
                    "エラー", f"処理が異常終了しました。終了コード: {proc.returncode}"
                )

        except FileNotFoundError:
            error_msg = (
                "sync_photos.pyが見つかりません。同じディレクトリに配置してください。"
            )
            output_text.insert(tk.END, f"❌ {error_msg}")
            status_label.config(text="❌ ファイルエラー")
            messagebox.showerror("エラー", error_msg)
        except Exception as e:
            error_msg = f"実行エラー: {str(e)}"
            output_text.insert(tk.END, f"❌ {error_msg}")
            status_label.config(text="❌ 実行エラー")
            messagebox.showerror("エラー", error_msg)

    threading.Thread(target=run, daemon=True).start()


def choose_directory():
    selected = filedialog.askdirectory()
    if selected:
        root_dir.set(selected)
        # ディレクトリ選択時に統計情報を表示
        update_stats_display()


def update_stats_display():
    """現在のディレクトリの統計情報を更新表示"""
    if not root_dir.get() or not os.path.exists(root_dir.get()):
        stats_label.config(text="")
        return

    jpg_dir = os.path.join(root_dir.get(), "JPG")
    raw_dir_path = os.path.join(root_dir.get(), "ARW")

    jpg_count = 0
    raw_count = 0

    if os.path.exists(jpg_dir):
        jpg_count = sum(
            1
            for root, dirs, files in os.walk(jpg_dir)
            for file in files
            if file.lower().endswith(".jpg")
        )

    if os.path.exists(raw_dir_path):
        raw_count = sum(
            1
            for root, dirs, files in os.walk(raw_dir_path)
            for file in files
            if file.lower().endswith(".arw")
        )

    stats_text = f"📸 JPG: {jpg_count} 個 | 📷 RAW: {raw_count} 個"
    if jpg_count == 0 and raw_count == 0:
        stats_text += " | ⚠️ ファイルが見つかりません"
    elif jpg_count == 0:
        stats_text += " | ⚠️ JPGファイルが見つかりません"
    elif raw_count == 0:
        stats_text += " | ⚠️ RAWファイルが見つかりません"

    stats_label.config(text=stats_text)


def choose_logfile():
    selected = filedialog.asksaveasfilename(
        defaultextension=".log",
        filetypes=[("Log files", "*.log"), ("All files", "*.*")],
    )
    if selected:
        log_path.set(selected)


# --- GUI構築 ---
app = tk.Tk()
app.title("RAWファイル整理ツール")
app.geometry("750x700")
app.resizable(True, True)

root_dir = tk.StringVar()
log_path = tk.StringVar()
copy_var = tk.BooleanVar()
isolate_var = tk.BooleanVar()
dryrun_var = tk.BooleanVar()

# パス入力部
tk.Label(app, text="📁 対象ルートディレクトリ (RAW / JPG を含む)").pack(
    anchor="w", padx=10, pady=(10, 0)
)
tk.Entry(app, textvariable=root_dir, width=70).pack(padx=10)
tk.Button(app, text="参照...", command=choose_directory).pack(padx=10, pady=5)

# オプション
tk.Label(app, text="⚙️ オプション").pack(anchor="w", padx=10, pady=(10, 0))
tk.Checkbutton(app, text="コピー（移動の代わり）", variable=copy_var).pack(
    anchor="w", padx=20
)
tk.Checkbutton(app, text="孤立RAWを隔離", variable=isolate_var).pack(
    anchor="w", padx=20
)
tk.Checkbutton(app, text="ドライラン（実行せず確認）", variable=dryrun_var).pack(
    anchor="w", padx=20
)

# ログファイル指定
tk.Label(app, text="📝 ログファイル出力先（オプション）").pack(
    anchor="w", padx=10, pady=(10, 0)
)
tk.Entry(app, textvariable=log_path, width=70).pack(padx=10)
tk.Button(app, text="ログファイル選択...", command=choose_logfile).pack(padx=10, pady=5)

# 実行ボタン
tk.Button(
    app,
    text="▶️ 処理を実行",
    command=run_script_with_progress,
    bg="#4CAF50",
    fg="white",
    height=2,
).pack(pady=15)

# 進捗バー
progress_bar = ttk.Progressbar(app, orient="horizontal", length=660, mode="determinate")
progress_bar.pack(padx=10, pady=(0, 5))

# ステータスラベル
status_label = tk.Label(app, text="⏳ 待機中", font=("Arial", 10), fg="#666")
status_label.pack(padx=10, pady=(0, 5))

# 統計情報ラベル
stats_label = tk.Label(app, text="", font=("Arial", 9), fg="#888")
stats_label.pack(padx=10, pady=(0, 10))

# 出力表示
output_frame = tk.Frame(app)
output_frame.pack(padx=10, pady=(0, 10), fill="both", expand=True)

tk.Label(output_frame, text="📄 実行ログ", font=("Arial", 11, "bold")).pack(anchor="w")
output_text = scrolledtext.ScrolledText(
    output_frame, width=85, height=20, font=("Courier", 9), wrap=tk.WORD
)
output_text.pack(fill="both", expand=True)

# 下部の情報パネル
info_frame = tk.Frame(app)
info_frame.pack(padx=10, pady=(0, 10), fill="x")

tk.Label(
    info_frame,
    text="💡 使用方法: 1) ルートディレクトリを選択 2) オプションを設定 3) 処理を実行",
    font=("Arial", 9),
    fg="#666",
).pack(anchor="w")

app.mainloop()
