import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from utils.direct_win32_hotkey import Win32Hotkey
import win32con
from ui.keyboard_window import VirtualKeyboard


class KeyboardApp(QApplication):
    """Main application class with global hotkey support"""

    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(True)
        self.keyboard = None

        # Set up global hotkey
        self.hotkey = Win32Hotkey()
        self.hotkey.register(win32con.VKqedg_SPACE, [win32con.MOD_CONTROL])


        # Create the keyboard window
        self.keyboard = VirtualKeyboard()


    def exec(self):
        """Override exec to ensure proper cleanup"""
        result = super().exec()

        # Clean up the hotkey before exiting
        if hasattr(self, 'hotkey'):
            self.hotkey.unregister()

        return result


if __name__ == "__main__":
    app = KeyboardApp(sys.argv)
    sys.exit(app.exec())
