"""
GUI タブの基底クラス
"""

import threading
from abc import ABC, abstractmethod
from typing import Any, Optional

import customtkinter as ctk


class BaseTab(ABC):
    """全てのタブの基底クラス"""

    def __init__(self, parent: ctk.CTkFrame, logger: Any):
        self.parent = parent
        self.logger = logger
        self.current_task: Optional[threading.Thread] = None

        # 共通ウィジェット
        self.progress_var = ctk.StringVar(value="待機中...")
        self.progress_bar = None

        self.setup_widgets()

    @abstractmethod
    def setup_widgets(self):
        """タブ固有のウィジェット設定（サブクラスで実装）"""

    @abstractmethod
    def execute(self):
        """タブの主要機能実行（サブクラスで実装）"""

    def setup_common_widgets(self):
        """共通ウィジェットの設定"""
        # 進捗表示
        self.progress_label = ctk.CTkLabel(
            self.parent, textvariable=self.progress_var, font=ctk.CTkFont(size=12)
        )
        self.progress_label.pack(pady=(0, 10))

        # 進捗バー
        self.progress_bar = ctk.CTkProgressBar(self.parent)
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 20))
        self.progress_bar.set(0)

    def update_progress(self, current: int, total: int, message: str = ""):
        """進捗更新の共通メソッド"""
        if total > 0:
            progress = current / total
            self.progress_bar.set(progress)

            if message:
                status = f"{message}: {current}/{total} ({progress * 100:.1f}%)"
            else:
                status = f"進捗: {current}/{total} ({progress * 100:.1f}%)"

            self.progress_var.set(status)

    def reset_ui(self):
        """UI状態をリセット"""
        self.progress_var.set("待機中...")
        if self.progress_bar:
            self.progress_bar.set(0)

    def show_error(self, title: str, message: str):
        """エラー表示の共通メソッド"""
        self.logger.error(f"{title}: {message}")
        # メインスレッドで実行されることを保証
        self.parent.after(
            0,
            lambda: ctk.CTkInputDialog(
                text=f"エラーが発生しました:\n{message}", title=title
            ),
        )

    def show_result(self, result: Any):
        """結果表示の共通メソッド"""
        if hasattr(result, "success_count") and hasattr(result, "error_count"):
            message = f"✅ 成功: {
                result.success_count} ファイル\n❌ 失敗: {
                result.error_count} ファイル"
            if hasattr(result, "success_rate"):
                message += f"\n📈 成功率: {result.success_rate * 100:.1f}%"
        else:
            message = "処理が完了しました"

        ctk.CTkInputDialog(text=message, title="実行結果")
