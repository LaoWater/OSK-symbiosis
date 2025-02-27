# Model Rating: 4/10
# GUI feeling Really nice
# (failed AI agentic system realization of the purpose of the program - to type KEYS in current window.)
# Second Iteration: Prompting specifically to ponder & integrate the main functionality and real world use.
# Better but not sending keys
# Third Iteration: Generated Code doubled to 500 lines from the prompt engineered. Model starts to begin to grasp the problem's environment.
# UI greatly improved and beautifully feeling  - but fails to perform the main task of sending Keys to last active window - even tho window remains focused.
# Beautiful, beautiful UI, allowing drag from many points

import sys
import keyboard
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                             QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, QTimer, QPoint
from PyQt6.QtGui import QColor, QPalette, QFont, QFontDatabase, QCursor, QPainter, QPen, QBrush, QPainterPath, \
    QLinearGradient
import win32gui  # For capturing active window on Windows
import win32con


class NeonKeyButton(QPushButton):
    def __init__(self, key_text, key_value=None, width=50, height=50, parent=None):
        super().__init__(key_text, parent)
        self.key_text = key_text
        self.key_value = key_value if key_value is not None else key_text
        self.width = width
        self.height = height

        # Set focus policy to prevent focus stealing
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Fixed size for consistent layout
        self.setFixedSize(width, height)

        # Set styles
        self.setup_styles()

        # Initialize animations
        self.setup_animations()

    def setup_styles(self):
        self.default_style = f"""
            QPushButton {{
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #0077cc;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                min-width: {self.width}px;
                min-height: {self.height}px;
            }}
        """

        self.hover_style = f"""
            QPushButton {{
                background-color: #2a2a2a;
                color: #ffffff;
                border: 2px solid #00aaff;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                min-width: {self.width}px;
                min-height: {self.height}px;
            }}
        """

        self.pressed_style = f"""
            QPushButton {{
                background-color: #003366;
                color: #ffffff;
                border: 2px solid #66ccff;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                min-width: {self.width}px;
                min-height: {self.height}px;
            }}
        """

        self.setStyleSheet(self.default_style)

    def setup_animations(self):
        # Size animation for hover effect
        self.size_animation = QPropertyAnimation(self, b"size")
        self.size_animation.setDuration(100)
        self.size_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Glow intensity for custom painting
        self.glow_intensity = 0
        self.glow_animation = QTimer()
        self.glow_animation.timeout.connect(self.update_glow)

        # Pressed flag for painting
        self.is_pressed = False

    def update_glow(self):
        if self.is_pressed and self.glow_intensity < 100:
            self.glow_intensity += 10
        elif not self.is_pressed and self.glow_intensity > 0:
            self.glow_intensity -= 5

        if self.glow_intensity <= 0 and not self.is_pressed:
            self.glow_animation.stop()
            self.glow_intensity = 0

        self.update()  # Trigger repaint

    def enterEvent(self, event):
        self.setStyleSheet(self.hover_style)
        cursor = QCursor(Qt.CursorShape.PointingHandCursor)
        QApplication.setOverrideCursor(cursor)

        # Start size animation
        self.size_animation.setStartValue(self.size())
        self.size_animation.setEndValue(QSize(self.width + 4, self.height + 4))
        self.size_animation.start()

        # Start glow animation if not running
        if not self.glow_animation.isActive():
            self.glow_animation.start(30)  # Update every 30ms

        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self.default_style)
        QApplication.restoreOverrideCursor()

        # Shrink back to normal size
        self.size_animation.setStartValue(self.size())
        self.size_animation.setEndValue(QSize(self.width, self.height))
        self.size_animation.start()

        # Let glow animation fade out
        self.is_pressed = False

        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setStyleSheet(self.pressed_style)
            self.is_pressed = True

            # Notify parent to handle key press
            self.parent().parent().parent().parent().handle_key_press(self.key_value)

            # Don't call super() to prevent focus change
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Restore hover style if mouse is still over the button
            if self.underMouse():
                self.setStyleSheet(self.hover_style)
            else:
                self.setStyleSheet(self.default_style)

            # Notify parent to handle key release
            self.parent().parent().parent().parent().handle_key_release(self.key_value)
            self.is_pressed = False

            # Don't call super() to prevent focus change
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        # Call the parent class paint event to draw the button
        super().paintEvent(event)

        # Add custom neon effect if glowing
        if self.glow_intensity > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Draw outer glow
            pen = QPen(QColor(0, 170, 255, self.glow_intensity))
            pen.setWidth(2)
            painter.setPen(pen)

            # Create rounded rectangle path
            path = QPainterPath()
            path.addRoundedRect(2, 2, self.width - 4, self.height - 4, 5, 5)
            painter.drawPath(path)

            # Draw bottom neon line
            gradient = QLinearGradient(0, self.height - 3, self.width, self.height - 3)
            gradient.setColorAt(0, QColor(0, 170, 255, 0))
            gradient.setColorAt(0.5, QColor(0, 170, 255, self.glow_intensity * 2))
            gradient.setColorAt(1, QColor(0, 170, 255, 0))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(gradient))
            painter.drawRect(0, self.height - 3, self.width, 2)


