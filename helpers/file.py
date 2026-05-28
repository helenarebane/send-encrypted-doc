import argparse
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog


def valid_file(path_str, allowed_extensions=None):
    path = Path(path_str)
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"'{path_str}' is not a valid file.")
    if len(allowed_extensions) > 0 and path.suffix not in allowed_extensions:
        raise argparse.ArgumentTypeError(
            f"'{path_str}' is not a valid file type. Allowed extensions are {allowed_extensions}.")
    return path


def get_valid_file_path(cli_arg, allowed_extensions=None):
    path_str = cli_arg if cli_arg else get_file_via_gui()

    if not path_str:
        print("No file selected. Exiting.")
        sys.exit(0)

    try:
        return valid_file(path_str, allowed_extensions)
    except argparse.ArgumentTypeError as e:
        print(f"Validation Error: {e}")
        sys.exit(1)


def get_file_via_gui():
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.focus_force()
    root.update()

    file_path = tk.filedialog.askopenfilename(parent=root, title="Select a file")

    root.destroy()
    return file_path
