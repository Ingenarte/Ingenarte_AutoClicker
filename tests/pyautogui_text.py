import pyautogui
import time
import cv2
import numpy as np

def find_and_move(image_path, confidence=0.9, timeout=10):
    """
    Search for the image on the screen (in grayscale) and move the mouse cursor to its center.
    Saves a screenshot for debugging.

    :param image_path: The path to the image file (e.g., "evernote2.png").
    :param confidence: The matching confidence (0.0 to 1.0, default 0.9).
    :param timeout: Maximum time (in seconds) to keep searching for the image.
    """
    # Load the template image in grayscale
    template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"Error: Could not load template image from {image_path}")
        return

    template_h, template_w = template.shape[:2]
    start_time = time.time()
    location = None

    # Continuously capture a screenshot, convert to grayscale, and search for the template.
    while time.time() - start_time < timeout:
        # Capture a screenshot using PyAutoGUI
        screenshot = pyautogui.screenshot()
        # Save screenshot for debugging (optional)
        screenshot.save("debug_screenshot.png")
        # Convert screenshot to a NumPy array, then to grayscale
        screenshot_np = np.array(screenshot)
        screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

        # Use template matching from OpenCV
        res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= confidence)
        if len(loc[0]) > 0:
            # Take the first matching location
            top_left = (loc[1][0], loc[0][0])
            bottom_right = (top_left[0] + template_w, top_left[1] + template_h)
            # Calculate the center of the found template
            center = (top_left[0] + template_w // 2, top_left[1] + template_h // 2)
            location = center
            break

        time.sleep(0.5)

    if location:
        print(f"Found image at {location}. Moving mouse there.")
        pyautogui.moveTo(location)
    else:
        print("Image not found on screen within the timeout period.")

if __name__ == "__main__":
    # Replace "evernote2.png" with the path to your image
    find_and_move("evernote3.png", confidence=0.9, timeout=10)