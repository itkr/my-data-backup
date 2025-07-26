"""
Photo Organizer タブビュー
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading

from src.core.services import PhotoOrganizerService
from src.core.domain.models import OrganizationConfig
from src.infrastructure.repositories import FileSystemRepository


class PhotoOrganizerTab:
    """Photo Organizer タブの実装"""

    def __init__(self, parent, logger):
        self.parent = parent
        self.logger = logger
        self.current_task = None

        # サービスの初期化
        self.file_repository = FileSystemRepository(logger.logger)
        self.photo_service = PhotoOrganizerService(self.file_repository, logger.logger)

        self.setup_widgets()

    def setup_widgets(self):
        """ウィジェットの配置"""
        # メインフレーム
        main_frame = ctk.CTkScrollableFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # タイトル
        title_label = ctk.CTkLabel(
            main_frame,
            text="📸 Photo Organizer - RAW/JPG ファイル同期",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title_label.pack(pady=(0, 20))

        # 説明
        desc_label = ctk.CTkLabel(
            main_frame,
            text="RAWファイルとJPGファイルの対応関係を分析し、整理します",
            font=ctk.CTkFont(size=12),
        )
        desc_label.pack(pady=(0, 20))

        # ディレクトリ選択セクション
        self.setup_directory_section(main_frame)

        # オプション設定セクション
        self.setup_options_section(main_frame)

        # 実行ボタンセクション
        self.setup_action_section(main_frame)

        # 進捗表示セクション
        self.setup_progress_section(main_frame)

        # 結果表示セクション
        self.setup_result_section(main_frame)

    def setup_directory_section(self, parent):
        """ディレクトリ選択セクションの設定"""
        dir_frame = ctk.CTkFrame(parent)
        dir_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            dir_frame,
            text="📁 ディレクトリ設定",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # ソースディレクトリ
        src_frame = ctk.CTkFrame(dir_frame)
        src_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(src_frame, text="ソースディレクトリ:").pack(
            anchor="w", padx=10, pady=5
        )

        src_input_frame = ctk.CTkFrame(src_frame)
        src_input_frame.pack(fill="x", padx=10, pady=5)

        self.src_var = ctk.StringVar()
        self.src_entry = ctk.CTkEntry(
            src_input_frame,
            textvariable=self.src_var,
            placeholder_text="RAW/JPGファイルがあるディレクトリを選択",
        )
        self.src_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        src_button = ctk.CTkButton(
            src_input_frame,
            text="📂 選択",
            width=80,
            command=self.select_source_directory,
        )
        src_button.pack(side="right")

        # ターゲットディレクトリ
        target_frame = ctk.CTkFrame(dir_frame)
        target_frame.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkLabel(target_frame, text="出力ディレクトリ:").pack(
            anchor="w", padx=10, pady=5
        )

        target_input_frame = ctk.CTkFrame(target_frame)
        target_input_frame.pack(fill="x", padx=10, pady=5)

        self.target_var = ctk.StringVar()
        self.target_entry = ctk.CTkEntry(
            target_input_frame,
            textvariable=self.target_var,
            placeholder_text="整理後のファイル出力先ディレクトリを選択",
        )
        self.target_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        target_button = ctk.CTkButton(
            target_input_frame,
            text="📂 選択",
            width=80,
            command=self.select_target_directory,
        )
        target_button.pack(side="right")

    def setup_options_section(self, parent):
        """オプション設定セクションの設定"""
        options_frame = ctk.CTkFrame(parent)
        options_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            options_frame,
            text="⚙️ オプション設定",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # チェックボックスフレーム
        checkbox_frame = ctk.CTkFrame(options_frame)
        checkbox_frame.pack(fill="x", padx=10, pady=(0, 10))

        # ドライランモード
        self.dry_run_var = ctk.BooleanVar(value=True)
        dry_run_checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="🧪 ドライランモード（実際のファイル操作を行わない）",
            variable=self.dry_run_var,
        )
        dry_run_checkbox.pack(anchor="w", padx=10, pady=5)

        # ファイル保持モード
        self.preserve_var = ctk.BooleanVar(value=False)
        preserve_checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="💾 元ファイルを保持（移動ではなくコピー）",
            variable=self.preserve_var,
        )
        preserve_checkbox.pack(anchor="w", padx=10, pady=5)

        # ログ記録
        self.log_var = ctk.BooleanVar(value=True)
        log_checkbox = ctk.CTkCheckBox(
            checkbox_frame, text="📝 操作ログを記録", variable=self.log_var
        )
        log_checkbox.pack(anchor="w", padx=10, pady=5)

    def setup_action_section(self, parent):
        """実行ボタンセクションの設定"""
        action_frame = ctk.CTkFrame(parent)
        action_frame.pack(fill="x", pady=10)

        button_frame = ctk.CTkFrame(action_frame)
        button_frame.pack(pady=20)

        # 実行ボタン
        self.execute_button = ctk.CTkButton(
            button_frame,
            text="🚀 実行",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40,
            width=120,
            command=self.execute_photo_organizer,
        )
        self.execute_button.pack(side="left", padx=10)

        # 停止ボタン
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="⏹️ 停止",
            font=ctk.CTkFont(size=16),
            height=40,
            width=120,
            state="disabled",
            command=self.stop_execution,
        )
        self.stop_button.pack(side="left", padx=10)

    def setup_progress_section(self, parent):
        """進捗表示セクションの設定"""
        progress_frame = ctk.CTkFrame(parent)
        progress_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            progress_frame, text="📊 進捗状況", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # 進捗バー
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        self.progress_bar.set(0)

        # 進捗ラベル
        self.progress_label = ctk.CTkLabel(progress_frame, text="待機中...")
        self.progress_label.pack(padx=10, pady=(0, 10))

    def setup_result_section(self, parent):
        """結果表示セクションの設定"""
        result_frame = ctk.CTkFrame(parent)
        result_frame.pack(fill="both", expand=True, pady=10)

        ctk.CTkLabel(
            result_frame, text="📋 実行結果", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # 結果表示テキストボックス
        self.result_textbox = ctk.CTkTextbox(result_frame)
        self.result_textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.result_textbox.insert("1.0", "実行結果がここに表示されます...\n")

    def select_source_directory(self):
        """ソースディレクトリ選択"""
        directory = filedialog.askdirectory(title="ソースディレクトリを選択")
        if directory:
            self.src_var.set(directory)

    def select_target_directory(self):
        """ターゲットディレクトリ選択"""
        directory = filedialog.askdirectory(title="出力ディレクトリを選択")
        if directory:
            self.target_var.set(directory)

    def execute_photo_organizer(self):
        """Photo Organizer実行"""
        # 入力検証
        if not self.src_var.get():
            messagebox.showerror("エラー", "ソースディレクトリを選択してください")
            return

        if not self.target_var.get():
            messagebox.showerror("エラー", "出力ディレクトリを選択してください")
            return

        # UI状態変更
        self.execute_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.progress_bar.set(0)
        self.progress_label.configure(text="実行中...")
        self.result_textbox.delete("1.0", "end")

        # 設定作成
        config = OrganizationConfig(
            dry_run=self.dry_run_var.get(),
            preserve_original=self.preserve_var.get(),
            log_operations=self.log_var.get(),
        )

        # 別スレッドで実行
        self.current_task = threading.Thread(
            target=self._execute_worker,
            args=(Path(self.src_var.get()), Path(self.target_var.get()), config),
        )
        self.current_task.start()

    def _execute_worker(
        self, source_dir: Path, target_dir: Path, config: OrganizationConfig
    ):
        """実行ワーカー（別スレッド）"""
        try:
            result = self.photo_service.organize_photos(
                source_dir=source_dir,
                target_dir=target_dir,
                config=config,
                progress_callback=self._update_progress,
            )

            # 結果表示
            self._display_result(result)

        except Exception as e:
            self.logger.error(f"Photo Organizer実行エラー: {e}")
            messagebox.showerror("エラー", f"実行中にエラーが発生しました:\n{str(e)}")

        finally:
            # UI状態復元
            self.execute_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.progress_label.configure(text="完了")

    def _update_progress(self, current: int, total: int):
        """進捗更新"""
        if total > 0:
            progress = current / total
            self.progress_bar.set(progress)
            self.progress_label.configure(
                text=f"進捗: {current}/{total} ({progress*100:.1f}%)"
            )

    def _display_result(self, result):
        """結果表示"""
        result_text = f"""
📊 Photo Organizer 実行結果
==============================

✅ 成功: {result.success_count} ファイル
❌ 失敗: {result.error_count} ファイル
📈 成功率: {result.success_rate*100:.1f}%

処理済みファイル:
"""

        for file_info in result.processed_files[:10]:  # 最初の10件表示
            result_text += f"  • {file_info.name}\n"

        if len(result.processed_files) > 10:
            result_text += f"  ... 他 {len(result.processed_files) - 10} ファイル\n"

        if result.errors:
            result_text += "\nエラー:\n"
            for error in result.errors[:5]:  # 最初の5件表示
                result_text += f"  • {error}\n"

        self.result_textbox.insert("1.0", result_text)

    def stop_execution(self):
        """実行停止"""
        # 実装は今後追加
        self.logger.info("停止が要求されました")
        messagebox.showinfo("情報", "停止機能は今後実装予定です")
