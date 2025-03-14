"""
Main window class for the Neon Virtual Keyboard
Handles the UI layout and interaction with the system
"""
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QPushButton,
                             QVBoxLayout, QHBoxLayout, QLabel, QFrame)
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPainter, QPen, QPainterPath, QColor
from ui.theme import NeonTheme
from ui.layouts import KeyboardLayoutManager
from utils.window_utils import WindowManager


class VirtualKeyboard(QMainWindow):
    """Main window for the virtual keyboard application"""

    def __init__(self):
        """Initialize the virtual keyboard window"""
        super().__init__()
        self.target_window = None
        self.window_manager = WindowManager()
        self.theme = NeonTheme()
        self.initUI()

        # Variables for window dragging
        self.dragging = False
        self.offset = QPoint()

    def initUI(self):
        """Initialize the user interface"""
        # Set window properties
        self.setWindowTitle('Neon Virtual Keyboard')
        self.setGeometry(100, 100, 900, 350)

        # Set window flags to stay on top and frameless
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)

        # Set the window as a tool window so it doesn't show in taskbar and loses focus easily
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

        # Create keyboard layout manager
        self.keyboard_manager = KeyboardLayoutManager()

        # Add keyboard to main layout
        main_layout.addWidget(keyboard_frame)

        # Add bottom status bar
        self.add_status_bar(main_layout)

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
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(close_btn)

        main_layout.addWidget(title_bar)

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
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(10, 0, 10, 0)

        # Add target window display
        self.target_window_label = QLabel("Target: None")
        self.target_window_label.setStyleSheet("color: #0099ff; font-size: 12px;")
        bottom_layout.addWidget(self.target_window_label)

        # Add spacer
        bottom_layout.addStretch()

        # Add version info
        version_info = QLabel("v1.0.0")
        version_info.setStyleSheet("color: #0077cc; font-size: 12px;")
        bottom_layout.addWidget(version_info)

        main_layout.addWidget(bottom_frame)

    def update_status(self, key):
        """Update the status label with the pressed key"""
        self.status_label.setText(f"Key Pressed: {key}")
        # Reset status after 1 second
        QTimer.singleShot(1000,
                          lambda: self.status_label.setText("Click keys to type (focus maintained on target window)"))

        # Ensure focus is maintained on target window
        self.restore_target_window_focus()

    def store_target_window(self):
        """Store the target window before showing the keyboard"""
        self.target_window = self.window_manager.get_active_window()
        window_title = self.window_manager.get_window_title(self.target_window)

        if self.target_window and window_title:
            # Truncate if too long
            if len(window_title) > 30:
                window_title = window_title[:27] + "..."
            self.target_window_label.setText(f"Target: {window_title}")
        else:
            self.target_window_label.setText("Target: None")

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
        # Store the active window before we take focus
        QTimer.singleShot(100, self.store_target_window)

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
