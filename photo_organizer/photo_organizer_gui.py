import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import threading
import sys
import os

# 不要になったため削除


def get_line_type(line):
    """出力行の種類を判定する"""
    if "❌" in line or "Error" in line:
        return "error"
    elif "⚠️" in line or "Warning" in line:
        return "warning"
    elif "📝 Moving" in line or "📝 Copying" in line:
        return "success"
    elif "🔍" in line or "🧹" in line:
        return "info"
    else:
        return "default"


def insert_colored_text(text_widget, text, text_type):
    """テキストを色付きで挿入する"""
    try:
        # 開始位置を記録
        start_pos = text_widget.index(tk.END)

        # テキストを挿入
        text_widget.insert(tk.END, text)

        # 終了位置を記録
        end_pos = text_widget.index(tk.END)

        # 色付きタグを適用
        if text_type != "default":
            # 改行文字を除く範囲にタグを適用
            tag_end = f"{end_pos} -1c" if text.endswith("\n") else end_pos
            text_widget.tag_add(text_type, start_pos, tag_end)

        # 最後に移動
        text_widget.see(tk.END)

    except Exception as e:
        print(f"Error inserting text: {e}")
        print(f"Text: {text}")
        print(f"Type: {text_type}")
        # フォールバック：シンプルな挿入
        text_widget.insert(tk.END, text)


def setup_text_colors(text_widget):
    """出力テキストの色設定"""
    text_widget.tag_configure("error", foreground="red", font=("Helvetica", 11, "bold"))
    text_widget.tag_configure(
        "warning", foreground="orange", font=("Helvetica", 11, "bold")
    )
    text_widget.tag_configure(
        "success", foreground="green", font=("Helvetica", 11, "bold")
    )
    text_widget.tag_configure("info", foreground="blue", font=("Helvetica", 11, "bold"))
    text_widget.tag_configure("default", foreground="black", font=("Helvetica", 11))
    text_widget.tag_configure("sel", background="lightblue", foreground="black")


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
            # 初期メッセージの出力
            insert_colored_text(
                output_text, f"🚀 実行コマンド: {' '.join(command)}\n", "info"
            )
            insert_colored_text(
                output_text, f"📁 対象ディレクトリ: {root_dir.get()}\n", "info"
            )
            insert_colored_text(output_text, "=" * 60 + "\n", "info")

            # 処理開始メッセージ
            insert_colored_text(output_text, "🔄 処理を開始します...\n", "info")
            app.update_idletasks()

            # 環境変数を設定してPythonの出力バッファリングを無効化
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"

            proc = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=env,
                cwd=os.path.dirname(os.path.abspath(__file__)),
            )

            moved_count = 0

            # 標準出力と標準エラー出力を同時に処理
            while True:
                # 標準出力の処理
                stdout_line = proc.stdout.readline()
                if stdout_line:
                    line_type = get_line_type(stdout_line)
                    insert_colored_text(output_text, stdout_line, line_type)
                    app.update_idletasks()

                    # 統計情報を更新
                    if "📝 Moving" in stdout_line or "📝 Would move" in stdout_line:
                        stats["total_moved"] += 1
                        moved_count += 1
                    elif "📝 Copying" in stdout_line or "📝 Would copy" in stdout_line:
                        stats["total_copied"] += 1
                        moved_count += 1
                    elif "⚠️" in stdout_line:
                        stats["warnings"] += 1
                    elif "❌" in stdout_line:
                        stats["errors"] += 1
                    elif "orphan" in stdout_line.lower():
                        stats["orphan_files"] += 1

                    # 進捗バーを更新
                    progress_bar["value"] = min(moved_count, total_jpg_files)
                    if moved_count > 0:
                        status_label.config(
                            text=f"🔄 処理中... ({moved_count}/{total_jpg_files})"
                        )

                # 標準エラー出力の処理
                stderr_line = proc.stderr.readline()
                if stderr_line:
                    insert_colored_text(output_text, stderr_line, "error")
                    app.update_idletasks()
                    stats["errors"] += 1

                # プロセスが終了し、出力もなくなった場合は終了
                if not stdout_line and not stderr_line and proc.poll() is not None:
                    break

            proc.wait()

            # 結果サマリーを表示
            insert_colored_text(output_text, "\n" + "=" * 60 + "\n", "info")
            insert_colored_text(output_text, "📊 処理結果サマリー\n", "info")
            insert_colored_text(
                output_text, f"✅ 移動したファイル: {stats['total_moved']}\n", "success"
            )
            insert_colored_text(
                output_text,
                f"📋 コピーしたファイル: {stats['total_copied']}\n",
                "success",
            )
            insert_colored_text(
                output_text, f"🔍 孤立RAWファイル: {stats['orphan_files']}\n", "info"
            )
            insert_colored_text(
                output_text, f"⚠️ 警告: {stats['warnings']}\n", "warning"
            )
            insert_colored_text(output_text, f"❌ エラー: {stats['errors']}\n", "error")
            insert_colored_text(output_text, "=" * 60 + "\n", "info")

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
            insert_colored_text(output_text, f"❌ {error_msg}\n", "error")
            status_label.config(text="❌ ファイルエラー")
            messagebox.showerror("エラー", error_msg)
        except Exception as e:
            error_msg = f"実行エラー: {str(e)}"
            insert_colored_text(output_text, f"❌ {error_msg}\n", "error")
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

output_text = tk.Text(
    output_frame,
    width=85,
    height=18,
    font=("Helvetica", 11),
    wrap=tk.WORD,
    bg="white",
    fg="black",
    insertbackground="black",
    selectbackground="lightblue",
    relief="solid",
    bd=1,
)

# スクロールバーを手動で追加
scrollbar = tk.Scrollbar(output_frame, orient="vertical", command=output_text.yview)
output_text.configure(yscrollcommand=scrollbar.set)

output_text.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# 色設定を初期化
setup_text_colors(output_text)

# 初期メッセージを表示
insert_colored_text(output_text, "🔧 RAWファイル整理ツール - 待機中\n", "info")
insert_colored_text(
    output_text,
    "💡 使用方法: 対象ディレクトリを選択して「処理を実行」をクリック\n",
    "default",
)

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
