#!/usr/bin/env python3
import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


def main():
    # 最小限のテストGUI
    root = tk.Tk()
    root.title("RAW File Organizer - Minimal Test")
    root.geometry("600x400")

    # ラベル
    label = tk.Label(root, text="RAW File Organizer Tool", font=("Arial", 16, "bold"))
    label.pack(pady=20)

    # Labelで出力を表示（Textウィジェットの代わり）
    output_var = tk.StringVar()
    output_var.set("Ready - Click test button")
    output_label = tk.Label(
        root,
        textvariable=output_var,
        font=("Courier", 12),
        bg="white",
        fg="black",
        justify="left",
        anchor="nw",
        width=70,
        height=15,
        relief="sunken",
        bd=2,
    )
    output_label.pack(pady=10, padx=10, fill="both", expand=True)

    # 出力テキストを保持する変数
    output_lines = []

    def add_line(text):
        output_lines.append(text)
        # 最新の10行だけ表示
        display_lines = output_lines[-10:]
        output_var.set("\n".join(display_lines))
        root.update_idletasks()

    def test_function():
        add_line("TEST: Button clicked!")
        add_line("TEST: This should be visible")
        add_line(f"TEST: Time: {__import__('time').ctime()}")

    def clear_function():
        output_lines.clear()
        output_var.set("Cleared")

    # ボタンフレーム
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    tk.Button(
        button_frame, text="Test", command=test_function, bg="green", fg="white"
    ).pack(side="left", padx=5)
    tk.Button(
        button_frame, text="Clear", command=clear_function, bg="red", fg="white"
    ).pack(side="left", padx=5)

    # 初期メッセージ
    add_line("=== RAW File Organizer ===")
    add_line("This is a minimal test version")
    add_line("If you can see this, the display works!")

    print("Starting minimal GUI...")
    root.mainloop()


if __name__ == "__main__":
    main()
