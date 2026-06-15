import sys
import os
import tkinter as tk

from excel_reader import read_excel
from hlsl_generator import generate_hlsl


def show_result_window(hlsl_text: str, source_name: str):
    root = tk.Tk()
    root.title(f"Generated HLSL - {source_name}")
    root.geometry("900x600")

    text = tk.Text(root, wrap=tk.NONE, font=("Consolas", 10))
    text.insert(tk.END, hlsl_text)
    text.config(state=tk.DISABLED)

    scrollbar_y = tk.Scrollbar(root, orient=tk.VERTICAL, command=text.yview)
    scrollbar_x = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=text.xview)
    text.config(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
    text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def copy_to_clipboard():
        root.clipboard_clear()
        root.clipboard_append(hlsl_text)
        btn.config(text="Copied!")
        root.after(1500, lambda: btn.config(text="Copy to Clipboard"))

    btn = tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard,
                    font=("Consolas", 11), padx=20, pady=6)
    btn.pack(side=tk.BOTTOM, pady=8)

    root.mainloop()


DEFAULT_EXCEL_NAME = "Config.xlsx"


def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def main():
    if len(sys.argv) >= 2:
        excel_path = sys.argv[1]
    else:
        excel_path = DEFAULT_EXCEL_NAME

    if not os.path.isabs(excel_path):
        excel_path = os.path.join(get_base_dir(), excel_path)

    if not os.path.exists(excel_path):
        print(f"Error: File not found: {excel_path}")
        input("Press Enter to exit...")
        sys.exit(1)

    try:
        config = read_excel(excel_path)
        hlsl_text = generate_hlsl(config)
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

    source_name = os.path.basename(excel_path)
    show_result_window(hlsl_text, source_name)


if __name__ == "__main__":
    main()
