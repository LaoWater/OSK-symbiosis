"""
Main window class for the Neon Virtual Keyboard
Handles the UI layout and interaction with the system
"""
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QPushButton,
                             QVBoxLayout, QHBoxLayout, QLabel, QFrame, QApplication)
from PyQt6.QtCore import Qt, QTimer, QPoint, QAbstractNativeEventFilter
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QPainter, QPen, QPainterPath, QColor, QKeySequence, QShortcut
from ui.theme import NeonTheme
from ui.layouts import KeyboardLayoutManager
from utils.window_utils import WindowManager
import win32con  # Make sure to install pywin32 (pip install pywin32)
import ctypes


# Windows message constant
WM_HOTKEY = 0x0312


class HotkeyFilter(QAbstractNativeEventFilter):
    """Native event filter for handling global hotkeys"""

    def __init__(self, hotkey_id, callback):
        super().__init__()
        self.hotkey_id = hotkey_id
        self.callback = callback

    def nativeEventFilter(self, eventType, message):
        # Check if we're on Windows
        if sys.platform == 'win32':
            # Convert the message to a usable form
            msg = ctypes.wintypes.MSG.from_address(int(message))

            # Check if it's a hotkey message and matches our ID
            if msg.message == WM_HOTKEY and msg.wParam == self.hotkey_id:
                print(f"Hotkey detected in nativeEventFilter: {self.hotkey_id}")
                self.callback()
                return True, 0  # Event handled

        # Event not handled, pass it on
        return False, 0



