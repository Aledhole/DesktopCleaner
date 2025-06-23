from desktopOrganiser import (
    folders_by_type, get_desktop_path, load_skip_list, save_skip_list, 
    add_skip_extension, remove_skip_extension, add_delete_extension
)
from tkinter import (
    Checkbutton, IntVar, Button, Label, messagebox,
    Listbox, Scrollbar, Toplevel, END, Entry, StringVar, Frame, filedialog,
    Menubutton, Menu
)
from appStyling import DnDWindow
import shutil
import itertools
import threading
import json
from pathlib import Path
import os

# ----- Core Logic -----

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

            if delete_temp and ext in delete_extensions_list:
                selected_files.append(file)
            elif sort_by_type:
                selected_files.append(file)

    return selected_files

def run_cleanup():
    folder_path = selected_folder if selected_folder else get_desktop_path()

    recursive = recursive_var.get()
    delete_temp = delete_temp_var.get()
    sort_by_type = sort_files_var.get()

    cleanup_status = Label(root, text="Cleaning in progress...", fg="blue")
    cleanup_status.pack()

    def do_cleanup():
        files_to_clean = find_files_to_clean(
            folder_path,
            recursive,
            delete_temp,
            sort_by_type
        )

        if not files_to_clean:
            root.after(0, lambda: messagebox.showinfo("Nothing to clean", "No matching files found."))
            root.after(0, cleanup_status.destroy)
            return

        moved_files = []
        for file in files_to_clean:
            if sort_by_type:
                moved = False
                for folder_name, extensions in folders_by_type.items():
                    if not category_vars[folder_name].get():
                        continue
                    if file.suffix.lower() in extensions:
                        target_folder = folder_path / folder_name
                        target_folder.mkdir(exist_ok=True)
                        try:
                            shutil.move(str(file), str(target_folder / file.name))
                            moved_files.append({"from": str(file), "to": str(target_folder / file.name)})
                            moved = True
                            break
                        except Exception as e:
                            print(f"Failed to move {file.name}: {e}")
                if not moved:
                    print(f"Unsorted: {file.name}")
            elif delete_temp and file.suffix.lower() in delete_extensions_list:
                try:
                    file.unlink()
                except Exception as e:
                    print(f"Failed: {file} — {e}")

        if moved_files:
            with open("undo_cleanup.json", "w") as undo_file:
                json.dump(moved_files, undo_file, indent=2)

        root.after(0, lambda: messagebox.showinfo("Done", "Cleanup complete."))
        root.after(0, cleanup_status.destroy)

    threading.Thread(target=do_cleanup, daemon=True).start()

def undo_last_cleanup():
    try:
        with open("undo_cleanup.json", "r") as f:
            moves = json.load(f)

        for entry in moves:
            to_path = Path(entry["to"])
            from_path = Path(entry["from"])

            if to_path.exists():
                to_path.rename(from_path)
            else:
                print(f"Missing: {to_path} (already moved or deleted)")

        os.remove("undo_cleanup.json")
        messagebox.showinfo("Undo Complete", "All moved files were restored.")
    except FileNotFoundError:
        messagebox.showwarning("Undo Failed", "No previous cleanup to undo.")
    except Exception as e:
        messagebox.showerror("Undo Error", str(e))

def preview_cleanup():
    folder_path = selected_folder if selected_folder else get_desktop_path()
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
        files = find_files_to_clean(folder_path, recursive, delete_temp, sort_by_type)

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

def choose_folder():
    global selected_folder
    path = filedialog.askdirectory()
    if path:
        selected_folder = Path(path)
        selected_folder_label.config(text=f"Selected Folder:\n{path}")

def on_close():
    save_skip_list(skip_extensions_list, category_vars)
    root.destroy()

# ----- UI Setup -----

root = DnDWindow(themename="darkly")
root.title("Desktop Cleanup Tool")
root.geometry("600x800")
root.protocol("WM_DELETE_WINDOW", on_close)

recursive_var = IntVar()
delete_temp_var = IntVar()
sort_files_var = IntVar()
skip_extensions_list = []
delete_extensions_list = [".log", ".tmp"]
delete_extension_input = StringVar()
current_extension = StringVar()
selected_folder = None
category_vars = {category: IntVar(value=1) for category in folders_by_type}

# --- Top Header ---
header_frame = Frame(root)
header_frame.pack(fill="x", pady=10, padx=10)
Button(header_frame, text="☀️", command=root.toggle_theme).pack(side="right")
Button(header_frame, text="Choose Folder", command=choose_folder).pack(side="left", padx=10)

# --- Menu for File Categories & Cleanup Options ---
menu_bar = Menu(root)
file_menu = Menu(menu_bar, tearoff=0)

for category, var in category_vars.items():
    file_menu.add_checkbutton(label=category, variable=var)

options_menu = Menu(menu_bar, tearoff=0)
options_menu.add_checkbutton(label="Include Subfolders", variable=recursive_var)
options_menu.add_checkbutton(label="Delete files", variable=delete_temp_var)
options_menu.add_checkbutton(label="Move files into folders", variable=sort_files_var)

menu_bar.add_cascade(label="File Categories ▾", menu=file_menu)
menu_bar.add_cascade(label="Cleanup Options ▾", menu=options_menu)
root.config(menu=menu_bar)

# --- Folder Path Display ---
folder_frame = Frame(root)
folder_frame.pack(pady=(5, 10))
selected_folder_label = Label(folder_frame, text="No folder selected. Default: Desktop")
selected_folder_label.pack()

# --- Buttons Section ---
button_frame = Frame(root)
button_frame.pack(pady=15)
Button(button_frame, text="Preview", width=20, command=preview_cleanup).pack(pady=2)
Button(button_frame, text="Run Cleanup", width=20, command=run_cleanup).pack(pady=2)
Button(button_frame, text="Undo Last Cleanup", width=20, command=undo_last_cleanup).pack(pady=2)

# --- Delete Extensions ---
Label(root, text="Extensions to Delete (dangerous):").pack()
delete_frame = Frame(root)
delete_frame.pack(pady=5)
Entry(delete_frame, textvariable=delete_extension_input, width=20).pack(side="left", padx=5)
Button(delete_frame, text="Add", command=add_delete_extension).pack(side="left")
delete_listbox = Listbox(root, height=4, width=40)
delete_listbox.pack(pady=5)
for ext in delete_extensions_list:
    delete_listbox.insert(END, ext)

# --- Skip Extensions ---
Label(root, text="Skip Extensions:").pack(pady=(10, 0))
skip_frame = Frame(root)
skip_frame.pack()
Entry(skip_frame, textvariable=current_extension, width=20).pack(side="left", padx=5)
Button(skip_frame, text="Add", command=add_skip_extension).pack(side="left")
skip_listbox = Listbox(root, height=4, width=40)
skip_listbox.pack(pady=5)
Button(root, text="Remove Selected", command=remove_skip_extension).pack(pady=(0, 10))

load_skip_list(skip_extensions_list, skip_listbox, category_vars)
root.mainloop()



