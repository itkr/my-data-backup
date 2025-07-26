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
        self.var_dry_run = customtkinter.BooleanVar(value=True)
        self.var_recursive = customtkinter.BooleanVar(value=True)

        # Extension checkboxes
        self.extension_vars = {}
        self.default_extensions = {
            "画像": [".jpg", ".jpeg", ".arw", ".raw", ".cr2", ".nef", ".dng"],
            "動画": [".mov", ".mp4", ".mpg", ".avi", ".mts", ".lrf", ".lrv"],
            "音声": [".wav", ".mp3", ".aac", ".flac"],
        }

        # Initialize extension variables
        for category, extensions in self.default_extensions.items():
            for ext in extensions:
                self.extension_vars[ext] = customtkinter.BooleanVar(value=True)

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
            text="File Extensions:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
        )
        self.label_filter.pack(pady=(10, 5), anchor="w")

        self.frame_filter_content = customtkinter.CTkFrame(self.frame_filter)
        self.frame_filter_content.pack(pady=(0, 10), padx=10, fill="both", expand=True)

        # Control buttons
        self.frame_filter_controls = customtkinter.CTkFrame(self.frame_filter_content)
        self.frame_filter_controls.pack(pady=5, padx=5, fill="x")

        self.button_select_all = customtkinter.CTkButton(
            self.frame_filter_controls,
            text="全選択",
            width=80,
            height=25,
            command=self.select_all_extensions,
        )
        self.button_select_all.pack(side="left", padx=(0, 5))

        self.button_deselect_all = customtkinter.CTkButton(
            self.frame_filter_controls,
            text="全解除",
            width=80,
            height=25,
            command=self.deselect_all_extensions,
        )
        self.button_deselect_all.pack(side="left", padx=(0, 10))

        # Extension checkboxes by category
        for category, extensions in self.default_extensions.items():
            category_frame = customtkinter.CTkFrame(self.frame_filter_content)
            category_frame.pack(pady=5, padx=5, fill="x")

            category_label = customtkinter.CTkLabel(
                category_frame,
                text=f"{category}:",
                font=customtkinter.CTkFont(size=12, weight="bold"),
            )
            category_label.pack(pady=(5, 0), anchor="w")

            extensions_frame = customtkinter.CTkFrame(category_frame)
            extensions_frame.pack(pady=(5, 10), padx=10, fill="x")

            # Create checkboxes in rows of 4
            for i, ext in enumerate(extensions):
                if i % 4 == 0:
                    row_frame = customtkinter.CTkFrame(extensions_frame)
                    row_frame.pack(pady=2, fill="x")

                checkbox = customtkinter.CTkCheckBox(
                    row_frame,
                    text=ext.upper(),
                    variable=self.extension_vars[ext],
                    width=70,
                )
                checkbox.pack(side="left", padx=5, pady=2)

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

        # Recursive search checkbox
        self.checkbox_recursive = customtkinter.CTkCheckBox(
            self.frame_options_content,
            text="Recursive search (include subdirectories)",
            variable=self.var_recursive,
        )
        self.checkbox_recursive.pack(pady=5, anchor="w")

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

        self.progress_bar = customtkinter.CTkProgressBar(self.frame_progress)
        self.progress_bar.pack(pady=5, padx=10, fill="x")
        self.progress_bar.set(0)

        self.label_status = customtkinter.CTkLabel(
            self.frame_progress,
            textvariable=self.progress_var,
            font=customtkinter.CTkFont(size=12),
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
            self.show_error("入力エラー", "Source directory is required")
            return False

        if not dest_path:
            self.show_error("入力エラー", "Destination directory is required")
            return False

        if not Path(source_path).exists():
            self.show_error(
                "パスエラー", f"Source directory does not exist: {source_path}"
            )
            return False

        return True

    def execute(self):
        """Move処理の実行"""
        if not self.validate_inputs():
            return

        source_path = Path(self.entry_source.get().strip())
        dest_path = Path(self.entry_dest.get().strip())
        selected_extensions = self.get_selected_extensions()
        copy_mode = self.var_copy_mode.get()
        dry_run = self.var_dry_run.get()
        recursive = self.var_recursive.get()

        try:
            from src.core.domain.models import OrganizationConfig
            from src.infrastructure.repositories import FileSystemRepository

            # サービス初期化
            file_repository = FileSystemRepository(self.logger)
            self.move_service = MoveService(file_repository, self.logger)

            # 設定作成
            config = OrganizationConfig(
                dry_run=dry_run,
                create_date_dirs=True,
                create_type_dirs=True,
                handle_duplicates=True,
                log_operations=True,
                preserve_original=copy_mode,
                file_extensions=selected_extensions or None,
                recursive=recursive,
            )

            # Progress callback setup
            def progress_callback(current, total):
                if total > 0:
                    progress = current / total
                    message = f"Processing {current}/{total} files..."
                    self.progress_var.set(message)
                    if self.progress_bar:
                        self.progress_bar.set(progress)

            self.progress_var.set("🚀 Starting move operation...")
            self.logger.info(f"📁 Source: {source_path}")
            self.logger.info(f"📁 Destination: {dest_path}")
            self.logger.info(f"🔧 Mode: {'Copy' if copy_mode else 'Move'}")
            self.logger.info(f"🧪 Dry run: {dry_run}")
            self.logger.info(f"🔍 Recursive: {recursive}")
            if selected_extensions:
                self.logger.info(f"📋 Extensions: {', '.join(selected_extensions)}")

            # Start move operation
            result = self.move_service.organize_by_date(
                source_dir=source_path,
                target_dir=dest_path,
                config=config,
                progress_callback=progress_callback,
            )

            # Display results
            self.progress_var.set("📊 Operation completed!")
            self.logger.info("📊 Operation completed!")
            self.logger.info(f"✅ Success: {result.success_count} files")
            self.logger.info(f"❌ Failed: {result.error_count} files")
            self.logger.info(f"📈 Success rate: {result.success_rate * 100:.1f}%")

            if result.errors:
                self.logger.error("❌ Errors:")
                for error in result.errors[:5]:
                    self.logger.error(f"  • {error}")

            # Show result dialog
            self.show_result(result)

        except Exception as e:
            self.show_error("実行エラー", f"Move operation failed: {str(e)}")
            self.logger.error(f"Move operation error: {e}")

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
            # Reset button states (メインスレッドで実行)
            self.parent.after(0, lambda: self.button_start.configure(state="normal"))
            self.parent.after(0, lambda: self.button_stop.configure(state="disabled"))

    def stop_move(self):
        """Move処理を停止"""
        if self.move_service:
            self.move_service.stop()
        self.progress_var.set("🛑 Stop requested...")
        self.button_stop.configure(state="disabled")

    def select_all_extensions(self):
        """すべての拡張子を選択"""
        for var in self.extension_vars.values():
            var.set(True)

    def deselect_all_extensions(self):
        """すべての拡張子の選択を解除"""
        for var in self.extension_vars.values():
            var.set(False)

    def get_selected_extensions(self):
        """選択された拡張子のリストを取得"""
        selected = []
        for ext, var in self.extension_vars.items():
            if var.get():
                selected.append(ext)
        return selected
