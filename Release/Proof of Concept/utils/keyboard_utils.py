"""
Keyboard input utilities for the Neon Virtual Keyboard
Handles sending keyboard inputs to the system
"""

import keyboard

class KeyboardController:
    """Controls keyboard input operations"""
    key_states = {}  # Stores the state of pressed keys

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
        """Press a keyboard key and update key state"""
        try:
            normalized_key = KeyboardController.normalize_key(key_value)
            if normalized_key:
                keyboard.press(normalized_key)
                KeyboardController.key_states[normalized_key] = True  # Update key state
                print(f"Pressed key: {normalized_key}, key_states: {KeyboardController.key_states}")  # Debugging print
                return True
        except Exception as e:
            print(f"Error pressing key {key_value}: {e}")
        return False

    @staticmethod
    def release_key(key_value):
        """Release a keyboard key and update key state"""
        try:
            normalized_key = KeyboardController.normalize_key(key_value)
            if normalized_key:
                keyboard.release(normalized_key)
                KeyboardController.key_states[normalized_key] = False  # Update key state
                print(f"Released key: {normalized_key}, key_states: {KeyboardController.key_states}")  # Debugging print
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
                KeyboardController.key_states[normalized_key] = False  # Ensure it's set to released
                print(f"Pressed and released key: {normalized_key}, key_states: {KeyboardController.key_states}")  # Debugging print
                return True
        except Exception as e:
            print(f"Error pressing and releasing key {key_value}: {e}")
        return False

    @staticmethod
    def is_key_pressed(key):
        """Check if a key is currently pressed."""
        normalized_key = KeyboardController.normalize_key(key)
        state = KeyboardController.key_states.get(normalized_key, False)
        print(f"Checking is_key_pressed({key}): {state}, key_states: {KeyboardController.key_states}")  # Debugging print
        return state
