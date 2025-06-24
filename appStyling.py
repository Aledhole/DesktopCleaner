from ttkbootstrap import Style
from tkinterdnd2 import TkinterDnD

class DnDWindow(TkinterDnD.Tk):
    def __init__(self, themename="darkly"):
        super().__init__()

        # Initialize ttkbootstrap style and apply theme
        self.style = Style()
        self.set_theme(themename)

    def set_theme(self, theme):
        """Set the current theme if valid."""
        try:
            self.style.theme_use(theme)
        except Exception as e:
            print(f"Theme '{theme}' failed to load. Error: {e}")

    def toggle_theme(self):
        """Toggle between dark and light themes."""
        current = self.style.theme.name
        new_theme = "flatly" if current == "darkly" else "darkly"
        self.set_theme(new_theme)