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
        if self.hotkey.register(win32con.VK_SPACE, [win32con.MOD_CONTROL]):
            print("Global hotkey Ctrl+Space registered successfully")
            # Connect the hotkey signal to our toggle method
            self.hotkey.hotkey_triggered.connect(self.toggle_keyboard)
        else:
            print("Failed to register global hotkey")

        # Create the keyboard window
        self.keyboard = VirtualKeyboard()

    def toggle_keyboard(self):
        """Toggle the keyboard window between minimized and normal states"""
        if not self.keyboard:
            return

        print("Hotkey triggered! Toggling keyboard visibility")
        if self.keyboard.isMinimized():
            print("Restoring keyboard window")
            self.keyboard.showNormal()
        else:
            print("Minimizing keyboard window")
            self.keyboard.showMinimized()

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
