# Windows APIs

import sys
import ctypes


class WindowManager:
    """Utility class for managing window interactions"""

    @staticmethod
    def get_active_window():
        """Get the currently active window handle"""
        if sys.platform == 'win32':
            try:
                return ctypes.windll.user32.GetForegroundWindow()
            except Exception:
                return None
        return None

    @staticmethod
    def get_window_title(hwnd):
        """Get the title of a window from its handle"""
        if sys.platform == 'win32' and hwnd:
            try:
                length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                buff = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
                return buff.value
            except Exception:
                return None
        return None

    @staticmethod
    def set_foreground_window(hwnd):
        """Set the foreground window to the specified handle"""
        if sys.platform == 'win32' and hwnd:
            try:
                ctypes.windll.user32.SetForegroundWindow(hwnd)
                return True
            except Exception:
                return False
        return False

    @staticmethod
    def is_window_valid(hwnd):
        """Check if a window handle is still valid"""
        if sys.platform == 'win32' and hwnd:
            try:
                return bool(ctypes.windll.user32.IsWindow(hwnd))
            except Exception:
                return False
        return False

    @staticmethod
    def apply_no_activate_style(window):
        """Apply the WS_EX_NOACTIVATE style to prevent the window from stealing focus"""
        if sys.platform == 'win32':
            try:
                hwnd = window.winId()

                # Define style constants
                WS_EX_NOACTIVATE = 0x08000000
                GWL_EXSTYLE = -20

                # Get current extended style
                exstyle = ctypes.windll.user32.GetWindowLongW(int(hwnd), GWL_EXSTYLE)

                # Add WS_EX_NOACTIVATE flag
                ctypes.windll.user32.SetWindowLongW(int(hwnd), GWL_EXSTYLE, exstyle | WS_EX_NOACTIVATE)

                return True
            except Exception as e:
                print(f"Failed to set WS_EX_NOACTIVATE: {e}")
                return False
        return False
