#!/usr/bin/env python3
"""共通ログ機構のテストスクリプト"""

import tempfile
from pathlib import Path

from common.logger import (
    UnifiedLogger,
    create_console_logger,
    create_file_logger,
    create_logger,
)


def test_console_logger():
    """コンソールログのテスト"""
    print("=== Console Logger Test ===")
    logger = create_console_logger("test_console")

    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.success("This is a success message")
    logger.progress("This is a progress message")
    logger.separator()


def test_file_logger():
    """ファイルログのテスト"""
    print("\n=== File Logger Test ===")

    with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as tmp:
        log_file = tmp.name

    logger = create_file_logger("test_file", log_file)

    logger.start_operation("Test Operation", param1="value1", param2="value2")
    logger.info("Processing files...")
    logger.success("File processed successfully")
    logger.warning("Minor issue detected")
    logger.end_operation("Test Operation", success_count=5, error_count=1)

    print(f"Log file created: {log_file}")

    # ログファイルの内容を表示
    with open(log_file, "r", encoding="utf-8") as f:
        print("Log file contents:")
        print(f.read())

    # クリーンアップ
    Path(log_file).unlink()


def test_unified_logger():
    """統一ログのテスト"""
    print("\n=== Unified Logger Test ===")

    with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as tmp:
        log_file = tmp.name

    # コンソールとファイル両方に出力
    logger = UnifiedLogger("test_unified", log_file=log_file, console=True)

    logger.separator("*", 40)
    logger.info("Testing unified logger")
    logger.debug("This debug message won't appear (level is INFO)")
    logger.success("All tests passed!")
    logger.separator("*", 40)

    print(f"Log file created: {log_file}")

    # クリーンアップ
    Path(log_file).unlink()


if __name__ == "__main__":
    test_console_logger()
    test_file_logger()
    test_unified_logger()

    print("\n✅ All tests completed successfully!")
