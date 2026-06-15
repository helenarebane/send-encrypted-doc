import argparse
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

from helpers.format import print_yellow, print_red


def valid_file(path_str, allowed_extensions=None):
    path = Path(path_str)
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"'{path_str}' is not a valid file.")
    if allowed_extensions and path.suffix not in allowed_extensions:
        raise argparse.ArgumentTypeError(
            f"'{path_str}' is not a valid file type. Allowed extensions are {allowed_extensions}.")
    return path


def get_valid_file_path(cli_arg, allowed_extensions=None):
    path = Path(cli_arg) if cli_arg else get_file_via_gui()

    if not path:
        print_yellow("No file selected. Exiting.")
        sys.exit(0)

    try:
        return valid_file(path, allowed_extensions)
    except argparse.ArgumentTypeError as e:
        print_red(f"Validation Error: {e}")
        sys.exit(1)


def get_file_via_gui():
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.focus_force()
    root.update()

    file_path = tk.filedialog.askopenfilename(parent=root, title="Select a file")

    root.destroy()
    return Path(file_path) if file_path else None