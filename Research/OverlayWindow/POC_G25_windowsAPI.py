import time
import numpy as np
import mss
import cv2
import win32gui
import win32process
import win32api
import ctypes  # For checking admin rights
import sys
import os

TARGET_PROCESS_NAME = "vlc.exe"
MODIFICATION_COLOR = (0, 0, 0)  # Black in BGR format


def is_admin():
    """Checks if the script is running with admin privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def find_target_windows(target_name):
    """Finds windows belonging to the target process."""
    target_windows = []

    def enum_windows_proc(hwnd, lParam):
        if not win32gui.IsWindowVisible(hwnd) or not win32gui.IsWindowEnabled(hwnd):
            return True  # Continue enumeration

        # Get the process ID (PID) for the window
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid == 0:
            return True  # Skip windows without a valid PID (e.g., system components)

        process_handle = None
        try:
            # PROCESS_QUERY_LIMITED_INFORMATION is often sufficient and requires fewer privileges
            # PROCESS_QUERY_INFORMATION | PROCESS_VM_READ might be needed on older systems or specific cases
            access_flags = win32con.PROCESS_QUERY_LIMITED_INFORMATION
            process_handle = win32api.OpenProcess(access_flags, False, pid)
            if process_handle:
                try:
                    # Attempt to get the executable path
                    exe_path = win32process.GetModuleFileNameEx(process_handle, 0)
                    exe_name = os.path.basename(exe_path)

                    # Check if it matches the target process (case-insensitive)
                    if exe_name.lower() == target_name.lower():
                        rect = win32gui.GetWindowRect(hwnd)
                        # GetWindowRect gives (left, top, right, bottom)
                        if rect[2] > rect[0] and rect[3] > rect[1]:  # Basic check for valid rect
                            target_windows.append({"hwnd": hwnd, "rect": rect})

                except Exception as e_inner:
                    # May fail if process exits between checks or insufficient permissions
                    # print(f"Error getting module name for PID {pid}: {e_inner}") # Optional debug
                    pass  # Continue enumeration
        except Exception as e_outer:
            # Often "Access is denied" if script lacks privileges for the target process
            # print(f"Error opening process PID {pid}: {e_outer}") # Optional debug
            pass  # Continue enumeration
        finally:
            if process_handle:
                win32api.CloseHandle(process_handle)

        return True  # Continue enumeration

    try:
        win32gui.EnumWindows(enum_windows_proc, None)
    except Exception as e:
        print(f"Error during EnumWindows: {e}")

    return target_windows


# --- Main Execution ---
if not sys.platform == 'win32':
    print("This script requires Windows and pywin32.")
    sys.exit(1)

# Check for admin rights, often needed for OpenProcess/GetModuleFileNameEx
if not is_admin():
    print("WARNING: Script not running as Administrator.")
    print("It might not be able to identify windows from other processes (like VLC).")
    print("Please try running this script as an Administrator.")
    # Consider exiting if admin is strictly required, or proceed with potential failures
    # sys.exit(1)

# Import win32con constants *after* platform check
import win32con

print(f"Attempting to hide windows belonging to: {TARGET_PROCESS_NAME}")
print("Press 'q' in the display window to quit.")

try:
    with mss.mss() as sct:
        # Use monitor 1 (usually the primary monitor)
        monitor = sct.monitors[1]

        while True:
            start_time = time.time()

            # 1. Capture the screen
            img_mss = sct.grab(monitor)
            # Convert BGRA raw bytes to NumPy array (BGRA format)
            img_np = np.frombuffer(img_mss.rgb, dtype=np.uint8).reshape((img_mss.height, img_mss.width, 4))
            # Convert BGRA to BGR for OpenCV display/drawing
            img_cv = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)

            # 2. Identify target windows
            vlc_windows = find_target_windows(TARGET_PROCESS_NAME)

            # 3. Modify the image
            if vlc_windows:
                for win_info in vlc_windows:
                    rect = win_info['rect']
                    left, top, right, bottom = rect

                    # Ensure coordinates are within the captured monitor bounds
                    # (GetWindowRect gives screen coords, grab gives monitor coords)
                    # Adjust coordinates relative to the monitor's top-left corner
                    mon_left, mon_top = monitor["left"], monitor["top"]
                    rel_left = max(0, left - mon_left)
                    rel_top = max(0, top - mon_top)
                    rel_right = min(monitor["width"], right - mon_left)
                    rel_bottom = min(monitor["height"], bottom - mon_top)

                    # Draw a filled rectangle over the window area
                    if rel_right > rel_left and rel_bottom > rel_top:
                        cv2.rectangle(img_cv, (rel_left, rel_top), (rel_right, rel_bottom), MODIFICATION_COLOR,
                                      -1)  # -1 thickness fills the rectangle
            else:
                # Optional: Print a message if VLC is not detected
                # print("No VLC windows detected.")
                pass

            # 4. Display the modified image
            cv2.imshow('Modified Screen Capture (Proof of Concept)', img_cv)

            # Frame rate limiting and exit condition
            elapsed = time.time() - start_time
            wait_time = max(1, int(1000 / 20 - elapsed * 1000))  # Aim for ~20 FPS

            if cv2.waitKey(wait_time) & 0xFF == ord('q'):
                break

finally:
    cv2.destroyAllWindows()
    print("Exited.")
