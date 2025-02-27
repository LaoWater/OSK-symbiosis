import sys
import pyautogui
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                             QGridLayout, QWidget, QSizePolicy)


# Custom KeyButton Class with Hover Animation
class KeyButton(QPushButton):
    def __init__(self, normal_char, shifted_char=None):
        super().__init__(normal_char)
        self.normal_char = normal_char
        self.shifted_char = shifted_char or self._get_shifted_char(normal_char)
        self.setFocusPolicy(Qt.NoFocus)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(QSize(40, 40))

        # Hover animation
        self.animation = QPropertyAnimation(self, b"color")
        self.animation.setDuration(200)
        self.default_color = QColor(127, 127, 127)
        self.hover_color = QColor(0, 255, 255)
        self._update_stylesheet(self.default_color)

    def _get_shifted_char(self, char):
        symbol_map = {
            '1': '!', '2': '@', '3': '#', '4': '$', '5': '%',
            '6': '^', '7': '&', '8': '*', '9': '(', '0': ')',
            '-': '_', '=': '+', '[': '{', ']': '}', '\\': '|',
            ';': ':', "'": '"', ',': '<', '.': '>', '/': '?'
        }
        return char.upper() if char.isalpha() else symbol_map.get(char, char)

    def enterEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self.default_color)
        self.animation.setEndValue(self.hover_color)
        self.animation.start()

    def leaveEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self.hover_color)
        self.animation.setEndValue(self.default_color)
        self.animation.start()

    def _update_stylesheet(self, color):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: #3a3a3a;
                color: rgb({color.red()}, {color.green()}, {color.blue()});
                border: 2px solid #00b4ff;
                border-radius: 5px;
                font-size: 14px;
                padding: 5px;
                margin: 2px;
            }}
            QPushButton:pressed {{
                background-color: #5a5a5a;
                border-color: #00ffff;
            }}
        """)

    def get_char(self, shift_active):
        return self.shifted_char if shift_active else self.normal_char


# Main Keyboard Window
class KeyboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.shift_active = False
        self.caps_lock = False
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Neon Keyboard")
        self.setFixedSize(800, 300)

        # Window configuration to stay on top and prevent focus
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)

        # Dark theme palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(43, 43, 43))
        self.setPalette(palette)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QGridLayout(central_widget)
        layout.setSpacing(3)
        layout.setContentsMargins(10, 10, 10, 10)

        # Keyboard layout
        rows = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '⌫'],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", '⏎'],
            ['⇧', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', '⇧'],
            ['␣']
        ]

        # Create keyboard layout
        for row_idx, row in enumerate(rows):
            col_span = {
                3: {0: 2, -1: 2},  # Shift keys
                4: {0: 12}  # Spacebar
            }

            col = 0
            for key in row:
                span = 1
                if row_idx in col_span and col in col_span[row_idx]:
                    span = col_span[row_idx][col]

                if key == '⇧':
                    btn = self.create_shift_button()
                elif key == '⏎':
                    btn = self.create_special_button('Enter', 'enter')
                elif key == '⌫':
                    btn = self.create_special_button('⌫', 'backspace')
                elif key == '␣':
                    btn = self.create_special_button('Space', 'space', 400)
                else:
                    btn = KeyButton(key)
                    btn.clicked.connect(self.create_key_handler(btn))

                layout.addWidget(btn, row_idx, col, 1, span)
                col += span

    def create_shift_button(self):
        btn = QPushButton('⇧')
        btn.setCheckable(True)
        btn.setFocusPolicy(Qt.NoFocus)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #004466;
                color: #00b4ff;
                border: 2px solid #00b4ff;
                border-radius: 5px;
                font-size: 14px;
                padding: 5px;
                margin: 2px;
            }
            QPushButton:checked {
                background-color: #006699;
                border-color: #00ffff;
            }
            QPushButton:pressed {
                background-color: #0088cc;
            }
        """)
        btn.clicked.connect(self.toggle_shift)
        return btn

    def create_special_button(self, text, key, width=None):
        btn = QPushButton(text)
        btn.setFocusPolicy(Qt.NoFocus)
        if width:
            btn.setFixedWidth(width)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #004466;
                color: #00b4ff;
                border: 2px solid #00b4ff;
                border-radius: 5px;
                font-size: 14px;
                padding: 5px;
                margin: 2px;
            }
            QPushButton:pressed {
                background-color: #006699;
            }
        """)
        btn.clicked.connect(lambda: pyautogui.press(key))
        return btn

    def create_key_handler(self, button):
        def handler():
            char = button.get_char(self.shift_active or self.caps_lock)
            pyautogui.write(char)

            # Handle shift behavior
            if self.shift_active and not self.caps_lock:
                self.shift_active = False
                self.update_shift_state()

        return handler

    def toggle_shift(self):
        self.shift_active = not self.shift_active
        self.update_shift_state()

    def update_shift_state(self):
        # Update shift buttons and key labels
        shift_btns = self.findChildren(QPushButton, '⇧')
        for btn in shift_btns:
            btn.setChecked(self.shift_active)

        for btn in self.findChildren(KeyButton):
            btn.setText(btn.get_char(self.shift_active))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KeyboardWindow()
    window.show()
    sys.exit(app.exec_())