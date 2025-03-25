"""
Main window class for the Neon Virtual Keyboard
Handles the UI layout and interaction with the system
"""
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QPushButton,
                             QVBoxLayout, QHBoxLayout, QLabel, QFrame, QApplication)
from PyQt6.QtCore import (Qt, QTimer, QPoint, QAbstractNativeEventFilter, 
                         QPropertyAnimation, QEasingCurve, QRect, 
                         QAbstractAnimation, QSize)
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QPainter, QPen, QPainterPath, QColor, QKeySequence, QShortcut, QIcon
from ui.theme import NeonTheme
from ui.layouts import KeyboardLayoutManager
from utils.window_utils import WindowManager
import ctypes
from ui.key_buttons import NeonKeyButton, SpecialNeonKeyButton
from inference_engine import predict_next_word, complete_current_word

# WM_HOTKEY (value 0x0312) is a Windows message that the system sends when a registered hotkey is triggered.
# Applications that register hotkeys using RegisterHotKey() receive this message in their window procedure when the hotkey is pressed.
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
        self.modifier_status_label = None
        self.update_timer = None
        self.keyboard_manager = None
        self.status_label = None
        self.target_window_label = None
        self.target_window = None
        self.window_manager = WindowManager()
        self.theme = NeonTheme()

        # Initialize size variables with None to indicate they haven't been loaded yet
        self.initial_width = None
        self.initial_height = None
        self.original_size = None
        
        # Variables for window dragging
        self.dragging = False
        self.resizing = False
        self.resize_edge = None
        self.offset = QPoint()
        self.border_width = 5

        # Initialize audio Recording button
        self.audio_recording = None

        # Load settings first, before initializing UI
        self.load_window_settings()
        
        # If settings weren't loaded, use defaults
        if self.initial_width is None:
            self.initial_width = 900
            self.initial_height = 350


        # Setting up for Inference Models - Current Word Completion and Next Word Prediction
        self.current_prefix = ""
        self.current_context = []
        self.prediction_widgets = []

        # Initialize UI
        self.initUI()

        # Set up hotkey handling
        self.hotkey_id = 1
        self.event_filter = HotkeyFilter(self.hotkey_id, self.toggle_minimize)
        QApplication.instance().installNativeEventFilter(self.event_filter)

    def toggle_minimize(self):
        """Toggle between minimized and normal state"""
        print("Hotkey activated - toggle_minimize called")
        if self.isMinimized():
            self.showNormal()
            print("Window restored")
        else:
            self.showMinimized()
            print("Window minimized")

    def scale_buttons(self):
        """Scale all keyboard buttons according to the current window size"""
        # Calculate scale factor based on initial window size
        width_scale = self.width() / self.initial_width
        height_scale = self.height() / self.initial_height
        
        # Use the smaller scale to maintain aspect ratio
        scale_factor = min(width_scale, height_scale)
        
        # Find all NeonKeyButton and SpecialNeonKeyButton instances
        key_buttons = self.findChildren((NeonKeyButton, SpecialNeonKeyButton))
        
        # Scale each button
        for button in key_buttons:
            button.scale_size(scale_factor)

    def process_key_input(self, key_text):
        """Process keyboard input and update predictions accordingly

        Args:
            key_text: The text of the key that was pressed
        """
        if key_text == " ":
            # Space was pressed - if we have a prefix, add it to context
            if self.current_prefix:
                self.current_context.append(self.current_prefix)
                self.current_prefix = ""
            # Show next word predictions
            self.update_predictions(is_next_word=True, context=self.current_context)
        elif key_text == "\b":
            # Backspace was pressed
            if self.current_prefix:
                # Remove last character from prefix
                self.current_prefix = self.current_prefix[:-1]
                if self.current_prefix:
                    # If prefix still exists, update completion suggestions
                    self.update_predictions(is_next_word=False, context=self.current_context,
                                            prefix=self.current_prefix)
                else:
                    # If prefix is empty, show next word predictions
                    self.update_predictions(is_next_word=True, context=self.current_context)
            elif self.current_context:
                # If no prefix but context exists, remove last word from context
                # and set it as prefix for editing
                self.current_prefix = self.current_context.pop()
                self.update_predictions(is_next_word=False, context=self.current_context, prefix=self.current_prefix)
        elif key_text == "\n":
            # Enter was pressed - reset context
            self.current_context = []
            self.current_prefix = ""
            self.update_predictions(is_next_word=True, context=self.current_context)
        else:
            # Regular character input
            self.current_prefix += key_text
            # Update completion suggestions
            self.update_predictions(is_next_word=False, context=self.current_context, prefix=self.current_prefix)

    def add_prediction_area(self, parent_layout):
        """Create the prediction area with clickable prediction widgets"""
        # Container for status label and prediction widgets
        prediction_container = QWidget()
        prediction_layout = QVBoxLayout(prediction_container)
        prediction_layout.setContentsMargins(0, 0, 0, 0)
        prediction_layout.setSpacing(5)

        # Status label
        self.status_label = QLabel("Click keys to type (focus will be maintained on your Active window)")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(
            "color: #66ccff; margin-bottom: 3px; border: 1px solid #66ccff; border-radius: 8px; padding: 3px;")
        prediction_layout.addWidget(self.status_label)

        # Prediction widgets container
        prediction_widgets_container = QWidget()
        prediction_widgets_layout = QHBoxLayout(prediction_widgets_container)
        prediction_widgets_layout.setContentsMargins(0, 0, 0, 0)
        prediction_widgets_layout.setSpacing(5)

        # Create 5 clickable prediction widgets
        self.prediction_widgets = []
        for i in range(5):
            prediction_widget = QPushButton("prediction " + str(i + 1))
            prediction_widget.setStyleSheet("""
                QPushButton {
                    background-color: #2a2a2a;
                    color: #ffffff;
                    border: 1px solid #444444;
                    border-radius: 8px;
                    padding: 5px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #3a3a3a;
                    border: 1px solid #66ccff;
                }
                QPushButton:pressed {
                    background-color: #444444;
                }
            """)
            prediction_widget.setCursor(Qt.CursorShape.PointingHandCursor)
            prediction_widget.clicked.connect(lambda checked, idx=i: self.on_prediction_clicked(idx))
            prediction_widgets_layout.addWidget(prediction_widget)
            self.prediction_widgets.append(prediction_widget)

        prediction_layout.addWidget(prediction_widgets_container)
        parent_layout.addWidget(prediction_container)

    def on_prediction_clicked(self, index):
        """Handle prediction widget click"""
        # Get the selected prediction text
        if index >= len(self.prediction_widgets) or not self.prediction_widgets[index].isVisible():
            return

        prediction_text = self.prediction_widgets[index].text()
        if not prediction_text:
            return

        print(f"Selected prediction {index + 1}: {prediction_text}")

        # In a real implementation, this would insert the text into the active window
        # For example, using something like:
        # self.send_text_to_active_window(prediction_text)

        # Update context with the selected word
        if not self.current_prefix:
            # If we were showing next word predictions, add the word to context
            self.current_context.append(prediction_text)
            # Reset prefix and update predictions for the next word
            self.current_prefix = ""
            self.update_predictions(is_next_word=True, context=self.current_context)
        else:
            # If we were showing completions, replace the prefix with the full word
            # and add it to the context
            self.current_context.append(prediction_text)
            # Reset prefix and update predictions for the next word
            self.current_prefix = ""
            self.update_predictions(is_next_word=True, context=self.current_context)

    def update_predictions(self, is_next_word=True, context=None, prefix=""):
        """Update the prediction widgets with new predictions

        Args:
            is_next_word: If True, show next word predictions, otherwise show completions
            context: The context for prediction (previous words) as a list
            prefix: The prefix of the current word for completion
        """
        # Default empty context if None is provided
        if context is None:
            context = []
        import random

        # Random word generator function
        def generate_random_words(count=5):
            # Dictionary of 25 common words
            word_dict = [
                "apple", "blue", "cat", "dog", "easy",
                "fish", "green", "house", "ice", "jump",
                "king", "light", "moon", "night", "ocean",
                "play", "queen", "red", "star", "tree",
                "up", "violet", "water", "xray", "yellow"
            ]
            # Return 'count' number of random words
            return random.sample(word_dict, min(count, len(word_dict)))

        # Get predictions from inference engine
        try:
            if is_next_word:
                # Debugging: Print input parameters
                print(f"Calling predict_next_word with context: {context}, top_k: 5")

                # Get next word predictions
                predictions = predict_next_word(context, top_k=5)

                # Debugging: Print returned value
                print(f"predict_next_word returned: {predictions}")

                prediction_type = "Next word"
            else:
                # Debugging: Print input parameters
                print(f"Calling complete_current_word with prefix: {prefix}, context: {context}, top_k: 5")

                # Get word completion suggestions
                predictions = complete_current_word(prefix, context, top_k=5)

                # Debugging: Print returned value
                print(f"complete_current_word returned: {predictions}")

                prediction_type = "Completion"

            # Handle case where predictions might be None or empty
            if not predictions or predictions is None:
                print("No predictions returned, generating random words")
                predictions = generate_random_words(count=5)
                prediction_type += " (using random words)"

        except Exception as e:
            print(f"Error getting predictions: {e}")
            predictions = generate_random_words(count=5)  # Use random words on error too
            prediction_type = "Error in (using random words)"

        # At this point, predictions will always contain values:
        # - Either from the inference engine if successful
        # - Or random words if the inference failed or returned nothing
        # Update prediction widgets
        for i, widget in enumerate(self.prediction_widgets):
            if i < len(predictions):
                widget.setText(predictions[i])
                widget.setVisible(True)
            else:
                widget.setVisible(False)

        # Update status label with context info
        context_str = " ".join(context) if context else ""
        if is_next_word:
            self.status_label.setText(f"{prediction_type} suggestions after '{context_str}'")
        else:
            self.status_label.setText(f"{prediction_type} suggestions for '{prefix}' after '{context_str}'")


    def initUI(self):
        """Initialize the user interface"""
        # Set window properties
        self.setWindowTitle('Neon Virtual Keyboard')
        
        # Force the window size to match the loaded/default dimensions
        print(f"Setting window size to: {self.initial_width}x{self.initial_height}")
        self.resize(self.initial_width, self.initial_height)

        # Apply initial scaling to buttons
        self.scale_buttons()
        
        # Store original size for proportional scaling
        self.original_size = QSize(self.initial_width, self.initial_height)
        print(f"Original size set to: {self.original_size}")
        
        # Set window flags
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)

        # Set the window as a tool window
        if sys.platform == 'win32':
            self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # Apply theme and window manager settings
        self.theme.apply_to_window(self)
        self.window_manager.apply_no_activate_style(self)

        # Create main layout structure
        self.setup_layout()

        # Show the window
        self.show()

        # Set cursor
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def check_modifier_states(self):
        """Check the actual state of modifier keys and update UI if changed."""
        try:
            from utils.keyboard_utils import KeyboardController

            new_states = {
                'alt': (KeyboardController.is_key_pressed('left alt') or KeyboardController.is_key_pressed(
                    'right alt')),
                'ctrl': (KeyboardController.is_key_pressed('left ctrl') or KeyboardController.is_key_pressed(
                    'right ctrl')),
                'shift': (KeyboardController.is_key_pressed('left shift') or KeyboardController.is_key_pressed(
                    'right shift'))
            }

            if new_states != self.modifier_states:  # Only update if there's a change
                print("State changed, updating UI...")
                self.modifier_states = new_states
                self.update_modifier_status()

        except Exception as e:
            print(f"Error in check_modifier_states: {e}")
            import traceback
            traceback.print_exc()

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

        # Add prediction area
        self.add_prediction_area(main_layout)

        # Create keyboard frame with neon effect
        keyboard_frame = self.create_keyboard_frame()

        # Set a size policy that allows the frame to expand and maintain proportions
        keyboard_frame.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                     QtWidgets.QSizePolicy.Policy.Expanding)

        # Create keyboard layout manager and add the standard layout to the frame
        self.keyboard_manager = KeyboardLayoutManager()
        self.keyboard_manager.create_standard_layout(keyboard_frame)

        # Add keyboard to main layout
        main_layout.addWidget(keyboard_frame)

        # Add bottom status bar
        self.add_status_bar(main_layout)

        # Add timer for periodic updates - Updates the Current Active OSK Window Label.
        # And check for modifier key states - for UI info updating
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_current_window_label)
        self.update_timer.timeout.connect(self.check_modifier_states)
        self.update_timer.start(2000)  # Update every 2 seconds

        # Initial call (optional, since showEvent handles it)
        self.update_current_window_label()


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

    def add_title_bar(self, main_layout):
        """Add a custom title bar to the window"""
        title_bar = QFrame()
        title_bar.setMaximumHeight(30)
        title_bar.setStyleSheet("background-color: transparent; border: none;")

        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(5, 0, 5, 0)

        # Title
        title_label = QLabel("OSK-Symbiosis")
        title_label.setStyleSheet("color: #00aaff; font-weight: bold; font-size: 13px;")
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

    @staticmethod
    def create_keyboard_frame():
        """Create a frame for the keyboard with neon styling"""
        keyboard_frame = QFrame()
        keyboard_frame.setFrameShape(QFrame.Shape.StyledPanel)
        keyboard_frame.setFrameShadow(QFrame.Shadow.Raised)
        keyboard_frame.setStyleSheet("""
            QFrame {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2a2a2a, stop:1 #1a1a1a);
            border: 1px solid #0077cc;
            border-radius: 5px;
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
        self.modifier_status_label.setStyleSheet("color: #0099ff; font-size: 11px; font-weight: normal;")
        bottom_layout.addWidget(self.modifier_status_label)

        # bottom_layout.addStretch()

        from ui.audio_recording_functionality import add_audio_recording
        # Add the recording button instead of stretch
        add_audio_recording(self, bottom_layout)


        version_info = QLabel("v1.0.0")
        version_info.setStyleSheet("color: #0077cc; font-size: 12px;")
        bottom_layout.addWidget(version_info)

        main_layout.addWidget(bottom_frame)  # Fix typo: should be bottom_frame

    def update_status(self, key):
        """Update the status label with the pressed key"""
        self.status_label.setText(f"Key Pressed: {key}")
        # Reset status after 1 second
        QTimer.singleShot(1000,
                          lambda: self.status_label.setText("Click keys to type (focus maintained on Active window)"))

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
            self.target_window_label.setText(f"Current Window: {window_title}")
        else:
            self.target_window_label.setText("Current Window: None")

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

    def get_resize_edge(self, pos):
        """Determine if position is on a resize edge and which one"""
        x, y = pos.x(), pos.y()
        width, height = self.width(), self.height()

        # Check corners first (they take priority)
        if x <= self.border_width and y <= self.border_width:
            return "top-left"
        elif x >= width - self.border_width and y <= self.border_width:
            return "top-right"
        elif x <= self.border_width and y >= height - self.border_width:
            return "bottom-left"
        elif x >= width - self.border_width and y >= height - self.border_width:
            return "bottom-right"

        # Check edges
        elif x <= self.border_width:
            return "left"
        elif x >= width - self.border_width:
            return "right"
        elif y <= self.border_width:
            return "top"
        elif y >= height - self.border_width:
            return "bottom"

        return None

    def mousePressEvent(self, event):
        """Handle mouse press events for dragging and resizing the window"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if we're on a resize edge
            self.resize_edge = self.get_resize_edge(event.position().toPoint())

            if self.resize_edge:
                self.resizing = True
                self.offset = event.position().toPoint()
            else:
                # Store the initial position for dragging (moving) the window
                self.dragging = True
                self.offset = event.position().toPoint()

    def mouseMoveEvent(self, event):
        """Handle mouse move events for dragging and resizing the window"""

        print("Scaling from key_window.py")

        print(f"Current Width & Height: {self.width()}, {self.height()}")

        # Update cursor based on position
        resize_edge = self.get_resize_edge(event.position().toPoint())
        if resize_edge in ["left", "right"]:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif resize_edge in ["top", "bottom"]:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif resize_edge in ["top-left", "bottom-right"]:
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif resize_edge in ["top-right", "bottom-left"]:
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

        # Get current position
        current_pos = event.position().toPoint()

        # Handle resize operation
        if self.resizing and event.buttons() & Qt.MouseButton.LeftButton:
            # Throttle updates - only process every few pixels of movement
            if not hasattr(self, 'last_resize_pos') or (current_pos - self.last_resize_pos).manhattanLength() >= 5:
                self.last_resize_pos = current_pos

                # Apply easing to the movement
                diff = self.apply_easing(current_pos - self.offset)

                new_width = self.width()
                new_height = self.height()
                new_x = self.x()
                new_y = self.y()

                # Calculate new size based on resize direction
                if self.resize_edge in ["right", "top-right", "bottom-right"]:
                    new_width += diff.x()
                if self.resize_edge in ["bottom", "bottom-left", "bottom-right"]:
                    new_height += diff.y()
                if self.resize_edge in ["left", "top-left", "bottom-left"]:
                    new_width -= diff.x()
                    new_x += diff.x()
                if self.resize_edge in ["top", "top-left", "top-right"]:
                    new_height -= diff.y()
                    new_y += diff.y()

                # Enforce minimum size
                min_width, min_height = 400, 200
                if new_width < min_width:
                    if self.resize_edge in ["left", "top-left", "bottom-left"]:
                        new_x = self.x() + (self.width() - min_width)
                    new_width = min_width
                if new_height < min_height:
                    if self.resize_edge in ["top", "top-left", "top-right"]:
                        new_y = self.y() + (self.height() - min_height)
                    new_height = min_height

                # Use animation for smoother transitions
                if hasattr(self, 'animation') and self.animation.state() == QAbstractAnimation.State.Running:
                    self.animation.stop()

                # Create property animation for smooth transition
                self.animation = QPropertyAnimation(self, b"geometry")
                self.animation.setDuration(50)  # Short duration for responsiveness
                self.animation.setStartValue(self.geometry())
                self.animation.setEndValue(QRect(new_x, new_y, new_width, new_height))
                self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
                self.animation.start()

                # Update offset for continuous resize
                self.offset = current_pos

        # Handle dragging operation
        elif self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            # Throttle updates - only process every few pixels of movement
            if not hasattr(self, 'last_drag_pos') or (current_pos - self.last_drag_pos).manhattanLength() >= 5:
                self.last_drag_pos = current_pos

                # Apply easing to the movement
                new_pos = self.mapToGlobal(event.position().toPoint() - self.offset)

                # Use animation for smoother transitions
                if hasattr(self, 'drag_animation') and self.drag_animation.state() == QAbstractAnimation.State.Running:
                    self.drag_animation.stop()

                self.drag_animation = QPropertyAnimation(self, b"pos")
                self.drag_animation.setDuration(50)
                self.drag_animation.setStartValue(self.pos())
                self.drag_animation.setEndValue(new_pos)
                self.drag_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
                self.drag_animation.start()


    def apply_easing(self, diff):
        """Apply easing to mouse movements for smoother feel"""
        # Use QEasingCurve for smooth interpolation
        easing = QEasingCurve(QEasingCurve.Type.OutCubic)

        # Scale the input to 0-1 range for the easing function
        scale_factor_easing = 1.0  # Adjust this to control sensitivity

        # Apply easing separately to x and y components
        eased_x = diff.x() * easing.valueForProgress(min(1.0, abs(diff.x()) / scale_factor_easing))
        eased_y = diff.y() * easing.valueForProgress(min(1.0, abs(diff.y()) / scale_factor_easing))

        # Preserve original direction while applying easing
        return QPoint(int(eased_x), int(eased_y))



    def mouseReleaseEvent(self, event):
        """Handle mouse release events for dragging and resizing the window"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.dragging or self.resizing:
                # Save window settings after drag or resize
                self.save_window_settings()
            
            self.dragging = False
            self.resizing = False
            self.resize_edge = None

    def resizeEvent(self, event):
        """Handle window resize events to maintain proportions of UI elements"""
        super().resizeEvent(event)
        self.scale_buttons()
        


    def save_window_settings(self):
        """Save window position and size to a JSON file"""
        import json
        import os
        
        settings = {
            'position': {
                'x': self.x(),
                'y': self.y()
            },
            'size': {
                'width': self.width(),
                'height': self.height()
            },
            'default stable size': {
                'width': 761,
                'height': 317
            }
        }
        
        try:
            # Ensure the settings directory exists
            os.makedirs('settings', exist_ok=True)
            
            settings_path = 'settings/window_settings.json'
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=4)
                
            print(f"Window settings saved to: {os.path.abspath(settings_path)}")
            print(f"Settings: {settings}")
            
        except Exception as e:
            print(f"Error saving window settings: {e}")
            import traceback
            traceback.print_exc()

    def load_window_settings(self):
        """Load window position and size from JSON file"""
        import json
        import os
        
        settings_path = 'settings/window_settings.json'
        print(f"Attempting to load settings from: {os.path.abspath(settings_path)}")
        
        try:
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    
                    # Get screen geometry to ensure window appears on screen
                    screen = QApplication.primaryScreen().geometry()
                    
                    # Ensure coordinates are within screen bounds
                    x = min(max(settings['position']['x'], 0), screen.width() - 100)
                    y = min(max(settings['position']['y'], 0), screen.height() - 100)
                    width = min(settings['size']['width'], screen.width())
                    height = min(settings['size']['height'], screen.height())
                    
                    print(f"Loading window settings - x: {x}, y: {y}, width: {width}, height: {height}")
                    
                    # Store the dimensions
                    self.initial_width = width
                    self.initial_height = height
                    
                    # Set window geometry
                    self.setGeometry(x, y, width, height)
                    
                    return True
                
        except FileNotFoundError:
            print(f"Settings file not found at: {os.path.abspath(settings_path)}")
        except json.JSONDecodeError as e:
            print(f"Error decoding settings JSON: {e}")
        except Exception as e:
            print(f"Unexpected error loading settings: {e}")
            import traceback
            traceback.print_exc()
        
        print("Using default window settings")
        return False



    # # Not used from here onwards for now, handling presses in key_buttons.py
    #
    # def handle_key_press(self, key):
    #     """Handle a key press from the keyboard UI"""
    #     from utils.keyboard_utils import KeyboardController
    #
    #     if not self.toggle_modifier_key(key):
    #         # For non-modifier keys, do normal press and release
    #         KeyboardController.press_and_release_key(key)
    #         self.update_status(key)
