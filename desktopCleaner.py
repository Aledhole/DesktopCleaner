import os
import shutil
from pathlib import Path
import itertools
from tkinter import (Tk, Checkbutton, IntVar, Button, Label, messagebox, Listbox, Scrollbar, Toplevel, END)

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

    files_to_delete = find_files_to_clean(desktop_path, recursive, delete_temp)

    if not files_to_delete:
        messagebox.showinfo("Nothing to clean", "No matching files found.")
        return

    confirm = messagebox.askyesno("Confirm", f"Delete {len(files_to_delete)} files?")
    if not confirm:
        return

    for file in files_to_delete:
        try:
            file.unlink()
            print(f"Deleted: {file}")
        except Exception as e:
            print(f"Failed: {file} — {e}")

    messagebox.showinfo("Done", f"Deleted {len(files_to_delete)} files.")

def preview_cleanup():
    desktop_path = get_desktop_path()
    recursive = recursive_var.get()
    delete_temp = delete_temp_var.get()

    preview_win = Toplevel()
    preview_win.title("Preview Files to be Deleted")
    preview_win.geometry("500x400")

    label = Label(preview_win, text="Loading preview...")
    label.pack()

    listbox = Listbox(preview_win, width=80)
    scrollbar = Scrollbar(preview_win, command=listbox.yview)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    listbox.pack(fill="both", expand=True)

    def load_files():
        files = find_files_to_clean(desktop_path, recursive, delete_temp)
        listbox.delete(0, END)

        if not files:
            listbox.insert(END, "No matching files found.")
        else:
            for f in files:
                listbox.insert(END, str(f))

        label.config(text=f"Found {len(files)} file(s)")

    preview_win.after(100, load_files)  # Schedule after UI loads


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
    
