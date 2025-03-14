"""
Theme management for the Neon Virtual Keyboard
Contains styling definitions and theme application functions
"""

from PyQt6.QtGui import QFont, QFontDatabase


class NeonTheme:
    """Manages theme settings for the Neon Virtual Keyboard"""

    # Color definitions
    COLORS = {
        'background': '#121212',
        'secondary_bg': '#1a1a1a',
        'accent': '#0077cc',
        'accent_light': '#00aaff',
        'accent_bright': '#33ccff',
        'text': '#e0e0e0',
        'text_bright': '#ffffff',
        'text_dim': '#cccccc',
        'error': '#cc0000',
        'hover_bg': '#2a2a2a',
        'press_bg': '#003366',
        'press_border': '#66ccff',
    }

    @staticmethod
    def setup_font(app):
        """Set up application font"""
        # Try to load a custom font, or fall back to system font
        font_id = QFontDatabase.addApplicationFont("resources/fonts/Hack-Regular.ttf")
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            font = QFont(font_families[0], 11)
        else:
            # Fallback to system monospace font
            font = QFont("Monospace", 11)

        app.setFont(font)
        return font

    @staticmethod
    def main_window_style():
        """Return the stylesheet for the main window"""
        return f"""
            QMainWindow {{
                background-color: {NeonTheme.COLORS['background']};
                border: 1px solid {NeonTheme.COLORS['accent']};
                border-radius: 10px;
            }}
            QLabel {{
                color: {NeonTheme.COLORS['accent_light']};
                font-size: 14px;
            }}
            QFrame {{
                background-color: {NeonTheme.COLORS['secondary_bg']};
                border: 1px solid {NeonTheme.COLORS['accent']};
                border-radius: 10px;
            }}
            QPushButton#titleButton {{
                background-color: transparent;
                color: {NeonTheme.COLORS['accent_light']};
                border: none;
                font-size: 16px;
            }}
            QPushButton#titleButton:hover {{
                color: {NeonTheme.COLORS['accent_bright']};
            }}
            QPushButton#minimizeButton {{
                background-color: transparent;
                color: {NeonTheme.COLORS['text_dim']};
                border: none;
                font-size: 16px;
            }}
            QPushButton#minimizeButton:hover {{
                color: {NeonTheme.COLORS['text_bright']};
                background-color: #444444;
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
                    background-color: {NeonTheme.COLORS['secondary_bg']};
                    color: {NeonTheme.COLORS['text']};
                    border: 1px solid {NeonTheme.COLORS['accent']};
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 14px;
                    min-width: {width}px;
                    min-height: {height}px;
                }}
            """,
            'hover': f"""
                QPushButton {{
                    background-color: {NeonTheme.COLORS['hover_bg']};
                    color: {NeonTheme.COLORS['text_bright']};
                    border: 2px solid {NeonTheme.COLORS['accent_light']};
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 14px;
                    min-width: {width}px;
                    min-height: {height}px;
                }}
            """,
            'pressed': f"""
                QPushButton {{
                    background-color: {NeonTheme.COLORS['press_bg']};
                    color: {NeonTheme.COLORS['text_bright']};
                    border: 2px solid {NeonTheme.COLORS['press_border']};
                    border-radius: 5px;
                    padding: 5px;
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
