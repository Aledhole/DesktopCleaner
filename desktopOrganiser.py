from pathlib import Path
import os

import json

CONFIG_FILE = "skip_config.json"

folders_by_type = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".pptx", ".xlsx", ".xls"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv"],
    "Audio": [".mp3", ".wav", ".m4a", ".aac"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Executables": [".exe", ".msi", ".bat"],
    "Scripts": [".py", ".js", ".sh", ".rb"]
}


def get_desktop_path():
    user_profile = Path(os.environ.get("USERPROFILE"))
    one_drive = user_profile / "OneDrive" / "Desktop"
    fallback = user_profile / "Desktop"
    return one_drive if one_drive.exists() else fallback



def load_skip_list(skip_extensions_list, skip_listbox, category_vars):
    try:
        with open("skip_config.json", "r") as f:
            data = json.load(f)

            # Load skips
            for ext in data.get("skips", []):
                if ext not in skip_extensions_list:
                    skip_extensions_list.append(ext)
                    skip_listbox.insert(END, ext)

            # Load categories
            saved_cats = data.get("categories", {})
            for cat, value in saved_cats.items():
                if cat in category_vars:
                    category_vars[cat].set(value)

    except Exception as e:
        print(f"Failed to load config: {e}")

def save_skip_list(skip_extensions_list, category_vars):
    try:
        data = {
            "skips": skip_extensions_list,
            "categories": {cat: var.get() for cat, var in category_vars.items()}
        }
        with open("skip_config.json", "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Failed to save skip list: {e}")


def add_skip_extension():
    ext = current_extension.get().strip().lower()
    
    if ext and not ext.startswith("."):
        ext = "." + ext
    if ext and ext not in skip_extensions_list:
        skip_extensions_list.append(ext)
        skip_listbox.insert(END, ext)
    current_extension.set("")

def remove_skip_extension():
    selected = skip_listbox.curselection()
    if selected:
        index = selected[0]
        ext = skip_listbox.get(index)
        skip_listbox.delete(index)
        skip_extensions_list.remove(ext)

def add_delete_extension():
    ext = delete_extension_input.get().strip().lower()
    if ext and not ext.startswith("."):
        ext = "." + ext
    if ext and ext not in delete_extensions_list:
        delete_extensions_list.append(ext)
        delete_listbox.insert(END, ext)
    delete_extension_input.set("")
