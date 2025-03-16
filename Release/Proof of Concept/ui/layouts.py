"""
Keyboard layout definitions for the Neon Virtual Keyboard
Provides methods to create different keyboard layouts
"""

from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QFrame
from PyQt6.QtCore import Qt

from ui.key_buttons import NeonKeyButton, SpecialNeonKeyButton


class KeyboardLayoutManager:
    """Manages keyboard layout creation and configuration"""

    def __init__(self):
        """Initialize the keyboard layout manager"""
        self.keyboard_frame = None
        self.layout = None
        self.row_layouts = []

    def create_keyboard(self, layout_type="standard", scale_factor=1.0):
        """
        Create a complete keyboard with the specified layout

        Args:
            layout_type (str): The type of layout ("standard", "compact", etc.)
            scale_factor (float): Scale factor for key sizing

        Returns:
            QFrame: The keyboard frame containing the layout
        """
        # Create the keyboard frame
        self.keyboard_frame = self.create_keyboard_frame()

        # Create the appropriate layout
        if layout_type.lower() == "standard":
            self.layout = self.create_standard_layout(self.keyboard_frame)
        # Add other layout types here as needed
        # elif layout_type.lower() == "compact":
        #     self.layout = self.create_compact_layout(self.keyboard_frame)
        else:
            # Default to standard layout
            self.layout = self.create_standard_layout(self.keyboard_frame)

        # Apply scaling if needed
        if scale_factor != 1.0:
            self.scale_layout(scale_factor)

        return self.keyboard_frame

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

    def create_standard_layout(self, parent_frame):
        """Create a standard QWERTY keyboard layout"""
        keyboard_layout = QVBoxLayout(parent_frame)
        keyboard_layout.setSpacing(8)
        keyboard_layout.setContentsMargins(10, 10, 10, 10)

        # Initialize row layouts list
        self.row_layouts = []

        # Add all keyboard rows
        row1 = self._add_function_row(keyboard_layout)
        row2 = self._add_number_row(keyboard_layout)
        row3 = self._add_qwerty_row(keyboard_layout)
        row4 = self._add_asdf_row(keyboard_layout)
        row5 = self._add_zxcv_row(keyboard_layout)
        row6 = self._add_control_row(keyboard_layout)

        # Store row layouts for scaling
        self.row_layouts.extend([row1, row2, row3, row4, row5, row6])

        return keyboard_layout

    def _add_function_row(self, layout):
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
            try:
                key_btn = NeonKeyButton(key_text, key_value)
                row_layout.addWidget(key_btn)
            except Exception as e:
                print(f"Error creating key {key_text}: {e}")

        layout.addLayout(row_layout)
        return row_layout

    def _add_number_row(self, layout):
        """Add number keys row to the layout"""
        row_layout = QHBoxLayout()
        row_layout.setSpacing(5)

        number_keys = [
            ("`", "`"), ("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"),
            ("5", "5"), ("6", "6"), ("7", "7"), ("8", "8"), ("9", "9"),
            ("0", "0"), ("-", "-"), ("=", "="), ("⌫", "backspace")
        ]

        for i, (key_text, key_value) in enumerate(number_keys):
            try:
                if key_text == "⌫":
                    key_btn = SpecialNeonKeyButton(key_text, key_value, 80)
                else:
                    key_btn = NeonKeyButton(key_text, key_value)
                row_layout.addWidget(key_btn)
            except Exception as e:
                print(f"Error creating key {key_text}: {e}")

        layout.addLayout(row_layout)
        return row_layout

    def _add_qwerty_row(self, layout):
        """Add QWERTY row to the layout"""
        row_layout = QHBoxLayout()
        row_layout.setSpacing(5)

        qwerty_keys = [
            ("Tab", "tab"), ("Q", "q"), ("W", "w"), ("E", "e"), ("R", "r"),
            ("T", "t"), ("Y", "y"), ("U", "u"), ("I", "i"), ("O", "o"),
            ("P", "p"), ("[", "["), ("]", "]"), ("\\", "\\")
        ]

        for i, (key_text, key_value) in enumerate(qwerty_keys):
            try:
                if key_text == "Tab":
                    key_btn = SpecialNeonKeyButton(key_text, key_value, 70)
                else:
                    key_btn = NeonKeyButton(key_text, key_value)
                row_layout.addWidget(key_btn)
            except Exception as e:
                print(f"Error creating key {key_text}: {e}")

        layout.addLayout(row_layout)
        return row_layout

    def _add_asdf_row(self, layout):
        """Add ASDF row to the layout"""
        row_layout = QHBoxLayout()
        row_layout.setSpacing(5)

        asdf_keys = [
            ("Caps", "caps lock"), ("A", "a"), ("S", "s"), ("D", "d"), ("F", "f"),
            ("G", "g"), ("H", "h"), ("J", "j"), ("K", "k"), ("L", "l"),
            (";", ";"), ("'", "'"), ("Enter", "enter")
        ]

        for i, (key_text, key_value) in enumerate(asdf_keys):
            try:
                if key_text in ["Caps", "Enter"]:
                    key_btn = SpecialNeonKeyButton(key_text, key_value, 80)
                else:
                    key_btn = NeonKeyButton(key_text, key_value)
                row_layout.addWidget(key_btn)
            except Exception as e:
                print(f"Error creating key {key_text}: {e}")

        layout.addLayout(row_layout)
        return row_layout

    def _add_zxcv_row(self, layout):
        """Add ZXCV row to the layout"""
        row_layout = QHBoxLayout()
        row_layout.setSpacing(5)

        zxcv_keys = [
            ("Shift", "left shift"), ("Z", "z"), ("X", "x"), ("C", "c"), ("V", "v"),
            ("B", "b"), ("N", "n"), ("M", "m"), (",", ","), (".", "."),
            ("/", "/"), ("Shift", "right shift")
        ]

        for key_text, key_value in zxcv_keys:
            try:
                if key_text == "Shift":
                    key_btn = SpecialNeonKeyButton(key_text, key_value, 90)
                else:
                    key_btn = NeonKeyButton(key_text, key_value)
                row_layout.addWidget(key_btn)
            except Exception as e:
                print(f"Error creating key {key_text}: {e}")

        layout.addLayout(row_layout)
        return row_layout

    def _add_control_row(self, layout):
        """Add control keys row to the layout"""
        row_layout = QHBoxLayout()
        row_layout.setSpacing(5)

        control_keys = [
            ("Ctrl", "left ctrl"), ("Win", "win"), ("Alt", "left alt"),
            ("Space", "space"),
            ("Alt", "right alt"), ("Fn", "fn"), ("Ctrl", "right ctrl")
        ]

        for key_text, key_value in control_keys:
            try:
                if key_text == "Space":
                    key_btn = SpecialNeonKeyButton(key_text, key_value, 350, 50)
                elif key_text in ["Ctrl", "Win", "Alt", "Fn"]:
                    key_btn = SpecialNeonKeyButton(key_text, key_value, 60, 50)
                else:
                    key_btn = NeonKeyButton(key_text, key_value)
                row_layout.addWidget(key_btn)
            except Exception as e:
                print(f"Error creating key {key_text}: {e}")

        layout.addLayout(row_layout)
        return row_layout

    def scale_layout(self, scale_factor):
        """Scale the spacing in the keyboard layout"""

        print("Scaling function entered in layous.py")

        # Scale the spacing between keys
        horizontal_spacing = max(2, int(5 * scale_factor))
        vertical_spacing = max(2, int(8 * scale_factor))

        self.layout.setSpacing(vertical_spacing)
        self.layout.setContentsMargins(
            horizontal_spacing,
            vertical_spacing,
            horizontal_spacing,
            vertical_spacing
        )

        # If you stored row layouts, you could iterate through them here
        if hasattr(self, 'row_layouts'):
            for row_layout in self.row_layouts:
                row_layout.setSpacing(int(5 * scale_factor))