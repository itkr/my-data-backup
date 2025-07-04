#!/usr/bin/env python3
import tkinter as tk
import sys
import platform


def check_environment():
    print("=== Python Environment Check ===")
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Tkinter version: {tk.TkVersion}")
    print(f"Tcl version: {tk.TclVersion}")

    try:
        # 基本的なTkinterテスト
        root = tk.Tk()
        root.title("Environment Test")
        root.geometry("400x300")

        # 基本的なウィジェット
        tk.Label(root, text="Environment Test", font=("Arial", 16)).pack(pady=20)

        # Text ウィジェット
        text_widget = tk.Text(root, width=40, height=10, bg="white", fg="black")
        text_widget.pack(pady=10)

        # テキストを挿入してみる
        text_widget.insert("1.0", "This is a test\n")
        text_widget.insert(tk.END, "Second line\n")
        text_widget.insert(tk.END, "Third line\n")

        content = text_widget.get("1.0", tk.END)
        print(f"Text widget content: {repr(content)}")

        def test_insert():
            text_widget.insert(
                tk.END, f"Button clicked! Lines: {len(content.splitlines())}\n"
            )
            text_widget.see(tk.END)
            text_widget.update()

        tk.Button(root, text="Add Text", command=test_insert).pack(pady=5)

        def quit_app():
            print("Quitting...")
            root.quit()

        tk.Button(root, text="Quit", command=quit_app).pack(pady=5)

        print("Starting GUI...")
        root.mainloop()

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    check_environment()