class VirtualKeyboard(QMainWindow):
    """Main window for the virtual keyboard application"""

    def __init__(self):
        """Initialize the virtual keyboard window"""
        super().__init__()
        self.target_window = None
        self.window_manager = WindowManager()
        self.theme = NeonTheme()

        # Modifier keys state tracking
        self.modifier_states = {
            'alt': False,
            'ctrl': False,
            'shift': False
        }

        self.initUI()

        # Set up global hotkey for minimize/restore (Ctrl+K)
        self.hotkey_id = 1
        self.register_global_hotkey()

        # Install native event filter for hotkey handling
        self.event_filter = HotkeyFilter(self.hotkey_id, self.toggle_minimize)
        QApplication.instance().installNativeEventFilter(self.event_filter)

        # Variables for window dragging
        self.dragging = False
        self.offset = QPoint()

    def register_global_hotkey(self):
        """Register the global hotkey Ctrl+K"""
        if sys.platform != 'win32':
            return False

        # Register Ctrl+K globally
        try:
            # Get the main window handle
            hwnd = int(self.winId())

            # VK_K = 75 (ASCII code for 'K'), MOD_CONTROL = 2
            mod_value = win32con.MOD_CONTROL
            key_value = ord('K')  # Virtual key code for 'K'

            # Register the hotkey with Windows
            result = ctypes.windll.user32.RegisterHotKey(
                hwnd,  # Window handle
                self.hotkey_id,  # Hotkey ID (arbitrary unique ID)
                mod_value,  # Modifiers (MOD_CONTROL for Ctrl key)
                key_value  # Virtual key code
            )

            if result:
                print(f"Global hotkey Ctrl+K registered successfully with ID {self.hotkey_id}")
                return True
            else:
                error_code = ctypes.windll.kernel32.GetLastError()
                print(f"Failed to register hotkey. Error code: {error_code}")
                return False

        except Exception as e:
            print(f"Error registering hotkey: {e}")
            return False

    def toggle_minimize(self):
        """Toggle between minimized and normal state"""
        print("Hotkey activated - toggle_minimize called")
        if self.isMinimized():
            self.showNormal()
            print("Window restored")
        else:
            self.showMinimized()
            print("Window minimized")

    def initUI(self):
        """Initialize the user interface"""
        # Set window properties
        self.setWindowTitle('Neon Virtual Keyboard')
        self.setGeometry(100, 100, 900, 350)

        # Set window flags to stay on top and frameless
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)

        # Set the window as a tool window, so it doesn't show in taskbar and loses focus easily
        if sys.platform == 'win32':
            self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # Apply theme
        self.theme.apply_to_window(self)

        # Apply Windows-specific fix to prevent stealing focus
        self.window_manager.apply_no_activate_style(self)

        # Create main layout structure
        self.setup_layout()

        # Show the window
        self.show()

    def check_modifier_states(self):
        """Check the actual state of modifier keys and update UI if changed."""
        try:
            from utils.keyboard_utils import KeyboardController

            print("Checking modifier states...")  # Debugging print

            new_states = {
                'alt': (KeyboardController.is_key_pressed('left alt') or KeyboardController.is_key_pressed(
                    'right alt')),
                'ctrl': (KeyboardController.is_key_pressed('left ctrl') or KeyboardController.is_key_pressed(
                    'right ctrl')),
                'shift': (KeyboardController.is_key_pressed('left shift') or KeyboardController.is_key_pressed(
                    'right shift'))
            }

            print(f"New detected states: {new_states}")  # Debugging print
            print(f"Previous modifier states: {self.modifier_states}")  # Debugging print

            if new_states != self.modifier_states:  # Only update if there's a change
                print("State changed, updating UI...")
                self.modifier_states = new_states
                self.update_modifier_status()
            else:
                print("No change in modifier states.")

        except Exception as e:
            print(f"Error in check_modifier_states: {e}")
            import traceback
            traceback.print_exc()


    def setup_layout(self):
        """Create the main layout structure for the keyboard window"""
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

        # Create keyboard layout manager and add the standard layout to the frame
        self.keyboard_manager = KeyboardLayoutManager()
        self.keyboard_manager.create_standard_layout(keyboard_frame)

        # Add keyboard to main layout
        main_layout.addWidget(keyboard_frame)

        # Add bottom status bar
        self.add_status_bar(main_layout)

        # Add timer for periodic updates - Updates the Current Active OSK Window Label.
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_current_window_label)
        self.update_timer.timeout.connect(self.check_modifier_states)
        self.update_timer.start(2000)  # Update every 2 seconds

        # Initial call (optional, since showEvent handles it)
        self.update_current_window_label()

    def add_title_bar(self, main_layout):
        """Add a custom title bar to the window"""
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
        close_btn.clicked.connect(self.handle_exit)
        title_layout.addWidget(close_btn)

        main_layout.addWidget(title_bar)

    def handle_exit(self):
        """Handle application exit properly"""
        # Release any held modifier keys
        self.release_all_modifiers()
        # Quit the application
        sys.exit()

    def release_all_modifiers(self):
        """Release all modifier keys that might be in pressed state"""
        from utils.keyboard_utils import KeyboardController

        # Go through all modifiers and release them if they're currently pressed
        for mod_key, is_pressed in self.modifier_states.items():
            if is_pressed:
                KeyboardController.release_key(mod_key)
                self.modifier_states[mod_key] = False

    def create_keyboard_frame(self):
        """Create a frame for the keyboard with neon styling"""
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

    def add_status_bar(self, main_layout):
        """Add a status bar to display information at the bottom of the window"""
        bottom_frame = QFrame()
        bottom_frame.setMaximumHeight(30)
        bottom_frame.setStyleSheet("background-color: transparent; border: none;")
        bottom_layout = QHBoxLayout(bottom_frame)  # Fix typo: should be bottom_frame

        bottom_layout.setContentsMargins(10, 0, 10, 0)

        self.target_window_label = QLabel("Target: None")
        self.target_window_label.setStyleSheet("color: #0099ff; font-size: 12px;")
        bottom_layout.addWidget(self.target_window_label)

        self.modifier_states = {'alt': False, 'ctrl': False, 'shift': False}

        self.modifier_status_label = QLabel("ALT: Off | CTRL: Off | SHIFT: Off")
        self.modifier_status_label.setStyleSheet("color: #0099ff; font-size: 12px;")
        bottom_layout.addWidget(self.modifier_status_label)

        bottom_layout.addStretch()

        version_info = QLabel("v1.0.0")
        version_info.setStyleSheet("color: #0077cc; font-size: 12px;")
        bottom_layout.addWidget(version_info)

        main_layout.addWidget(bottom_frame)  # Fix typo: should be bottom_frame


    def toggle_modifier_key(self, key):
        """Toggle the state of a modifier key with error handling"""
        try:
            from utils.keyboard_utils import KeyboardController

            print(f"toggle_modifier_key called with key: {key}")

            key = key.lower()

            if not hasattr(self, 'modifier_states'):
                print("Creating modifier_states dictionary")
                self.modifier_states = {'alt': False, 'ctrl': False, 'shift': False}

            print(f"Current modifier_states: {self.modifier_states}")

            if key in self.modifier_states:
                new_state = not self.modifier_states[key]
                self.modifier_states[key] = new_state
                print(f"Set {key} to {new_state}")

                if new_state:
                    KeyboardController.press_key(key)
                    self.update_status(f"{key.upper()} locked")
                else:
                    KeyboardController.release_key(key)
                    self.update_status(f"{key.upper()} released")

                print("Calling update_modifier_status()")
                self.update_modifier_status()

                return True
            else:
                print(f"Key {key} not found in modifier_states: {self.modifier_states.keys()}")

            return False
        except Exception as e:
            print(f"Error in toggle_modifier_key: {e}")
            import traceback
            traceback.print_exc()
            return False


    def update_modifier_status(self):
        """Update the modifier status display"""
        try:
            alt_state = self.modifier_states.get('alt', False)
            ctrl_state = self.modifier_states.get('ctrl', False)
            shift_state = self.modifier_states.get('shift', False)

            print(f"update_modifier_status: alt={alt_state}, ctrl={ctrl_state}, shift={shift_state}")

            alt_status = "On" if alt_state else "Off"
            ctrl_status = "On" if ctrl_state else "Off"
            shift_status = "On" if shift_state else "Off"

            self.modifier_status_label.setText(f"ALT: {alt_status} | CTRL: {ctrl_status} | SHIFT: {shift_status}")
            print(f"Label text set to: {self.modifier_status_label.text()}")

            self.modifier_status_label.update()
            self.update()  # Ensure main window updates
        except Exception as e:
            print(f"Error in update_modifier_status: {e}")
            import traceback
            traceback.print_exc()


    def handle_key_press(self, key):
        """Handle a key press from the keyboard UI"""
        from utils.keyboard_utils import KeyboardController

        if not self.toggle_modifier_key(key):
            # For non-modifier keys, do normal press and release
            KeyboardController.press_and_release_key(key)
            self.update_status(key)


    def update_status(self, key):
        """Update the status label with the pressed key"""
        self.status_label.setText(f"Key Pressed: {key}")
        # Reset status after 1 second
        QTimer.singleShot(1000,
                          lambda: self.status_label.setText("Click keys to type (focus maintained on target window)"))

        # Ensure focus is maintained on target window
        self.restore_target_window_focus()

    def update_current_window_label(self):
        """Updates label with current active window information without storing it"""
        current_window = self.window_manager.get_active_window()
        window_title = self.window_manager.get_window_title(current_window)

        if current_window and window_title:
            # Truncate if too long
            if len(window_title) > 30:
                window_title = window_title[:27] + "..."
            self.target_window_label.setText(f"Current: {window_title}")
        else:
            self.target_window_label.setText("Current: None")

    def restore_target_window_focus(self):
        """Restore focus to the target window"""
        if self.target_window:
            # Check if window still exists and restore focus
            if self.window_manager.is_window_valid(self.target_window):
                self.window_manager.set_foreground_window(self.target_window)
            else:
                # Window no longer exists, clear target
                self.target_window = None
                self.target_window_label.setText("Target: None")

    def showEvent(self, event):
        """Called when the window is shown"""
        super().showEvent(event)

        # Optionally, can still update the label to show the current active window
        # if you want to display that information
        QTimer.singleShot(100, self.update_current_window_label)

    def closeEvent(self, event):
        """Handle window close event"""
        # Release any held modifier keys
        self.release_all_modifiers()

        # Unregister global hotkey
        if hasattr(self, 'hotkey'):
            self.hotkey.unregister()

        event.accept()

    def mousePressEvent(self, event):
        """Handle mouse press events for dragging the window"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Store the initial position for dragging
            self.dragging = True
            self.offset = event.position().toPoint()

    def mouseMoveEvent(self, event):
        """Handle mouse move events for dragging the window"""
        if self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            # Move the window when dragging
            new_pos = self.mapToGlobal(event.position().toPoint() - self.offset)
            self.move(new_pos)

    def mouseReleaseEvent(self, event):
        """Handle mouse release events for dragging the window"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False

    def paintEvent(self, event):
        """Custom paint event to draw neon effects"""
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
