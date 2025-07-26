"""
Move Tab モジュール
File Move 機能のGUIタブ実装
"""

import threading
from pathlib import Path
from tkinter import filedialog

import customtkinter

from src.app.gui.base.base_tab import BaseTab
from src.core.services.move_service import MoveService


class MoveTab(BaseTab):
    """Move機能のタブクラス"""

    def __init__(self, parent, logger):
        # Variables (setup_widgets()で使用するため先に初期化)
        self.var_copy_mode = customtkinter.BooleanVar()
        self.var_dry_run = customtkinter.BooleanVar()

        # Move service
        self.move_service = None
        self.move_thread = None

        super().__init__(parent, logger)

    def setup_widgets(self):
        """UI要素のセットアップ"""
        self.setup_source_directory_section()
        self.setup_destination_directory_section()
        self.setup_filter_section()
        self.setup_options_section()
        self.setup_action_buttons()
        self.setup_progress_section()

    def setup_source_directory_section(self):
        """Source directory 選択セクション"""
        self.frame_source = customtkinter.CTkFrame(self.parent)
        self.frame_source.pack(pady=10, padx=20, fill="x")

        self.label_source = customtkinter.CTkLabel(
            self.frame_source,
            text="Source Directory:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
        )
        self.label_source.pack(pady=(10, 5), anchor="w")

        self.frame_source_input = customtkinter.CTkFrame(self.frame_source)
        self.frame_source_input.pack(pady=(0, 10), padx=10, fill="x")

        self.entry_source = customtkinter.CTkEntry(
            self.frame_source_input, placeholder_text="Select source directory"
        )
        self.entry_source.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.button_browse_source = customtkinter.CTkButton(
            self.frame_source_input,
            text="Browse",
            command=self.browse_source,
            width=100,
        )
        self.button_browse_source.pack(side="right")

    def setup_destination_directory_section(self):
        """Destination directory 選択セクション"""
        self.frame_dest = customtkinter.CTkFrame(self.parent)
        self.frame_dest.pack(pady=10, padx=20, fill="x")

        self.label_dest = customtkinter.CTkLabel(
            self.frame_dest,
            text="Destination Directory:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
        )
        self.label_dest.pack(pady=(10, 5), anchor="w")

        self.frame_dest_input = customtkinter.CTkFrame(self.frame_dest)
        self.frame_dest_input.pack(pady=(0, 10), padx=10, fill="x")

        self.entry_dest = customtkinter.CTkEntry(
            self.frame_dest_input, placeholder_text="Select destination directory"
        )
        self.entry_dest.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.button_browse_dest = customtkinter.CTkButton(
            self.frame_dest_input, text="Browse", command=self.browse_dest, width=100
        )
        self.button_browse_dest.pack(side="right")

    def setup_filter_section(self):
        """Filter 設定セクション"""
        self.frame_filter = customtkinter.CTkFrame(self.parent)
        self.frame_filter.pack(pady=10, padx=20, fill="x")

        self.label_filter = customtkinter.CTkLabel(
            self.frame_filter,
            text="File Filter:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
        )
        self.label_filter.pack(pady=(10, 5), anchor="w")

        self.frame_filter_content = customtkinter.CTkFrame(self.frame_filter)
        self.frame_filter_content.pack(pady=(0, 10), padx=10, fill="x")

        self.entry_filter = customtkinter.CTkEntry(
            self.frame_filter_content,
            placeholder_text="*.txt, *.pdf, etc. (leave empty for all files)",
        )
        self.entry_filter.pack(pady=5, padx=10, fill="x")

    def setup_options_section(self):
        """Options セクション"""
        self.frame_options = customtkinter.CTkFrame(self.parent)
        self.frame_options.pack(pady=10, padx=20, fill="x")

        self.label_options = customtkinter.CTkLabel(
            self.frame_options,
            text="Options:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
        )
        self.label_options.pack(pady=(10, 5), anchor="w")

        self.frame_options_content = customtkinter.CTkFrame(self.frame_options)
        self.frame_options_content.pack(pady=(0, 10), padx=10, fill="x")

        # Copy mode checkbox
        self.checkbox_copy = customtkinter.CTkCheckBox(
            self.frame_options_content,
            text="Copy files (instead of move)",
            variable=self.var_copy_mode,
        )
        self.checkbox_copy.pack(pady=5, anchor="w")

        # Dry run checkbox
        self.checkbox_dry_run = customtkinter.CTkCheckBox(
            self.frame_options_content,
            text="Dry run (preview only)",
            variable=self.var_dry_run,
        )
        self.checkbox_dry_run.pack(pady=5, anchor="w")

    def setup_action_buttons(self):
        """Action buttons セクション"""
        self.frame_buttons = customtkinter.CTkFrame(self.parent)
        self.frame_buttons.pack(pady=10, padx=20, fill="x")

        self.button_start = customtkinter.CTkButton(
            self.frame_buttons,
            text="Start Move",
            command=self.start_move,
            height=40,
            font=customtkinter.CTkFont(size=16, weight="bold"),
        )
        self.button_start.pack(side="left", padx=(10, 5), fill="x", expand=True)

        self.button_stop = customtkinter.CTkButton(
            self.frame_buttons,
            text="Stop",
            command=self.stop_move,
            height=40,
            font=customtkinter.CTkFont(size=16, weight="bold"),
            state="disabled",
        )
        self.button_stop.pack(side="right", padx=(5, 10), fill="x", expand=True)

    def setup_progress_section(self):
        """Progress 表示セクション"""
        self.frame_progress = customtkinter.CTkFrame(self.parent)
        self.frame_progress.pack(pady=10, padx=20, fill="both", expand=True)

        self.label_progress = customtkinter.CTkLabel(
            self.frame_progress,
            text="Progress:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
        )
        self.label_progress.pack(pady=(10, 5), anchor="w")

        self.progressbar = customtkinter.CTkProgressBar(self.frame_progress)
        self.progressbar.pack(pady=5, padx=10, fill="x")
        self.progressbar.set(0)

        self.label_status = customtkinter.CTkLabel(
            self.frame_progress, text="Ready", font=customtkinter.CTkFont(size=12)
        )
        self.label_status.pack(pady=5, anchor="w")

        # Log display
        self.textbox_log = customtkinter.CTkTextbox(self.frame_progress, height=200)
        self.textbox_log.pack(pady=(5, 10), padx=10, fill="both", expand=True)

    def browse_source(self):
        """Source directory を選択"""
        directory = filedialog.askdirectory(title="Select Source Directory")
        if directory:
            self.entry_source.delete(0, "end")
            self.entry_source.insert(0, directory)

    def browse_dest(self):
        """Destination directory を選択"""
        directory = filedialog.askdirectory(title="Select Destination Directory")
        if directory:
            self.entry_dest.delete(0, "end")
            self.entry_dest.insert(0, directory)

    def validate_inputs(self):
        """入力値の検証"""
        source_path = self.entry_source.get().strip()
        dest_path = self.entry_dest.get().strip()

        if not source_path:
            self.show_error("Source directory is required")
            return False

        if not dest_path:
            self.show_error("Destination directory is required")
            return False

        if not Path(source_path).exists():
            self.show_error(f"Source directory does not exist: {source_path}")
            return False

        if source_path == dest_path:
            self.show_error("Source and destination directories cannot be the same")
            return False

        return True

    def execute(self):
        """Move処理の実行"""
        if not self.validate_inputs():
            return

        source_path = self.entry_source.get().strip()
        dest_path = self.entry_dest.get().strip()
        file_filter = self.entry_filter.get().strip() or "*"
        copy_mode = self.var_copy_mode.get()
        dry_run = self.var_dry_run.get()

        try:
            self.move_service = MoveService(self.logger)

            # Progress callback setup
            def progress_callback(current, total, message):
                progress = current / total if total > 0 else 0
                self.update_progress(progress, message)

            # Start move operation
            result = self.move_service.move_files(
                source_path=source_path,
                dest_path=dest_path,
                file_pattern=file_filter,
                copy_mode=copy_mode,
                dry_run=dry_run,
                progress_callback=progress_callback,
            )

            if result.success:
                self.update_progress(1.0, "Move completed successfully!")
                self.log_message(
                    f"✅ Completed: {
                        result.files_processed} files processed"
                )
                if result.files_skipped > 0:
                    self.log_message(f"⚠️ Skipped: {result.files_skipped} files")
            else:
                self.show_error(f"Move failed: {result.error}")

        except Exception as e:
            self.logger.error(f"Move operation failed: {e}")
            self.show_error(f"Move operation failed: {str(e)}")

    def start_move(self):
        """Move処理を開始"""
        self.reset_ui()
        self.button_start.configure(state="disabled")
        self.button_stop.configure(state="normal")

        # Start in separate thread
        self.move_thread = threading.Thread(target=self._run_move_thread)
        self.move_thread.daemon = True
        self.move_thread.start()

    def _run_move_thread(self):
        """Move処理のスレッド実行"""
        try:
            self.execute()
        finally:
            # Reset button states
            self.button_start.configure(state="normal")
            self.button_stop.configure(state="disabled")

    def stop_move(self):
        """Move処理を停止"""
        if self.move_service:
            self.move_service.stop()
        self.log_message("🛑 Stop requested...")
        self.button_stop.configure(state="disabled")
