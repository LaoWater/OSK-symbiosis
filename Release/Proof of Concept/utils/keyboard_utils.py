"""
Keyboard input utilities for the Neon Virtual Keyboard
Handles sending keyboard inputs to the system
"""

import keyboard


class KeyboardController:
    """Controls keyboard input operations"""

    @staticmethod
    def normalize_key(key_value):
        """Normalize key values for consistent behavior"""
        if not key_value:
            return None

        # Handle special keys
        if key_value.lower() == "space":
            return " "

        # Keys that need special handling
        special_keys = {
            "win": "windows",  # Windows key
        }

        # Check if we have a special mapping
        if key_value.lower() in special_keys:
            return special_keys[key_value.lower()]

        # Return single character keys as-is, otherwise lowercase
        return key_value.lower() if len(key_value) == 1 else key_value

    @staticmethod
    def press_key(key_value):
        """Press a keyboard key"""
        try:
            normalized_key = KeyboardController.normalize_key(key_value)
            if normalized_key:
                keyboard.press(normalized_key)
                return True
        except Exception as e:
            print(f"Error pressing key {key_value}: {e}")
        return False

    @staticmethod
    def release_key(key_value):
        """Release a keyboard key"""
        try:
            normalized_key = KeyboardController.normalize_key(key_value)
            if normalized_key:
                keyboard.release(normalized_key)
                return True
        except Exception as e:
            print(f"Error releasing key {key_value}: {e}")
        return False

    @staticmethod
    def press_and_release_key(key_value):
        """Press and release a keyboard key"""
        try:
            normalized_key = KeyboardController.normalize_key(key_value)
            if normalized_key:
                keyboard.press_and_release(normalized_key)
                return True
        except Exception as e:
            print(f"Error pressing and releasing key {key_value}: {e}")
        return False