class SpecialNeonKeyButton(NeonKeyButton):
    def __init__(self, key_text, key_value=None, width=80, height=50, parent=None):
        super().__init__(key_text, key_value, width, height, parent)


class VirtualKeyboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.target_window = None
        self.initUI()

    def initUI(self):
        # Set window properties
        self.setWindowTitle('Neon Virtual Keyboard')
        self.setGeometry(100, 100, 900, 350)

        # Set window flags to stay on top and frameless
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)

        # Set the window as a tool window so it doesn't show in taskbar and loses focus easily
        if sys.platform == 'win32':
            self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # Set font
        self.setup_font()

        # Set up the theme
        self.setup_theme()

        # Create main layout structure
        self.setup_layout()

        # Show the window
        self.show()

        # Variables for window dragging
        self.dragging = False
        self.offset = QPoint()

    def setup_font(self):
        # Try to load a custom font, or fall back to system font
        font_id = QFontDatabase.addApplicationFont(":/fonts/Hack-Regular.ttf")
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            font = QFont(font_families[0], 11)
        else:
            # Fallback to system monospace font
            font = QFont("Monospace", 11)

        self.setFont(font)

    def setup_theme(self):
        # Set the dark theme with neon blue accents
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
                border: 1px solid #0077cc;
                border-radius: 10px;
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
            QPushButton#titleButton {
                background-color: transparent;
                color: #00aaff;
                border: none;
                font-size: 16px;
            }
            QPushButton#titleButton:hover {
                color: #33ccff;
            }
            QPushButton#minimizeButton {
                background-color: transparent;
                color: #cccccc;
                border: none;
                font-size: 16px;
            }
            QPushButton#minimizeButton:hover {
                color: white;
                background-color: #444444;
            }
            QPushButton#closeButton {
                background-color: transparent;
                color: #cccccc;
                border: none;
                font-size: 16px;
            }
            QPushButton#closeButton:hover {
                color: white;
                background-color: #cc0000;
            }
        """)

    def setup_layout(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # Add custom title bar
        self.add_title_bar(main_layout)

        # Add status label
        self.status_label = QLabel("Click keys to type (focus will be maintained on your target window)")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #66ccff; margin-bottom: 15px;")
        main_layout.addWidget(self.status_label)

        # Create keyboard frame with neon effect
        keyboard_frame = self.create_keyboard_frame()
        keyboard_layout = QVBoxLayout(keyboard_frame)
        keyboard_layout.setSpacing(8)
        keyboard_layout.setContentsMargins(10, 10, 10, 10)

        # Create keyboard rows
        self.create_keyboard_layout(keyboard_layout)

        # Add keyboard to main layout
        main_layout.addWidget(keyboard_frame)

        # Add bottom status bar
        self.add_status_bar(main_layout)

    def add_title_bar(self, main_layout):
        title_bar = QFrame()
        title_bar.setMaximumHeight(30)
        title_bar.setStyleSheet("background-color: transparent; border: none;")

        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(5, 0, 5, 0)

        # Title
        title_label = QLabel("Neon OSK")
        title_label.setStyleSheet("color: #00aaff; font-weight: bold; font-size: 16px;")
        title_layout.addWidget(title_label)

        # Spacer
        title_layout.addStretch()

        # Minimize button
        minimize_btn = QPushButton("—")
        minimize_btn.setObjectName("minimizeButton")
        minimize_btn.setFixedSize(30, 25)
        minimize_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        minimize_btn.clicked.connect(self.showMinimized)
        title_layout.addWidget(minimize_btn)

        # Close button
        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeButton")
        close_btn.setFixedSize(30, 25)
        close_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(close_btn)

        main_layout.addWidget(title_bar)

    def create_keyboard_frame(self):
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

    def create_keyboard_layout(self, keyboard_layout):
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
            key_btn = NeonKeyButton(key_text, key_value)
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
                key_btn = SpecialNeonKeyButton(key_text, key_value, 80)
            else:
                key_btn = NeonKeyButton(key_text, key_value)
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
                key_btn = SpecialNeonKeyButton(key_text, key_value, 70)
            else:
                key_btn = NeonKeyButton(key_text, key_value)
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
                key_btn = SpecialNeonKeyButton(key_text, key_value, 80)
            else:
                key_btn = NeonKeyButton(key_text, key_value)
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
                key_btn = SpecialNeonKeyButton(key_text, key_value, 90)
            else:
                key_btn = NeonKeyButton(key_text, key_value)
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
                key_btn = SpecialNeonKeyButton(key_text, key_value, 350, 50)
            elif key_text in ["Ctrl", "Win", "Alt", "Fn"]:
                key_btn = SpecialNeonKeyButton(key_text, key_value, 60, 50)
            else:
                key_btn = NeonKeyButton(key_text, key_value)
            control_row.addWidget(key_btn)

        keyboard_layout.addLayout(control_row)

    def add_status_bar(self, main_layout):
        bottom_frame = QFrame()
        bottom_frame.setMaximumHeight(30)
        bottom_frame.setStyleSheet("background-color: transparent; border: none;")
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(10, 0, 10, 0)

        # Add target window display
        self.target_window_label = QLabel("Target: None")
        self.target_window_label.setStyleSheet("color: #0099ff; font-size: 12px;")
        bottom_layout.addWidget(self.target_window_label)

        # Add spacer
        bottom_layout.addStretch()

        # Add version info
        version_info = QLabel("v1.2.0")
        version_info.setStyleSheet("color: #0077cc; font-size: 12px;")
        bottom_layout.addWidget(version_info)

        main_layout.addWidget(bottom_frame)

    def update_status(self, key):
        self.status_label.setText(f"Key Pressed: {key}")
        # Reset status after 1 second
        QTimer.singleShot(1000,
                          lambda: self.status_label.setText("Click keys to type (focus maintained on target window)"))

    def get_active_window(self):
        """Get the currently active window (platform specific)"""
        if sys.platform == 'win32':
            return win32gui.GetForegroundWindow()
        else:
            # For non-Windows platforms, return None for now
            # Would need to implement X11/Wayland or macOS specific code here
            return None

    def store_target_window(self):
        """Store the target window before showing the keyboard"""
        self.target_window = self.get_active_window()
        if self.target_window:
            window_title = win32gui.GetWindowText(self.target_window)
            if window_title:
                # Truncate if too long
                if len(window_title) > 30:
                    window_title = window_title[:27] + "..."
                self.target_window_label.setText(f"Target: {window_title}")
            else:
                self.target_window_label.setText("Target: Unknown Window")
        else:
            self.target_window_label.setText("Target: None")

    def handle_key_press(self, key):
        """Handle key press without stealing focus"""
        self.update_status(key)

        # If we have a target window, restore focus to it before sending the key
        self.restore_target_window_focus()

        # Simulate the key press
        keyboard.press(key)

    def handle_key_release(self, key):
        """Handle key release without stealing focus"""
        # Simulate the key release
        keyboard.release(key)

        # Make sure focus stays on the target window
        self.restore_target_window_focus()

    def restore_target_window_focus(self):
        """Restore focus to the target window"""
        if sys.platform == 'win32' and self.target_window:
            # Check if window still exists
            if win32gui.IsWindow(self.target_window):
                # Set the target window as the foreground window
                win32gui.SetForegroundWindow(self.target_window)
            else:
                # Window no longer exists, clear target
                self.target_window = None
                self.target_window_label.setText("Target: None")

    def showEvent(self, event):
        """Called when the window is shown"""
        super().showEvent(event)
        # Store the active window before we take focus
        QTimer.singleShot(100, self.store_target_window)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Store the initial position for dragging
            self.dragging = True
            self.offset = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            # Move the window when dragging
            new_pos = self.mapToGlobal(event.position().toPoint() - self.offset)
            self.move(new_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False

    def paintEvent(self, event):
        # Add a custom border glow effect to the main window
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw outer neon border
        pen = QPen(QColor(0, 170, 255, 60))
        pen.setWidth(2)
        painter.setPen(pen)

        # Create rounded rectangle for the main window
        path = QPainterPath()
        path.addRoundedRect(1, 1, self.width() - 2, self.height() - 2, 10, 10)
        painter.drawPath(path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    keyboard_app = VirtualKeyboard()
    sys.exit(app.exec())