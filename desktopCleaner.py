import os
import shutil
from pathlib import Path

def get_desktop_path():
    user_profile = Path(os.environ.get("USERPROFILE"))
    onedrive_desktop = user_profile / "OneDrive" / "Desktop"
    fallback_desktop = user_profile / "Desktop"
    return onedrive_desktop if onedrive_desktop.exists() else fallback_desktop

desktop = get_desktop_path()


# Folders and file types
folders = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
    "Notes": [".pdf", ".docx", ".doc", ".txt", ".pptx", ".xlsx", ".xls"],    
    "Videos": [".mp4", ".mov", ".avi", ".mkv"],
    "Audio": [".mp3", ".wav", ".m4a", ".aac"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Executables": [".exe", ".msi", ".bat"],
    "Scripts": [".py", ".js", ".sh", ".rb"],    
}

def create_folder(path):
    if not path.exists():
        path.mkdir()

def move_file(file, target_folder):
    try:
        shutil.move(str(file), str(target_folder / file.name))
    except shutil.Error:
        print(f"File already exists: {file.name}")

def clean_desktop():
    files = list(desktop.iterdir())
    if not files:
        print("No files found on the desktop.")
        return

    for file in files:
        if file.is_file():
            print(f"Found file: {file.name}")
            moved = False
            for folder_name, extensions in folders.items():
                if file.suffix.lower() in extensions:
                    target = desktop / folder_name
                    create_folder(target)
                    move_file(file, target)
                    moved = True
                    break            

if __name__ == "__main__":
    clean_desktop()
    print("Desktop cleanup complete.")
    
