"""
Theme management for the Neon Virtual Keyboard
Contains styling definitions and theme application functions
"""

from PyQt6.QtGui import QFont, QFontDatabase

class NeonTheme:
    """Manages theme settings for the Neon Virtual Keyboard"""

    # Color definitions with refined aesthetics
    COLORS = {
        'background': '#181818',  # Smooth dark gray instead of full black
        'secondary_bg': '#222222',  # Slightly lighter gray for contrast
        'accent': '#0088dd',  # Vibrant but slightly softened neon blue
        'accent_light': '#00b3ff',  # A touch brighter than original
        'accent_bright': '#33ddff',  # More luminescent blue for emphasis
        'text': '#e5e5e5',  # Warmer and softer white
        'text_bright': '#ffffff',  # Pure white for high contrast
        'text_dim': '#bbbbbb',  # Slightly softened dim text
        'error': '#ff4444',  # More vibrant red for better contrast
        'hover_bg': '#2e2e2e',  # Slightly lighter hover effect
        'press_bg': '#005588',  # Softer blue for press state
        'press_border': '#77ddff',  # Gentle neon glow
    }

    @staticmethod
    def setup_font(app):
        """Set up application font"""
        font_id = QFontDatabase.addApplicationFont("resources/fonts/Hack-Regular.ttf")
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            font = QFont(font_families[0], 11)
        else:
            font = QFont("Monospace", 11)

        app.setFont(font)
        return font

    @staticmethod
    def main_window_style():
        """Return the stylesheet for the main window"""
        return f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {NeonTheme.COLORS['secondary_bg']}, stop:1 {NeonTheme.COLORS['secondary_bg']});
                border: 1px solid {NeonTheme.COLORS['accent']};
                border-radius: 12px;
            }}
            QLabel {{
                color: {NeonTheme.COLORS['accent_light']};
                font-size: 13px;
                font-weight: normal;
            }}
            QFrame {{
                background-color: {NeonTheme.COLORS['secondary_bg']};
                border: 1px solid {NeonTheme.COLORS['accent']};
                border-radius: 12px;
            }}
            QPushButton#titleButton {{
                background-color: transparent;
                color: {NeonTheme.COLORS['accent_light']};
                border: none;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton#titleButton:hover {{
                color: {NeonTheme.COLORS['accent_bright']};
                text-shadow: 0px 0px 8px {NeonTheme.COLORS['accent_bright']};
            }}
            QPushButton#minimizeButton {{
                background-color: transparent;
                color: {NeonTheme.COLORS['text_dim']};
                border: none;
                font-size: 16px;
            }}
            QPushButton#minimizeButton:hover {{
                color: {NeonTheme.COLORS['text_bright']};
                background-color: rgba(255, 255, 255, 0.1);
            }}
            QPushButton#closeButton {{
                background-color: transparent;
                color: {NeonTheme.COLORS['text_dim']};
                border: none;
                font-size: 16px;
            }}
            QPushButton#closeButton:hover {{
                color: {NeonTheme.COLORS['text_bright']};
                background-color: {NeonTheme.COLORS['error']};
            }}
        """

    @staticmethod
    def get_key_styles(width, height):
        """Return styles for keyboard buttons"""
        return {
            'default': f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {NeonTheme.COLORS['secondary_bg']}, stop:1 {NeonTheme.COLORS['hover_bg']});
                    color: {NeonTheme.COLORS['text']};
                    border: 1px solid {NeonTheme.COLORS['accent']};
                    border-radius: 8px;
                    padding: 6px;
                    font-size: 14px;
                    min-width: {width}px;
                    min-height: {height}px;
                }}
            """,
            'hover': f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {NeonTheme.COLORS['hover_bg']}, stop:1 {NeonTheme.COLORS['press_border']});
                    color: {NeonTheme.COLORS['text_bright']};
                    border: 1px solid {NeonTheme.COLORS['accent_light']};
                    border-radius: 8px;
                    padding: 6px;
                    font-size: 14px;
                    min-width: {width}px;
                    min-height: {height}px;
                }}
            """,
            'pressed': f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {NeonTheme.COLORS['press_bg']}, stop:1 {NeonTheme.COLORS['press_border']});
                    color: {NeonTheme.COLORS['text_bright']};
                    border: 2px solid {NeonTheme.COLORS['press_border']};
                    border-radius: 8px;
                    padding: 6px;
                    font-size: 14px;
                    min-width: {width}px;
                    min-height: {height}px;
                }}
            """
        }

    @staticmethod
    def apply_to_window(window):
        """Apply the main window style to the given window instance"""
        window.setStyleSheet(NeonTheme.main_window_style())
