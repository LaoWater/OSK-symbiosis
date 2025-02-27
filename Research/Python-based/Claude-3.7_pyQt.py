# Model Rating: 4/10
# GUI feeling Really nice
# (failed AI agentic system realization of the purpose of the program - to type KEYS in current window.)


import sys
import keyboard
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                             QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, QTimer
from PyQt6.QtGui import QColor, QPalette, QFont, QFontDatabase, QCursor


class KeyButton(QPushButton):
    def __init__(self, key_text, key_value=None, width=50, height=50, parent=None):
        super().__init__(key_text, parent)
        self.key_text = key_text
        self.key_value = key_value if key_value is not None else key_text

        # Fixed string formatting by using normal string concatenation instead of .format()
        self.default_style = """
            QPushButton {
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #0077cc;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                min-width: """ + str(width) + """px;
                min-height: """ + str(height) + """px;
            }
        """

        self.hover_style = """
            QPushButton {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 2px solid #00aaff;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                min-width: """ + str(width) + """px;
                min-height: """ + str(height) + """px;
            }
        """

        self.pressed_style = """
            QPushButton {
                background-color: #003366;
                color: #ffffff;
                border: 2px solid #66ccff;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                min-width: """ + str(width) + """px;
                min-height: """ + str(height) + """px;
            }
        """

        self.setStyleSheet(self.default_style)
        self.setFixedSize(width, height)

        # Add glow animation effect
        self.animation = QPropertyAnimation(self, b"size")
        self.animation.setDuration(100)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def enterEvent(self, event):
        self.setStyleSheet(self.hover_style)
        cursor = QCursor(Qt.CursorShape.PointingHandCursor)
        QApplication.setOverrideCursor(cursor)
        self.animation.setStartValue(self.size())
        self.animation.setEndValue(QSize(self.width() + 4, self.height() + 4))
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self.default_style)
        QApplication.restoreOverrideCursor()
        self.animation.setStartValue(self.size())
        self.animation.setEndValue(QSize(self.width() - 4, self.height() - 4))
        self.animation.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setStyleSheet(self.pressed_style)
            keyboard.press(self.key_value)
            # Create temporary glow effect
            self.glow_timer = QTimer(self)
            self.glow_timer.setSingleShot(True)
            self.glow_timer.timeout.connect(self.remove_glow)
            self.glow_timer.start(200)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setStyleSheet(self.hover_style)
            keyboard.release(self.key_value)
        super().mouseReleaseEvent(event)

    def remove_glow(self):
        if self.underMouse():
            self.setStyleSheet(self.hover_style)
        else:
            self.setStyleSheet(self.default_style)


class SpecialKeyButton(KeyButton):
    def __init__(self, key_text, key_value=None, width=80, height=50, parent=None):
        super().__init__(key_text, key_value, width, height, parent)


class VirtualKeyboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Neon Virtual Keyboard')
        self.setGeometry(100, 100, 900, 350)

        # Set application font
        font_id = QFontDatabase.addApplicationFont(":/fonts/Hack-Regular.ttf")
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            font = QFont(font_families[0], 11)
            self.setFont(font)
        else:
            # Fallback to system monospace font
            font = QFont("Monospace", 11)
            self.setFont(font)

        # Set the dark theme with neon blue accents
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QLabel {
                color: #00aaff;
                font-size: 14px;
            }
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #0077cc;
                border-radius: 10px;
            }
        """)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Add title and status label
        title_label = QLabel("Neon Virtual Keyboard")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; color: #00aaff; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        self.status_label = QLabel("Click keys to type...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #66ccff; margin-bottom: 15px;")
        main_layout.addWidget(self.status_label)

        # Create keyboard frame
        keyboard_frame = QFrame()
        keyboard_frame.setFrameShape(QFrame.Shape.StyledPanel)
        keyboard_frame.setFrameShadow(QFrame.Shadow.Raised)
        keyboard_layout = QVBoxLayout(keyboard_frame)
        keyboard_layout.setSpacing(8)

        # Create keyboard rows
        # Row 1: Function keys
        function_row = QHBoxLayout()
        function_row.setSpacing(5)
        function_keys = [
            ("ESC", "esc"),
            ("F1", "f1"), ("F2", "f2"), ("F3", "f3"), ("F4", "f4"),
            ("F5", "f5"), ("F6", "f6"), ("F7", "f7"), ("F8", "f8"),
            ("F9", "f9"), ("F10", "f10"), ("F11", "f11"), ("F12", "f12")
        ]

        for key_text, key_value in function_keys:
            key_btn = KeyButton(key_text, key_value)
            function_row.addWidget(key_btn)

        keyboard_layout.addLayout(function_row)

        # Row 2: Number keys
        number_row = QHBoxLayout()
        number_row.setSpacing(5)
        number_keys = [
            ("`", "`"), ("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"),
            ("5", "5"), ("6", "6"), ("7", "7"), ("8", "8"), ("9", "9"),
            ("0", "0"), ("-", "-"), ("=", "="), ("⌫", "backspace")
        ]

        for i, (key_text, key_value) in enumerate(number_keys):
            if key_text == "⌫":
                key_btn = SpecialKeyButton(key_text, key_value, 80)
            else:
                key_btn = KeyButton(key_text, key_value)
            number_row.addWidget(key_btn)

        keyboard_layout.addLayout(number_row)

        # Row 3: QWERTY
        qwerty_row = QHBoxLayout()
        qwerty_row.setSpacing(5)
        qwerty_keys = [
            ("Tab", "tab"), ("Q", "q"), ("W", "w"), ("E", "e"), ("R", "r"),
            ("T", "t"), ("Y", "y"), ("U", "u"), ("I", "i"), ("O", "o"),
            ("P", "p"), ("[", "["), ("]", "]"), ("\\", "\\")
        ]

        for i, (key_text, key_value) in enumerate(qwerty_keys):
            if key_text == "Tab":
                key_btn = SpecialKeyButton(key_text, key_value, 70)
            else:
                key_btn = KeyButton(key_text, key_value)
            qwerty_row.addWidget(key_btn)

        keyboard_layout.addLayout(qwerty_row)

        # Row 4: ASDF
        asdf_row = QHBoxLayout()
        asdf_row.setSpacing(5)
        asdf_keys = [
            ("Caps", "caps lock"), ("A", "a"), ("S", "s"), ("D", "d"), ("F", "f"),
            ("G", "g"), ("H", "h"), ("J", "j"), ("K", "k"), ("L", "l"),
            (";", ";"), ("'", "'"), ("Enter", "enter")
        ]

        for i, (key_text, key_value) in enumerate(asdf_keys):
            if key_text in ["Caps", "Enter"]:
                key_btn = SpecialKeyButton(key_text, key_value, 80)
            else:
                key_btn = KeyButton(key_text, key_value)
            asdf_row.addWidget(key_btn)

        keyboard_layout.addLayout(asdf_row)

        # Row 5: ZXCV
        zxcv_row = QHBoxLayout()
        zxcv_row.setSpacing(5)
        zxcv_keys = [
            ("Shift", "shift"), ("Z", "z"), ("X", "x"), ("C", "c"), ("V", "v"),
            ("B", "b"), ("N", "n"), ("M", "m"), (",", ","), (".", "."),
            ("/", "/"), ("Shift", "shift")
        ]

        for i, (key_text, key_value) in enumerate(zxcv_keys):
            if key_text == "Shift":
                key_btn = SpecialKeyButton(key_text, key_value, 90)
            else:
                key_btn = KeyButton(key_text, key_value)
            zxcv_row.addWidget(key_btn)

        keyboard_layout.addLayout(zxcv_row)

        # Row 6: Control row
        control_row = QHBoxLayout()
        control_row.setSpacing(5)
        control_keys = [
            ("Ctrl", "ctrl"), ("Win", "win"), ("Alt", "alt"),
            ("Space", "space"),
            ("Alt", "alt"), ("Fn", "fn"), ("Ctrl", "ctrl")
        ]

        for i, (key_text, key_value) in enumerate(control_keys):
            if key_text == "Space":
                key_btn = SpecialKeyButton(key_text, key_value, 350, 50)
            elif key_text in ["Ctrl", "Win", "Alt", "Fn"]:
                key_btn = SpecialKeyButton(key_text, key_value, 60, 50)
            else:
                key_btn = KeyButton(key_text, key_value)
            control_row.addWidget(key_btn)

        keyboard_layout.addLayout(control_row)

        # Add keyboard to main layout
        main_layout.addWidget(keyboard_frame)

        # Add bottom status bar
        bottom_frame = QFrame()
        bottom_frame.setMaximumHeight(30)
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(10, 0, 10, 0)

        status_info = QLabel("Ready")
        status_info.setStyleSheet("color: #0099ff; font-size: 12px;")
        bottom_layout.addWidget(status_info)

        # Add spacer
        bottom_layout.addStretch()

        # Add version info
        version_info = QLabel("v1.0.0")
        version_info.setStyleSheet("color: #0077cc; font-size: 12px;")
        bottom_layout.addWidget(version_info)

        main_layout.addWidget(bottom_frame)

        self.show()

    def update_status(self, key):
        self.status_label.setText(f"Key Pressed: {key}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    keyboard_app = VirtualKeyboard()
    sys.exit(app.exec())


