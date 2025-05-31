import sys
import time
import pyautogui

# On macOS, we need Quartz to send a proper double-click event with clickCount.
if sys.platform == "darwin":
    import Quartz

def double_click(x, y, interval=0.2, button='left'):
    """
    Performs a double-click at (x, y) in a way that works on both macOS and Windows/Linux.
    - On Windows/Linux, uses pyautogui.click(clicks=2, interval=interval).
    - On macOS, uses Quartz to send two separate click events with the correct clickCount.
    """
    if sys.platform == "darwin":
        # Map 'left'/'right' to Quartz button constants
        quartz_button = Quartz.kCGMouseButtonLeft if button == 'left' else Quartz.kCGMouseButtonRight

        # First click (clickCount = 1)
        down1 = Quartz.CGEventCreateMouseEvent(
            None, Quartz.kCGEventLeftMouseDown if quartz_button == Quartz.kCGMouseButtonLeft else Quartz.kCGEventRightMouseDown,
            (x, y), quartz_button
        )
        Quartz.CGEventSetIntegerValueField(down1, Quartz.kCGMouseEventClickState, 1)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, down1)

        up1 = Quartz.CGEventCreateMouseEvent(
            None, Quartz.kCGEventLeftMouseUp if quartz_button == Quartz.kCGMouseButtonLeft else Quartz.kCGEventRightMouseUp,
            (x, y), quartz_button
        )
        Quartz.CGEventSetIntegerValueField(up1, Quartz.kCGMouseEventClickState, 1)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, up1)

        # Wait the specified interval
        time.sleep(interval)

        # Second click (clickCount = 2)
        down2 = Quartz.CGEventCreateMouseEvent(
            None, Quartz.kCGEventLeftMouseDown if quartz_button == Quartz.kCGMouseButtonLeft else Quartz.kCGEventRightMouseDown,
            (x, y), quartz_button
        )
        Quartz.CGEventSetIntegerValueField(down2, Quartz.kCGMouseEventClickState, 2)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, down2)

        up2 = Quartz.CGEventCreateMouseEvent(
            None, Quartz.kCGEventLeftMouseUp if quartz_button == Quartz.kCGMouseButtonLeft else Quartz.kCGEventRightMouseUp,
            (x, y), quartz_button
        )
        Quartz.CGEventSetIntegerValueField(up2, Quartz.kCGMouseEventClickState, 2)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, up2)
    else:
        # On Windows and Linux, pyautogui.click handles double-click correctly
        pyautogui.click(x=x, y=y, clicks=2, interval=interval, button=button)

if __name__ == "__main__":
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0.0

    # Give you 3 seconds to place the cursor over the text you want to select
    print("Coloca el cursor sobre el texto y espera 3 segundos...")
    time.sleep(3)

    # Read the position that PyAutoGUI sees
    x, y = pyautogui.position()
    print("Posición detectada por PyAutoGUI:", (x, y))

    # Now try different intervals for the double-click
    for intervalo in (0.2, 0.3, 0.5):
        print(f"Probando double-click con interval={intervalo}")
        double_click(x, y, interval=intervalo, button='left')
        time.sleep(3)