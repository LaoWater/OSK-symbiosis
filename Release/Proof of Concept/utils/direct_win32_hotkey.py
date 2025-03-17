"""
Direct Win32 Hotkey Implementation using pywin32
Module handle Hotkey across all Windwos - Making it easy to Minimize/Maximize
"""

import sys
import win32con
import win32gui
import win32api
from PyQt6.QtCore import QTimer, QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

# Define hotkey ID
HOTKEY_ID = 1


class Win32Hotkey(QObject):
    """A class to handle global hotkeys using Win32 API via pywin32"""

    # Signal emitted when hotkey is triggered
    hotkey_triggered = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.registered = False
        self.msg_handler = None
        self.timer = None

    def register(self, key, modifiers=None):
        """Register a global hotkey

        Args:
            key: Virtual key code (e.g., ord('K') for 'K')
            modifiers: List of modifier values (e.g., [win32con.MOD_CONTROL])

        Returns:
            bool: True if registration was successful, False otherwise
        """
        if sys.platform != 'win32':
            print("Global hotkeys are only supported on Windows")
            return False

        # Convert modifiers to a single value
        mod_value = 0
        if modifiers:
            for mod in modifiers:
                mod_value |= mod

        # Create a hidden window to receive hotkey messages
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._wnd_proc
        wc.lpszClassName = "NeonOSKHotkeyWindow"

        try:
            # Register window class
            win32gui.RegisterClass(wc)

            # Create hidden window
            self.hwnd = win32gui.CreateWindow(
                wc.lpszClassName,
                "Hotkey Window",
                0, 0, 0, 0, 0,
                0, 0, 0, None
            )

            # Register the hotkey
            result = win32gui.RegisterHotKey(
                self.hwnd,
                HOTKEY_ID,
                mod_value,
                key
            )



        except Exception as e:
            print(f"Error setting up hotkey: {e}")
            return False


    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        """Window procedure to handle window messages"""
        if msg == win32con.WM_HOTKEY and wparam == HOTKEY_ID:
            print("Hotkey detected!")
            # We can't emit the signal directly here because this is called from a different thread
            # Instead, we'll set a flag that our timer will check
            self.msg_handler = True

        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)


    def unregister(self):
        """Unregister the global hotkey and clean up resources"""
        if not self.registered:
            return True

        try:
            # Stop the timer
            if self.timer:
                self.timer.stop()

            # Unregister the hotkey
            win32gui.UnregisterHotKey(self.hwnd, HOTKEY_ID)

            # Destroy the window
            win32gui.DestroyWindow(self.hwnd)

            # Unregister the window class
            win32gui.UnregisterClass("NeonOSKHotkeyWindow", None)

            self.registered = False
            return True

        except Exception as e:
            print(f"Error unregistering hotkey: {e}")
            return False


    def __del__(self):
        """Cleanup when object is destroyed"""
        self.unregister()

