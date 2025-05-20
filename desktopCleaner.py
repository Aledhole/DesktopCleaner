from desktopOrganiser import folders_by_type, get_desktop_path

import shutil
import itertools
import threading

from tkinter import (
    Tk, Checkbutton, IntVar, Button, Label, messagebox,
    Listbox, Scrollbar, Toplevel, END, Entry, StringVar, Frame
)


def add_skip_extension():
    ext = current_extension.get().strip().lower()
    
    if ext and not ext.startswith("."):
        ext = "." + ext
    if ext and ext not in skip_extensions_list:
        skip_extensions_list.append(ext)
        skip_listbox.insert(END, ext)
    current_extension.set("")


def find_files_to_clean(folder_path, recursive=False, delete_temp=False, sort_by_type=False):
    files = folder_path.rglob("*") if recursive else folder_path.iterdir()
    selected_files = []    

    for file in files:
        if file.is_file():
            ext = file.suffix.lower()  

            if ext in skip_extensions_list:
                continue
            if file.name.startswith("."):
                continue

            if delete_temp and ext in [".log", ".tmp"]:
                selected_files.append(file)
            elif sort_by_type:
                selected_files.append(file)

    return selected_files

def run_cleanup():
    desktop_path = get_desktop_path()
    recursive = recursive_var.get()
    delete_temp = delete_temp_var.get()
    sort_by_type = sort_files_var.get()

    cleanup_status = Label(root, text="Cleaning in progress...", fg="blue")
    cleanup_status.pack()

    def do_cleanup():
        files_to_clean = find_files_to_clean(
            desktop_path,
            recursive,
            delete_temp,
            sort_by_type
        )
        
        if not files_to_clean:
            root.after(0, lambda: messagebox.showinfo("Nothing to clean", "No matching files found."))
            root.after(0, cleanup_status.destroy)
            return

        for file in files_to_clean:
            if sort_by_type:
                moved = False
                for folder_name, extensions in folders_by_type.items():
                    if file.suffix.lower() in extensions:
                        target_folder = desktop_path / folder_name
                        target_folder.mkdir(exist_ok=True)
                        try:
                            shutil.move(str(file), str(target_folder / file.name))
                            print(f"Moved: {file.name} → {folder_name}/")
                            moved = True
                            break
                        except Exception as e:
                            print(f"Failed to move {file.name}: {e}")
                if not moved:
                    print(f"Unsorted: {file.name}")
            elif delete_temp and file.suffix in [".log", ".tmp"]:
                try:
                    file.unlink()
                    print(f"Deleted: {file}")
                except Exception as e:
                    print(f"Failed: {file} — {e}")

        root.after(0, lambda: messagebox.showinfo("Done", "Cleanup complete."))
        root.after(0, cleanup_status.destroy)

    threading.Thread(target=do_cleanup, daemon=True).start()

def preview_cleanup():
    desktop_path = get_desktop_path()
    recursive = recursive_var.get()
    delete_temp = delete_temp_var.get()
    sort_by_type = sort_files_var.get()

    preview_win = Toplevel()
    preview_win.title("Preview Files to be Affected")
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
        files = find_files_to_clean(desktop_path, recursive, delete_temp, sort_by_type)

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

    animate_spinner()
    threading.Thread(target=scan_files, daemon=True).start()

# ---------------- UI --------------------
root = Tk()
root.title("Desktop Cleanup Tool")
root.geometry("600x600")


Label(root, text="Cleanup Desktop:").pack(pady=10)

recursive_var = IntVar()
delete_temp_var = IntVar()
sort_files_var = IntVar()

skip_extensions_list = []
current_extension = StringVar()

skip_extensions_var = StringVar()

Checkbutton(root, text="Include Subfolders", variable=recursive_var).pack(anchor="w", padx=20)
Checkbutton(root, text="Delete .log/.tmp files", variable=delete_temp_var).pack(anchor="w", padx=20)
Checkbutton(root, text="Move files into folders", variable=sort_files_var).pack(anchor="w", padx=20)

Button(root, text="Preview", command=preview_cleanup).pack(pady=10)
Button(root, text="Run Cleanup", command=run_cleanup).pack(pady=5)

Label(root, text="Skip extensions:").pack(pady=(10, 0))

entry_frame = Frame(root)
entry_frame.pack()

Entry(entry_frame, textvariable=current_extension, width=20).pack(side="left", padx=5)
Button(entry_frame, text="Add", command=add_skip_extension).pack(side="left")

skip_listbox = Listbox(root, height=4, width=30)
skip_listbox.pack(pady=(5, 10))

root.mainloop()
