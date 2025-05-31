import time
import pyautogui
import ctypes
import sys
from screeninfo import get_monitors

pyautogui.FAILSAFE = False  # Disable fail-safe for this test

# Enable per-monitor DPI awareness (for accurate coordinates on Windows)
if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PER_MONITOR_DPI_AWARE
    except Exception:
        print("Warning: Could not set DPI awareness.")

# Step 1: List all monitors
print("== Connected Monitors ==")
for i, m in enumerate(get_monitors()):
    print(f"Monitor {i + 1}: {m.width}x{m.height} at ({m.x}, {m.y})")

# Step 2: Inform user and wait
print("\nMove the mouse to a target position within 5 seconds...")
time.sleep(5)

# Step 3: Capture mouse position
pos = pyautogui.position()
print(f"\nCaptured mouse position: {pos}")

# Step 4: Move to a safe point instead of (0,0)
print("Moving to (100, 100)...")
pyautogui.moveTo(100, 100, duration=0.5)
time.sleep(0.5)

# Step 5: Move back to captured position
print(f"Moving back to captured position: {pos}...")
pyautogui.moveTo(pos.x, pos.y, duration=0.5)

# Step 6: Validate offset
final_pos = pyautogui.position()
print(f"Returned position: {final_pos}")
dx = final_pos.x - pos.x
dy = final_pos.y - pos.y
print(f"Offset: Δx={dx}, Δy={dy}")

print("Done.")
