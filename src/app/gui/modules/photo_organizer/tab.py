"""
Photo Organizer タブモジュール
"""

import threading
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from src.app.gui.base import BaseTab
from src.core.domain.models import OrganizationConfig
from src.core.services import PhotoOrganizerService
from src.infrastructure.repositories import FileSystemRepository


class PhotoOrganizerTab(BaseTab):
    """Photo Organizer タブの実装"""

    def __init__(self, parent, logger):
        # サービスの初期化
        self.file_repository = FileSystemRepository(logger)
        self.photo_service = PhotoOrganizerService(self.file_repository, logger)

        super().__init__(parent, logger)

    def setup_widgets(self):
        """Photo Organizer固有のウィジェット設定"""
        # スクロールフレーム
        scroll_frame = ctk.CTkScrollableFrame(self.parent)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 説明
        description = ctk.CTkLabel(
            scroll_frame,
            text="📸 RAW/JPGファイルペアの自動整理\n\n"
            "RAWファイルとJPGファイルをペアとして認識し、指定された構造で整理します。",
            font=ctk.CTkFont(size=14),
            justify="left",
        )
        description.pack(pady=(0, 20), anchor="w")

        # 入力設定フレーム
        input_frame = ctk.CTkFrame(scroll_frame)
        input_frame.pack(fill="x", pady=(0, 15))

        # ソースディレクトリ
        ctk.CTkLabel(
            input_frame,
            text="📂 ソースディレクトリ:",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w", padx=15, pady=(15, 5))

        src_frame = ctk.CTkFrame(input_frame)
        src_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.src_var = ctk.StringVar()
        self.src_entry = ctk.CTkEntry(
            src_frame,
            textvariable=self.src_var,
            placeholder_text="ソースディレクトリを選択してください",
        )
        self.src_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)

        self.src_button = ctk.CTkButton(
            src_frame, text="📁 選択", command=self.select_source_dir, width=80
        )
        self.src_button.pack(side="right", padx=(5, 10), pady=10)

        # 出力ディレクトリ
        ctk.CTkLabel(
            input_frame,
            text="📁 出力ディレクトリ:",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w", padx=15, pady=(0, 5))

        dst_frame = ctk.CTkFrame(input_frame)
        dst_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.dst_var = ctk.StringVar()
        self.dst_entry = ctk.CTkEntry(
            dst_frame,
            textvariable=self.dst_var,
            placeholder_text="出力ディレクトリを選択してください",
        )
        self.dst_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)

        self.dst_button = ctk.CTkButton(
            dst_frame, text="📁 選択", command=self.select_output_dir, width=80
        )
        self.dst_button.pack(side="right", padx=(5, 10), pady=10)

        # オプション設定フレーム
        options_frame = ctk.CTkFrame(scroll_frame)
        options_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            options_frame,
            text="⚙️ 整理オプション:",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # ドライランオプション
        self.dry_run_var = ctk.BooleanVar(value=True)
        dry_run_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="🔍 ドライラン（実際にはファイルを移動せずに処理をシミュレート）",
            variable=self.dry_run_var,
            font=ctk.CTkFont(size=11),
        )
        dry_run_checkbox.pack(anchor="w", padx=30, pady=(0, 10))

        # 出力先に同名ファイルがある場合は常にスキップする
        ctk.CTkLabel(
            options_frame,
            text="⏭️ 出力先に同名ファイルがある場合はスキップします",
            font=ctk.CTkFont(size=11),
        ).pack(anchor="w", padx=30, pady=(0, 15))

        # 共通ウィジェット（進捗表示）
        self.setup_common_widgets()

        # 実行ボタン
        self.execute_button = ctk.CTkButton(
            scroll_frame,
            text="🚀 Photo Organizer実行",
            command=self.execute,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.execute_button.pack(pady=20)

    def select_source_dir(self):
        """ソースディレクトリ選択"""
        directory = filedialog.askdirectory(title="ソースディレクトリを選択")
        if directory:
            self.src_var.set(directory)

    def select_output_dir(self):
        """出力ディレクトリ選択"""
        directory = filedialog.askdirectory(title="出力ディレクトリを選択")
        if directory:
            self.dst_var.set(directory)

    def execute(self):
        """Photo Organizer実行"""
        # 入力検証
        source_path = Path(self.src_var.get().strip())
        target_path = Path(self.dst_var.get().strip())

        if not source_path.exists():
            self.show_error(
                "Photo Organizer", f"ソースディレクトリが存在しません: {source_path}"
            )
            return

        if not target_path.parent.exists():
            self.show_error(
                "Photo Organizer",
                f"出力先の親ディレクトリが存在しません: {
                    target_path.parent}",
            )
            return

        # 設定作成
        config = OrganizationConfig(
            dry_run=self.dry_run_var.get(),
            log_operations=True,
            preserve_original=False,
        )

        # バックグラウンド実行
        self.execute_button.configure(state="disabled")
        self.reset_ui()

        def run_photo_organizer():
            try:
                result = self.photo_service.organize_photos(
                    source_dir=source_path,
                    target_dir=target_path,
                    config=config,
                    progress_callback=self.update_progress_callback,
                )

                # 結果表示
                self.parent.after(0, lambda: self.show_result(result))

            except Exception as error:
                error_msg = str(error)
                self.parent.after(
                    0, lambda: self.show_error("Photo Organizer", error_msg)
                )
            finally:
                self.parent.after(0, self.reset_photo_organizer_ui)

        threading.Thread(target=run_photo_organizer, daemon=True).start()

    def update_progress_callback(self, current: int, total: int):
        """進捗更新コールバック"""
        self.parent.after(0, lambda: self.update_progress(current, total, "処理中"))

    def reset_photo_organizer_ui(self):
        """Photo Organizer UI リセット"""
        self.execute_button.configure(state="normal")
        self.reset_ui()
