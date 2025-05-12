import os
import shutil
from pathlib import Path
import itertools
from tkinter import (Tk, Checkbutton, IntVar, Button, Label, messagebox, Listbox, Scrollbar, Toplevel, END)
import threading

def get_desktop_path():
    user_profile = Path(os.environ.get("USERPROFILE"))
    one_drive = user_profile / "OneDrive" / "Desktop"
    fallback = user_profile / "Desktop"
    return one_drive if one_drive.exists() else fallback

def find_files_to_clean(folder_path, recursive=False, delete_temp=False):
    files = folder_path.rglob("*") if recursive else folder_path.iterdir()
    selected_files = []

    for file in files:
        if file.is_file() and delete_temp and file.suffix in [".log", ".tmp"]:
            selected_files.append(file)

    return selected_files

def run_cleanup():
    desktop_path = get_desktop_path()
    recursive = recursive_var.get()
    delete_temp = delete_temp_var.get()

    cleanup_status = Label(root, text="Cleaning in progress...", fg="blue")
    cleanup_status.pack()

    def do_cleanup():
        files_to_delete = find_files_to_clean(desktop_path, recursive, delete_temp)

        if not files_to_delete:
            root.after(0, lambda: messagebox.showinfo("Nothing to clean", "No matching files found."))
            root.after(0, cleanup_status.destroy)
            return

        for file in files_to_delete:
            try:
                file.unlink()
                print(f"Deleted: {file}")
            except Exception as e:
                print(f"Failed: {file} — {e}")

        root.after(0, lambda: messagebox.showinfo("Done", f"Deleted {len(files_to_delete)} files."))
        root.after(0, cleanup_status.destroy)

    threading.Thread(target=do_cleanup, daemon=True).start()

def preview_cleanup():
    desktop_path = get_desktop_path()
    recursive = recursive_var.get()
    delete_temp = delete_temp_var.get()

    preview_win = Toplevel()
    preview_win.title("Preview Files to be Deleted")
    preview_win.geometry("500x400")

    label = Label(preview_win, text="Scanning files...")
    label.pack()

    listbox = Listbox(preview_win, width=80)
    scrollbar = Scrollbar(preview_win, command=listbox.yview)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    listbox.pack(fill="both", expand=True)

    spinner_cycle = itertools.cycle(["|", "/", "-", "\\"])
    preview_win.spinner_active = True

    def animate_spinner():
        if preview_win.spinner_active:
            label.config(text=f"Scanning files... {next(spinner_cycle)}")
            preview_win.after(100, animate_spinner)

    def scan_files():
        files = find_files_to_clean(desktop_path, recursive, delete_temp)

        def update_ui():
            listbox.delete(0, END)
            if not files:
                listbox.insert(END, "No matching files found.")
            else:
                for f in files:
                    listbox.insert(END, str(f))
            label.config(text=f"Found {len(files)} file(s)")
            preview_win.spinner_active = False

        preview_win.after(0, update_ui)

    # Start the animation and scanning thread
    animate_spinner()
    threading.Thread(target=scan_files, daemon=True).start()


# ----- UI -----
root = Tk()
root.title("Desktop Cleanup Tool")
root.geometry("320x250")

Label(root, text="Cleanup Desktop:").pack(pady=10)

recursive_var = IntVar()
delete_temp_var = IntVar()

Checkbutton(root, text="Include Subfolders", variable=recursive_var).pack(anchor="w", padx=20)
Checkbutton(root, text="Delete .log/.tmp files", variable=delete_temp_var).pack(anchor="w", padx=20)

Button(root, text="Preview", command=preview_cleanup).pack(pady=10)
Button(root, text="Run Cleanup", command=run_cleanup).pack(pady=5)

root.mainloop()
    
