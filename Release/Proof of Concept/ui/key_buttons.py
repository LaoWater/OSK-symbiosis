"""
Key button classes for the Neon Virtual Keyboard
Provides styled keyboard buttons with neon effects
"""

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, QTimer
from PyQt6.QtGui import QCursor, QPainter, QPen, QBrush, QPainterPath, QLinearGradient, QColor
from PyQt6.QtWidgets import QApplication

from ui.theme import NeonTheme
from utils.keyboard_utils import KeyboardController


class NeonKeyButton(QPushButton):
    """Custom button with neon styling for keyboard keys"""

    def __init__(self, key_text, key_value=None, width=50, height=50, parent=None):
        """Initialize the button with custom styling and animations"""
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
        """Set up button styles"""
        styles = NeonTheme.get_key_styles(self.width, self.height)
        self.default_style = styles['default']
        self.hover_style = styles['hover']
        self.pressed_style = styles['pressed']
        self.setStyleSheet(self.default_style)

    def setup_animations(self):
        """Set up button animations"""
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
        """Update glow effect animation"""
        if self.is_pressed and self.glow_intensity < 100:
            self.glow_intensity += 10
        elif not self.is_pressed and self.glow_intensity > 0:
            self.glow_intensity -= 5

        if self.glow_intensity <= 0 and not self.is_pressed:
            self.glow_animation.stop()
            self.glow_intensity = 0

        self.update()  # Trigger repaint

    def enterEvent(self, event):
        """Handle mouse enter event"""
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
        """Handle mouse leave event"""
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
        """Handle mouse press event"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.setStyleSheet(self.pressed_style)
            self.is_pressed = True

            # Directly handle key press using keyboard library
            KeyboardController.press_key(self.key_value)

            # Also notify parent to update UI
            # Find the VirtualKeyboard parent to call its method
            parent = self
            while parent.parent():
                parent = parent.parent()
                if hasattr(parent, 'update_status'):
                    parent.update_status(self.key_value)
                    break

            # Don't call super() to prevent focus change
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release event"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Restore hover style if mouse is still over the button
            if self.underMouse():
                self.setStyleSheet(self.hover_style)
            else:
                self.setStyleSheet(self.default_style)

            # Release key using keyboard library
            KeyboardController.release_key(self.key_value)

            # Notify parent to restore focus to target window
            parent = self
            while parent.parent():
                parent = parent.parent()
                if hasattr(parent, 'restore_target_window_focus'):
                    # This fixes the issue where the window closes immediately
                    # by using a small delay before restoring focus
                    QTimer.singleShot(50, parent.restore_target_window_focus)
                    break

            self.is_pressed = False

            # Don't call super() to prevent focus change
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        """Custom paint event to add neon effects"""
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
    """Special keyboard button with different default size"""

    def __init__(self, key_text, key_value=None, width=80, height=50, parent=None):
        """Initialize a special key button with custom width"""
        super().__init__(key_text, key_value, width, height, parent)