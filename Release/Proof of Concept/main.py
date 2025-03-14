#!/usr/bin/env python3
"""
Neon Virtual Keyboard - Main Entry Point
A stylish on-screen keyboard with neon effects that sends keystrokes to the active window.
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui.keyboard_window import VirtualKeyboard


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    keyboard_app = VirtualKeyboard()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
