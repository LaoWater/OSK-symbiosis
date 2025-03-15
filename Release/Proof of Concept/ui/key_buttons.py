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
    MODIFIER_KEYS = ["left shift", "right shift", "left ctrl", "right ctrl", "left alt", "right alt"]

    def __init__(self, key_text, key_value=None, width=50, height=50, parent=None):
        super().__init__(key_text, parent)
        self.key_text = key_text
        self.key_value = key_value if key_value is not None else key_text
        self.width = width
        self.height = height
        self.is_toggled = False
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFixedSize(width, height)
        self.setup_styles()
        self.setup_animations()

    def setup_styles(self):
        styles = NeonTheme.get_key_styles(self.width, self.height)
        self.default_style = styles['default']
        self.hover_style = styles['hover']
        self.pressed_style = styles['pressed']
        self.setStyleSheet(self.default_style)

    def setup_animations(self):
        self.size_animation = QPropertyAnimation(self, b"size")
        self.size_animation.setDuration(100)
        self.size_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.glow_intensity = 0
        self.glow_animation = QTimer()
        self.glow_animation.timeout.connect(self.update_glow)
        self.is_pressed = False

    def update_glow(self):
        if self.is_pressed and self.glow_intensity < 100:
            self.glow_intensity += 10
        elif not self.is_pressed and self.glow_intensity > 0:
            self.glow_intensity -= 5
        if self.glow_intensity <= 0 and not self.is_pressed:
            self.glow_animation.stop()
            self.glow_intensity = 0
        self.update()

    def enterEvent(self, event):
        if self.key_value in self.MODIFIER_KEYS and self.is_toggled:
            self.setStyleSheet(self.pressed_style)
        else:
            self.setStyleSheet(self.hover_style)
        cursor = QCursor(Qt.CursorShape.PointingHandCursor)
        QApplication.setOverrideCursor(cursor)
        self.size_animation.setStartValue(self.size())
        self.size_animation.setEndValue(QSize(self.width + 4, self.height + 4))
        self.size_animation.start()
        if not self.glow_animation.isActive():
            self.glow_animation.start(30)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.key_value in self.MODIFIER_KEYS and self.is_toggled:
            self.setStyleSheet(self.pressed_style)
        else:
            self.setStyleSheet(self.default_style)
        QApplication.restoreOverrideCursor()
        self.size_animation.setStartValue(self.size())
        self.size_animation.setEndValue(QSize(self.width, self.height))
        self.size_animation.start()
        self.is_pressed = False
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.key_value in self.MODIFIER_KEYS:
                if not self.is_toggled:
                    KeyboardController.press_key(self.key_value)
                    self.is_toggled = True
                    self.setStyleSheet(self.pressed_style)
                else:
                    KeyboardController.release_key(self.key_value)
                    self.is_toggled = False
                    if self.underMouse():
                        self.setStyleSheet(self.hover_style)
                    else:
                        self.setStyleSheet(self.default_style)
                parent = self
                while parent.parent():
                    parent = parent.parent()
                    if hasattr(parent, 'restore_target_window_focus'):
                        QTimer.singleShot(50, parent.restore_target_window_focus)
                        break
            else:
                self.setStyleSheet(self.pressed_style)
                self.is_pressed = True
                KeyboardController.press_key(self.key_value)
                parent = self
                while parent.parent():
                    parent = parent.parent()
                    if hasattr(parent, 'update_status'):
                        parent.update_status(self.key_value)
                        break
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.key_value not in self.MODIFIER_KEYS:
                KeyboardController.release_key(self.key_value)
                if self.underMouse():
                    self.setStyleSheet(self.hover_style)
                else:
                    self.setStyleSheet(self.default_style)
                self.is_pressed = False
                parent = self
                while parent.parent():
                    parent = parent.parent()
                    if hasattr(parent, 'restore_target_window_focus'):
                        QTimer.singleShot(50, parent.restore_target_window_focus)
                        break
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.glow_intensity > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            pen = QPen(QColor(0, 170, 255, self.glow_intensity))
            pen.setWidth(2)
            painter.setPen(pen)
            path = QPainterPath()
            path.addRoundedRect(2, 2, self.width - 4, self.height - 4, 5, 5)
            painter.drawPath(path)
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