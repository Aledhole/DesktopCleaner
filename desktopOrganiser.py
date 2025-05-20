from pathlib import Path
import os

def get_desktop_path():
    user_profile = Path(os.environ.get("USERPROFILE"))
    one_drive = user_profile / "OneDrive" / "Desktop"
    fallback = user_profile / "Desktop"
    return one_drive if one_drive.exists() else fallback
    
folders_by_type = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
    "Notes": [".pdf", ".docx", ".doc", ".txt", ".pptx", ".xlsx", ".xls"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv"],
    "Audio": [".mp3", ".wav", ".m4a", ".aac"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Executables": [".exe", ".msi", ".bat"],
    "Scripts": [".py", ".js", ".sh", ".rb"]
}