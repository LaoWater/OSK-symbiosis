from PyQt6.QtWidgets import (QMainWindow, QWidget, QPushButton,
                             QVBoxLayout, QHBoxLayout, QLabel, QFrame, QApplication, QGraphicsOpacityEffect)
from PyQt6.QtCore import (Qt, QTimer, QPoint, QAbstractNativeEventFilter,
                          QPropertyAnimation, QEasingCurve, QRect,
                          QAbstractAnimation, QSize)
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QPainter, QPen, QPainterPath, QColor, QKeySequence, QShortcut, QIcon


def create_recording_button(icon_path):
    """Creates a styled recording button with different styles for AI and normal buttons."""
    is_ai_button = "ai" in icon_path.lower()

    border_color = "#0099ff" if not is_ai_button else "#bb00ff"  # Blue for normal, neon purple for AI
    hover_border_color = "#00bbff" if not is_ai_button else "#dd00ff"

    button = QPushButton()
    button.setFixedSize(24, 24)
    button.setIcon(QIcon(icon_path))
    button.setIconSize(QSize(18, 18))
    button.setStyleSheet(f"""
        QPushButton {{
            background-color: #2a2a2a;
            border-radius: 12px;
            border: 1px solid {border_color};
        }}
        QPushButton:hover {{
            background-color: #3a3a3a;
            border: 1px solid {hover_border_color};
        }}
        QPushButton:pressed {{
            background-color: #444444;
        }}
    """)
    return button

def add_audio_recording(parent, bottom_layout):
    """Add an audio recording button to the status bar"""
    # Create a container for the recording button to center it
    recording_container = QFrame()
    recording_container.setStyleSheet("background-color: transparent; border: none;")
    recording_layout = QHBoxLayout(recording_container)
    recording_layout.setContentsMargins(0, 0, 0, 0)

    # Create buttons using the helper function
    parent.recording_button = create_recording_button("icons/microphone.png")
    parent.ai_recording_button = create_recording_button("icons/ai_microphone.png")

    # Create status message label
    parent.status_message = QLabel("")
    parent.status_message.setStyleSheet("""
        QLabel {
            color: white;
            font-size: 12px;
            background-color: transparent;
        }
    """)
    # Create opacity effect for fade animation
    parent.message_opacity = QGraphicsOpacityEffect()
    parent.message_opacity.setOpacity(1.0)
    parent.status_message.setGraphicsEffect(parent.message_opacity)

    # Create the recording indicator (red dot)
    parent.recording_indicator = QFrame()
    parent.recording_indicator.setFixedSize(5, 5)
    parent.recording_indicator.setStyleSheet("""
        background-color: #cc0000;
        border-radius: 2px;
    """)
    parent.recording_indicator.setVisible(False)

    # Add widgets to layout
    indicator_container = QFrame()
    indicator_layout = QHBoxLayout(indicator_container)
    indicator_layout.setContentsMargins(0, 0, 0, 0)
    indicator_layout.addWidget(parent.recording_indicator)
    indicator_layout.addWidget(parent.status_message)
    indicator_layout.addStretch()

    # Connect the button to a function
    parent.recording_button.clicked.connect(lambda: toggle_recording(parent))
    parent.ai_recording_button.clicked.connect(lambda: toggle_ai_recording(parent))

    # Add the button to the container with stretch on both sides for centering
    recording_layout.addStretch()
    recording_layout.addStretch()
    recording_layout.addWidget(parent.recording_button)
    recording_layout.addWidget(parent.ai_recording_button)
    recording_layout.addStretch()

    # Add the container and the message label to the bottom layout
    bottom_layout.addWidget(recording_container)
    bottom_layout.addWidget(indicator_container)

    # Initialize recording state
    parent.is_normal_recording = False
    parent.is_ai_recording = False

    # Setup animation for the button
    setup_recording_animation(parent)
    setup_ai_recording_animation(parent)

    # Setup blinking animation for the red dot
    setup_blinking_animation(parent)


def setup_recording_animation(parent):
    """Set up the pulsing animation for the recording button"""
    parent.pulse_animation = QPropertyAnimation(parent.recording_button, b"styleSheet")
    parent.pulse_animation.setDuration(1000)
    parent.pulse_animation.setLoopCount(-1)  # Infinite loop

    # Define the start and end styles for pulsing effect
    normal_style = """
        QPushButton {
            background-color: #2a2a2a;
            border-radius: 12px;
            border: 1px solid #0099ff;
        }
        QPushButton:hover {
            background-color: #3a3a3a;
            border: 1px solid #00bbff;
        }
        QPushButton:pressed {
            background-color: #0077cc;
        }
    """

    recording_style = """
        QPushButton {
            background-color: #cc0000;
            border-radius: 12px;
            border: 1px solid #ff3333;
        }
        QPushButton:hover {
            background-color: #dd0000;
            border: 1px solid #ff5555;
        }
        QPushButton:pressed {
            background-color: #aa0000;
        }
    """

    parent.pulse_animation.setStartValue(normal_style)
    parent.pulse_animation.setEndValue(recording_style)


