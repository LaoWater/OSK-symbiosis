# Model Rating: 3.5/10
# GUI feeling nice
# (failed AI agentic system realization of the purpose of the program - to type KEYS in current window.)
# Second Iteration: Prompting specifically to ponder & integrate the main functionality and real world use.
#

import sys
import keyboard  # pip install keyboard
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QGridLayout
from PySide6.QtCore import Qt, QSize

class KeyButton(QPushButton):
    def __init__(self, label, parent=None):
        super().__init__(label, parent)
        self.key_label = label
        self.setFixedSize(QSize(60, 60))
        # Prevent focus so that the active app retains focus.
        self.setFocusPolicy(Qt.NoFocus)

    def mousePressEvent(self, event):
        # Determine the key to send.
        if self.key_label.lower() == "space":
            key_to_send = " "
        else:
            key_to_send = self.key_label.lower() if len(self.key_label) == 1 else self.key_label

        try:
            # Simulate a key press.
            keyboard.press_and_release(key_to_send)
        except Exception as e:
            print(f"Error sending key {self.key_label}: {e}")

        event.accept()

class KeyboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        grid = QGridLayout(self)
        grid.setSpacing(10)

        # Basic QWERTY layout.
        row1 = ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P']
        row2 = ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L']
        row3 = ['Z', 'X', 'C', 'V', 'B', 'N', 'M']

        # Add first row.
        for i, key in enumerate(row1):
            btn = KeyButton(key)
            grid.addWidget(btn, 0, i)

        # Second row offset by one.
        for i, key in enumerate(row2):
            btn = KeyButton(key)
            grid.addWidget(btn, 1, i + 1)

        # Third row offset by two.
        for i, key in enumerate(row3):
            btn = KeyButton(key)
            grid.addWidget(btn, 2, i + 2)

        # Space key spanning multiple columns.
        space_btn = KeyButton("Space")
        space_btn.setFixedSize(QSize(400, 60))
        grid.addWidget(space_btn, 3, 1, 1, 8)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Neon On-Screen Keyboard")
        self.setFixedSize(800, 400)
        self.init_ui()

    def init_ui(self):
        # Always on top and non-intrusive.
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setFocusPolicy(Qt.NoFocus)

        keyboard_widget = KeyboardWidget(self)
        keyboard_widget.setFocusPolicy(Qt.NoFocus)
        self.setCentralWidget(keyboard_widget)

        # Dark theme with neon blue accents.
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QWidget {
                background-color: #121212;
                color: #FFFFFF;
                font-family: Arial, sans-serif;
            }
            QPushButton {
                background-color: #1e1e1e;
                border: 2px solid #00AEEF;
                border-radius: 8px;
                font-size: 18px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #00AEEF;
                color: #121212;
            }
            QPushButton:pressed {
                background-color: #0088C9;
            }
        """)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Removed: app.setAttribute(Qt.AA_ShowWithoutActivating)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

