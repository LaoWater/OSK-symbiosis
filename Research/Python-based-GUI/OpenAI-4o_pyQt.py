# Model Rating: 3/10 - not working
# GUI feeling OK
# (failed AI agentic system realization of the purpose of the program - to type KEYS in current window.)
# Second Iteration: Prompting specifically to ponder & integrate the main functionality and real world use.
# Better but not sending keys
# Third Iteration: Focus is not lost, but key not sent. UI still highly rudimentary.

import sys
import win32gui
import win32con
import ctypes
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QSize, QTimer

# Win32 API for sending key presses
SendInput = ctypes.windll.user32.SendInput

PUL = ctypes.POINTER(ctypes.c_ulong)


class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]


# Function to send key press event
def press_key(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(hexKeyCode, 0, 0, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))


# Function to send key release event
def release_key(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(hexKeyCode, 0, 2, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))


# Standard QWERTY keyboard layout
KEYS = [
    [('Q', 0x51), ('W', 0x57), ('E', 0x45), ('R', 0x52), ('T', 0x54), ('Y', 0x59), ('U', 0x55), ('I', 0x49),
     ('O', 0x4F), ('P', 0x50)],
    [('A', 0x41), ('S', 0x53), ('D', 0x44), ('F', 0x46), ('G', 0x47), ('H', 0x48), ('J', 0x4A), ('K', 0x4B),
     ('L', 0x4C)],
    [('Z', 0x5A), ('X', 0x58), ('C', 0x43), ('V', 0x56), ('B', 0x42), ('N', 0x4E), ('M', 0x4D)],
    [('Space', 0x20)]
]


class OnScreenKeyboard(QWidget):
    def __init__(self):
        super().__init__()

        self.last_active_window = None
        self.setWindowTitle("Neon On-Screen Keyboard")
        self.setFixedSize(600, 300)

        # Keep the window on top and prevent focus stealing
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: #121212;")  # Dark theme

        # Timer to continuously track last active window
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_last_active_window)
        self.timer.start(500)  # Check every 500ms

        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()
        layout.setSpacing(10)

        # Create keyboard buttons
        for row_idx, row in enumerate(KEYS):
            for col_idx, (key, vk_code) in enumerate(row):
                btn = QPushButton(key)
                btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
                btn.setFixedSize(QSize(60, 60))
                btn.setStyleSheet(self.get_button_style())  # Apply styling

                btn.pressed.connect(lambda key=vk_code: self.send_keypress(key))  # Send key
                btn.released.connect(lambda key=vk_code: self.release_keypress(key))  # Release key

                layout.addWidget(btn, row_idx, col_idx)

        self.setLayout(layout)

    def get_button_style(self):
        return """
            QPushButton {
                background-color: #1E1E1E;
                border: 2px solid #00aaff;
                border-radius: 8px;
                color: white;
                font-size: 16px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #292929;
                border: 2px solid #33ccff;
            }
            QPushButton:pressed {
                background-color: #00aaff;
                border: 2px solid #005577;
            }
        """

    def update_last_active_window(self):
        """ Continuously store the last active window before interacting with OSK. """
        active_window = win32gui.GetForegroundWindow()

        # If OSK is not the active window, store it
        if active_window and active_window != int(self.winId()):
            self.last_active_window = active_window

    def send_keypress(self, vk_code):
        """ Send a simulated key press to the last active window. """
        if self.last_active_window:
            win32gui.SetForegroundWindow(self.last_active_window)  # Keep last active window in focus
        press_key(vk_code)

    def release_keypress(self, vk_code):
        """ Release the key after press. """
        release_key(vk_code)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    keyboard = OnScreenKeyboard()
    keyboard.show()
    sys.exit(app.exec())

