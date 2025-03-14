"""
Window management utilities for the Neon Virtual Keyboard
Handles getting active windows and managing focus
"""

import sys

# Import platform-specific modules
if sys.platform == 'win32':
    import win32gui
    import win32con


class WindowManager:
    """Manages window interactions with the operating system"""

    @staticmethod
    def get_active_window():
        """Get the currently active window (platform specific)"""
        if sys.platform == 'win32':
            return win32gui.GetForegroundWindow()
        else:
            # For non-Windows platforms, return None for now
            # TODO: Implement for other platforms
            return None

    @staticmethod
    def get_window_title(window_handle):
        """Get the title of a window from its handle"""
        if sys.platform == 'win32' and window_handle:
            try:
                return win32gui.GetWindowText(window_handle)
            except Exception:
                return "Unknown Window"
        return "None"

    @staticmethod
    def set_foreground_window(window_handle):
        """Set a window as the foreground window"""
        if sys.platform == 'win32' and window_handle:
            try:
                if win32gui.IsWindow(window_handle):
                    win32gui.SetForegroundWindow(window_handle)
                    return True
            except Exception:
                pass
        return False

    @staticmethod
    def apply_no_activate_style(window_id):
        """Apply the WS_EX_NOACTIVATE style to prevent window activation"""
        try:
            if sys.platform == 'win32':
                # Constants
                GWL_EXSTYLE = -20
                WS_EX_NOACTIVATE = 0x08000000  # Prevent window activation on click

                # Get window handle
                hwnd = int(window_id)

                # Get current extended window style
                ex_style = win32gui.GetWindowLong(hwnd, GWL_EXSTYLE)

                # Set the WS_EX_NOACTIVATE flag
                win32gui.SetWindowLong(hwnd, GWL_EXSTYLE, ex_style | WS_EX_NOACTIVATE)
                return True
        except Exception as e:
            print(f"Failed to set WS_EX_NOACTIVATE: {e}")
        return False