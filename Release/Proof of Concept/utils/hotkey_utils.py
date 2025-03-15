# utils/hotkey_utils.py
import sys
import ctypes
from ctypes import wintypes
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QCoreApplication
import win32con

# Windows constants
WM_HOTKEY = 0x0312


class GlobalHotkey(QObject):
    """Class for registering and handling global hotkeys in Windows"""

    # Signal emitted when the hotkey is triggered
    activated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.registered = False
        self.hotkey_id = 1  # ID for the hotkey registration
        self.thread = None

    def register(self, key, modifiers=None):
        """
        Register a global hotkey

        Args:
            key: Virtual key code (e.g., win32con.VK_K for 'K')
            modifiers: List of modifier keys (e.g., [win32con.MOD_CONTROL])
                       Default is None (no modifiers)

        Returns:
            bool: True if registration was successful, False otherwise
        """
        if sys.platform != 'win32':
            print("Global hotkeys are only supported on Windows")
            return False

        if self.registered:
            self.unregister()

        # Convert modifiers to single int value
        mod_value = 0
        if modifiers:
            for mod in modifiers:
                mod_value |= mod

        # Register the hotkey
        try:
            # Use main window handle for the hotkey registration
            parent_hwnd = int(self.parent().winId()) if self.parent() else None
            print(f"Using window handle: {parent_hwnd}")

            result = ctypes.windll.user32.RegisterHotKey(
                parent_hwnd,  # Use main window handle
                self.hotkey_id,  # Hotkey ID
                mod_value,  # Modifiers
                key  # Virtual key code
            )

            if result:
                print(f"Hotkey registered with ID: {self.hotkey_id}, modifiers: {mod_value}, key: {key}")
                self.registered = True

                # Use a method that hooks into the main event loop
                if parent_hwnd:
                    print("Using nativeEvent filter for hotkey detection")
                    # The parent window will handle the hotkey through nativeEvent
                    return True
                else:
                    # Start hotkey listener in a separate thread
                    print("Using thread-based hotkey detection")
                    self.thread = HotkeyListenerThread(self.hotkey_id)
                    self.thread.hotkey_triggered.connect(self.activated)
                    self.thread.start()
                    return True
            else:
                error_code = ctypes.windll.kernel32.GetLastError()
                print(f"Failed to register hotkey. Error code: {error_code}")
                return False

        except Exception as e:
            print(f"Error registering hotkey: {e}")
            return False

    def unregister(self):
        """Unregister the global hotkey"""
        if not self.registered:
            return True

        try:
            # Unregister the hotkey - use same window handle as during registration
            parent_hwnd = int(self.parent().winId()) if self.parent() else None
            result = ctypes.windll.user32.UnregisterHotKey(parent_hwnd, self.hotkey_id)

            # Stop the listener thread
            if self.thread:
                self.thread.stop()
                self.thread.wait()
                self.thread = None

            self.registered = False
            return bool(result)

        except Exception as e:
            print(f"Error unregistering hotkey: {e}")
            return False

    def __del__(self):
        """Clean up resources when object is destroyed"""
        self.unregister()


class HotkeyListenerThread(QThread):
    """Thread for listening to global hotkey events"""

    # Signal emitted when hotkey is triggered
    hotkey_triggered = pyqtSignal()

    def __init__(self, hotkey_id):
        super().__init__()
        self.hotkey_id = hotkey_id
        self.running = True

    def run(self):
        """Thread execution loop"""

        # Define message structure
        class MSG(ctypes.Structure):
            _fields_ = [
                ("hwnd", wintypes.HWND),
                ("message", wintypes.UINT),
                ("wParam", wintypes.WPARAM),
                ("lParam", wintypes.LPARAM),
                ("time", wintypes.DWORD),
                ("pt", wintypes.POINT),
            ]

        msg = MSG()

        print("Hotkey listener thread started")

        # Message loop to capture hotkey events
        while self.running:
            # Check for messages without blocking for too long
            if ctypes.windll.user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
                # Print message for debugging
                if msg.message == WM_HOTKEY:
                    print(f"WM_HOTKEY message received: wParam={msg.wParam}, lParam={msg.lParam}")

                # If it's our hotkey...
                if msg.message == WM_HOTKEY and msg.wParam == self.hotkey_id:
                    print(f"Our hotkey with ID {self.hotkey_id} was triggered!")
                    # Emit the signal
                    self.hotkey_triggered.emit()

                # Dispatch the message
                ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
                ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))

            # Sleep a bit to prevent high CPU usage
            self.msleep(10)

    def stop(self):
        """Stop the thread"""
        self.running = False
        print("Hotkey listener thread stopping")