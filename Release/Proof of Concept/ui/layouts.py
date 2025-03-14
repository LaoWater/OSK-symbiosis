"""
Keyboard layout definitions for the Neon Virtual Keyboard
Provides methods to create different keyboard layouts
"""

from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QFrame
from PyQt6.QtCore import Qt

from ui.key_buttons import NeonKeyButton, SpecialNeonKeyButton


class KeyboardLayoutManager:
    """Manages keyboard layout creation and configuration"""

    @staticmethod
    def create_keyboard_frame():
        """Create a styled frame for the keyboard"""
        keyboard_frame = QFrame()
        keyboard_frame.setFrameShape(QFrame.Shape.StyledPanel)
        keyboard_frame.setFrameShadow(QFrame.Shadow.Raised)
        keyboard_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #0077cc;
                border-radius: 10px;
            }
        """)
        return keyboard_frame

    @staticmethod
    def create_standard_layout(parent_frame):
        """Create a standard QWERTY keyboard layout"""
        keyboard_layout = QVBoxLayout(parent_frame)
        keyboard_layout.setSpacing(8)
        keyboard_layout.setContentsMargins(10, 10, 10, 10)

        # Add all keyboard rows
        KeyboardLayoutManager._add_function_row(keyboard_layout)
        KeyboardLayoutManager._add_number_row(keyboard_layout)
        KeyboardLayoutManager._add_qwerty_row(keyboard_layout)
        KeyboardLayoutManager._add_asdf_row(keyboard_layout)
        KeyboardLayoutManager._add_zxcv_row(keyboard_layout)
        KeyboardLayoutManager._add_control_row(keyboard_layout)

        return keyboard_layout

    @staticmethod
    def _add_function_row(layout):
        """Add function keys row to the layout"""
        row_layout = QHBoxLayout()
        row_layout.setSpacing(5)

        function_keys = [
            ("ESC", "esc"),
            ("F1", "f1"), ("F2", "f2"), ("F3", "f3"), ("F4", "f4"),
            ("F5", "f5"), ("F6", "f6"), ("F7", "f7"), ("F8", "f8"),
            ("F9", "f9"), ("F10", "f10"), ("F11", "f11"), ("F12", "f12")
        ]

        for key_text, key_value in function_keys:
            key_btn = NeonKeyButton(key_text, key_value)
            row_layout.addWidget(key_btn)

        layout.addLayout(row_layout)

    @staticmethod
    def _add_number_row(layout):
        """Add number keys row to the layout"""
        row_layout = QHBoxLayout()
        row_layout.setSpacing(5)

        number_keys = [
            ("`", "`"), ("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"),
            ("5", "5"), ("6", "6"), ("7", "7"), ("8", "8"), ("9", "9"),
            ("0", "0"), ("-", "-"), ("=", "="), ("⌫", "backspace")
        ]

        for i, (key_text, key_value) in enumerate(number_keys):
            if key_text == "⌫":
                key_btn = SpecialNeonKeyButton(key_text, key_value, 80)
            else:
                key_btn = NeonKeyButton(key_text, key_value)
            row_layout.addWidget(key_btn)

        layout.addLayout(row_layout)

    @staticmethod
    def _add_qwerty_row(layout):
        """Add QWERTY row to the layout"""
        row_layout = QHBoxLayout()
        row_layout.setSpacing(5)

        qwerty_keys = [
            ("Tab", "tab"), ("Q", "q"), ("W", "w"), ("E", "e"), ("R", "r"),
            ("T", "t"), ("Y", "y"), ("U", "u"), ("I", "i"), ("O", "o"),
            ("P", "p"), ("[", "["), ("]", "]"), ("\\", "\\")
        ]

        for i, (key_text, key_value) in enumerate(qwerty_keys):
            if key_text == "Tab":
                key_btn = SpecialNeonKeyButton(key_text, key_value, 70)
            else:
                key_btn = NeonKeyButton(key_text, key_value)
            row_layout.addWidget(key_btn)

        layout.addLayout(row_layout)

    @staticmethod
    def _add_asdf_row(layout):
        """Add ASDF row to the layout"""
        row_layout = QHBoxLayout()
        row_layout.setSpacing(5)

        asdf_keys = [
            ("Caps", "caps lock"), ("A", "a"), ("S", "s"), ("D", "d"), ("F", "f"),
            ("G", "g"), ("H", "h"), ("J", "j"), ("K", "k"), ("L", "l"),
            (";", ";"), ("'", "'"), ("Enter", "enter")
        ]

        for i, (key_text, key_value) in enumerate(asdf_keys):
            if key_text in ["Caps", "Enter"]:
                key_btn = SpecialNeonKeyButton(key_text, key_value, 80)
            else:
                key_btn = NeonKeyButton(key_text, key_value)
            row_layout.addWidget(key_btn)

        layout.addLayout(row_layout)

    @staticmethod
    def _add_zxcv_row(layout):
        """Add ZXCV row to the layout"""
        row_layout = QHBoxLayout()
        row_layout.setSpacing(5)

        zxcv_keys = [
            ("Shift", "shift"), ("Z", "z"), ("X", "x"), ("C", "c"), ("V", "v"),
            ("B", "b"), ("N", "n"), ("M", "m"), (",", ","), (".", "."),
            ("/", "/"), ("Shift", "shift")
        ]

        for i, (key_text, key_value) in enumerate(zxcv_keys):
            if key_text == "Shift":
                key_btn = SpecialNeonKeyButton(key_text, key_value, 90)
            else:
                key_btn = NeonKeyButton(key_text, key_value)
            row_layout.addWidget(key_btn)

        layout.addLayout(row_layout)

    @staticmethod
    def _add_control_row(layout):
        """Add control keys row to the layout"""
        row_layout = QHBoxLayout()
        row_layout.setSpacing(5)

        control_keys = [
            ("Ctrl", "ctrl"), ("Win", "win"), ("Alt", "alt"),
            ("Space", "space"),
            ("Alt", "alt"), ("Fn", "fn"), ("Ctrl", "ctrl")
        ]

        for i, (key_text, key_value) in enumerate(control_keys):
            if key_text == "Space":
                key_btn = SpecialNeonKeyButton(key_text, key_value, 350, 50)
            elif key_text in ["Ctrl", "Win", "Alt", "Fn"]:
                key_btn = SpecialNeonKeyButton(key_text, key_value, 60, 50)
            else:
                key_btn = NeonKeyButton(key_text, key_value)
            row_layout.addWidget(key_btn)

        layout.addLayout(row_layout)