def setup_ai_recording_animation(parent):
    ai_normal_style = """
        QPushButton {
            background-color: #2a2a2a;
            border-radius: 12px;
            border: 1px solid #bb00ff;
        }
        QPushButton:hover {
            background-color: #3a3a3a;
            border: 1px solid #dd00ff;
        }
        QPushButton:pressed {
            background-color: #444444;
        }
    """
    ai_recording_style = """
        QPushButton {
            background-color: #cc0000;
            border-radius: 12px;
            border: 1px solid #ff3333;
        }
        QPushButton:hover {
            background-color: #dd0000;
            border: 1px solid #ff5555;
        }
        QPushButton:pressed {
            background-color: #aa0000;
        }
    """
    parent.ai_pulse_animation = QPropertyAnimation(parent.ai_recording_button, b"styleSheet")
    parent.ai_pulse_animation.setDuration(1000)
    parent.ai_pulse_animation.setLoopCount(-1)
    parent.ai_pulse_animation.setStartValue(ai_normal_style)
    parent.ai_pulse_animation.setEndValue(ai_recording_style)


def setup_blinking_animation(parent):
    """Set up the blinking animation for the red indicator dot"""
    # Create a timer for blinking the recording indicator
    parent.blink_timer = QTimer()
    parent.blink_timer.setInterval(700)  # 0.7 second interval
    parent.blink_timer.timeout.connect(lambda: toggle_indicator_visibility(parent))

    # Create opacity effect for fade animation
    parent.message_opacity = QGraphicsOpacityEffect()

    # Create fade animation for status message
    parent.fade_animation = QPropertyAnimation(parent.message_opacity, b"opacity")
    parent.fade_animation.setDuration(1000)  # 1 second fade duration
    parent.fade_animation.setStartValue(1.0)
    parent.fade_animation.setEndValue(0.0)
    parent.fade_animation.setEasingCurve(QEasingCurve.Type.InQuad)  # Use QEasingCurve.Type.InQuad


def toggle_indicator_visibility(parent):
    """Toggle the visibility of the recording indicator"""
    parent.recording_indicator.setVisible(not parent.recording_indicator.isVisible())



def toggle_recording(parent):
    """Toggle the recording state"""
    parent.is_normal_recording = not parent.is_normal_recording

    if parent.is_normal_recording:
        # Start recording
        parent.status_message.setText("Recording started...")
        parent.message_opacity.setOpacity(1.0)  # Reset opacity before starting fade
        parent.fade_animation.start()

        # Show and start blinking the indicator
        parent.recording_indicator.setVisible(True)
        parent.blink_timer.start()

        # Start button pulse animation
        parent.pulse_animation.start()
        parent.recording_button.setIcon(QIcon("icons/stop.png"))

        print("Recording for Transcript started")
    else:
        # Stop recording
        parent.status_message.setText("Recording stopped.")
        parent.message_opacity.setOpacity(1.0)  # Reset opacity
        parent.fade_animation.start()

        # Stop and hide the blinking indicator
        parent.blink_timer.stop()
        parent.recording_indicator.setVisible(False)

        # Stop button animation and reset style
        parent.pulse_animation.stop()

        # Reset the button style properly without making it disappear
        normal_style = """
            QPushButton {
                background-color: #2a2a2a;
                border-radius: 12px;
                border: 1px solid #0099ff;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border: 1px solid #00bbff;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """
        parent.recording_button.setStyleSheet(normal_style)
        parent.recording_button.setIcon(QIcon("icons/microphone.png"))

        print("Recording for Transcript stopped")







def toggle_ai_recording(parent):
    parent.is_ai_recording = not parent.is_ai_recording
    if parent.is_ai_recording:
        parent.status_message.setText("Recording for LLM Inference started...")
        parent.message_opacity.setOpacity(1.0)
        parent.fade_animation.start()
        parent.recording_indicator.setVisible(True)
        parent.blink_timer.start()
        parent.ai_pulse_animation.start()
        parent.ai_recording_button.setIcon(QIcon("icons/stop.png"))
        print("Recording started")
    else:
        if not parent.is_normal_recording:
            parent.status_message.setText("Recording stopped.")
            parent.message_opacity.setOpacity(1.0)
            parent.fade_animation.start()
            parent.blink_timer.stop()
            parent.recording_indicator.setVisible(False)
        parent.ai_pulse_animation.stop()
        ai_normal_style = """
            QPushButton {
                background-color: #2a2a2a;
                border-radius: 12px;
                border: 1px solid #bb00ff;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border: 1px solid #dd00ff;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """
        parent.ai_recording_button.setStyleSheet(ai_normal_style)
        parent.ai_recording_button.setIcon(QIcon("icons/ai_microphone.png"))
        print("Recording for LLM Inference stopped")
