import customtkinter as ctk
import time 
import pyautogui
import pyperclip
from pynput import mouse
import threading
import json
import tkinter as tk
from tkinter import filedialog
import datetime
import os
import subprocess
import sys
from openpyxl import load_workbook  
from modals import recursivity_modal
from modals.modal_input import open_input_modal 
from modals.image_modal import open_image_modal
from modals.data_modal import open_data_modal

import logging
logging.getLogger("PIL").setLevel(logging.DEBUG)

# -----------------------------
# Global configuration (will be loaded from run.json if it exists)
# -----------------------------
global_config = {}

# -----------------------------
# Logging function: prints and appends to run-log.txt
# -----------------------------
def log_action(message):
    """Append a log message with timestamp to run-log.txt and print it."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d | %H:%M:%S")
    log_line = f"{timestamp} | {message}"
    with open("run-log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(log_line + "\n")
    print(log_line)

# -----------------------------
# Processing functions for steps
# -----------------------------

def get_clicks(value_str):
    """Convert a numeric string or word to an integer."""
    try:
        # Try to convert directly if it's a numeric string
        return int(value_str)
    except ValueError:
        # Otherwise, map known number words to integers
        mapping = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10
        }
        return mapping.get(value_str.lower(), 1)

def process_input_step(step_config, step_number, tab_name):
    """
    Processes an input step for either mouse or keyboard actions.
    
    For keyboard input, if the 'keyboard_ascii' value contains a combination (delimited by " + "),
    the function will hold down any modifier keys (such as Command, Ctrl, Alt, Shift) while pressing
    the other keys, with a 200ms delay between the normal keys.
    """
    action = step_config.get("input", {})
    log_action(f"[Tab {tab_name} | Step {step_number}] Processing input: {action}")
    input_from = action.get("input_from", "").lower()

    if input_from == "mouse":
        pos = step_config.get("position", "")
        if pos:
            try:
                x_str, y_str = pos.split("x")
                x, y = int(x_str), int(y_str)
            except Exception as e:
                log_action(f"Error parsing position: {e}")
                return
            button = "left" if action.get("mouse_event", "Left").lower() == "left" else "right"
            value_str = action.get("mouse_click_qty", "1")
            clicks = get_clicks(value_str)
            pyautogui.click(x=x, y=y, clicks=clicks, button=button)
            log_action(f"Mouse clicked at ({x}, {y}) {clicks} time(s) with {button} button.")
        else:
            log_action("Input step: No position specified for mouse click.")

    elif input_from == "keyboard":
        text = action.get("keyboard_ascii", "")
        # If the text is a key combination (e.g. "Command + C")
        if " + " in text:
            # Split the combination into parts.
            keys = [key.strip() for key in text.split(" + ")]
            # Separate modifiers from normal keys.
            modifiers = []
            non_modifiers = []
            for key in keys:
                # On macOS, if the key is "Command" (or "Meta") use the name "command" for pyautogui.
                if key.lower() in ["shift", "ctrl", "alt", "command", "meta"]:
                    if key.lower() in ["command", "meta"]:
                        modifiers.append("command")
                    else:
                        modifiers.append(key.lower())
                else:
                    non_modifiers.append(key.lower())

            log_action(f"Processing key combination: modifiers={modifiers}, keys={non_modifiers}")
            # Press and hold all modifier keys.
            for mod in modifiers:
                pyautogui.keyDown(mod)
            # Press each non-modifier key with a short delay.
            for key in non_modifiers:
                pyautogui.press(key)
                time.sleep(0.2)
            # Release all modifier keys.
            for mod in modifiers:
                pyautogui.keyUp(mod)
            log_action(f"Keyboard combination pressed: {' + '.join(modifiers + non_modifiers)}")
        else:
             # For a single key, check if it's alphabetic.
            key = text.strip()
            # if key.isalpha() and len(key) == 1:
            #     key = key.lower()
            pyautogui.press(key)
            log_action(f"Keyboard input: {text}")
    else:
        log_action("Input step: Unknown input source.")

def process_image_step(step_config, step_number, tab_name):
    # Save a screenshot for debugging purposes.
    screenshot = pyautogui.screenshot()
    screenshot.save("debug_screenshot.png")
    
    action = step_config.get("image", {})
    log_action(f"[Tab {tab_name} | Step {step_number}] Processing image: {action}")
    image_path = action.get("image_path", "")
    if not image_path:
        log_action("Image step: No image path specified.")
        return

    # Get the confidence value.
    try:
        confidence = float(action.get("image_confidence", "1.0"))
    except Exception as e:
        log_action(f"Error parsing image_confidence: {e}. Using 1.0")
        confidence = 1.0

    # Get the timeout value.
    try:
        timeout = float(action.get("image_timeout", "0"))
    except Exception as e:
        log_action(f"Error parsing image_timeout: {e}. Using 0")
        timeout = 0

    start_time = time.time()
    location = None

    if timeout > 0:
        # Loop until the image is found or timeout expires.
        while (time.time() - start_time) < timeout:
            try:
                location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            except pyautogui.ImageNotFoundException:
                location = None
            if location:
                break
            time.sleep(0.5)
        if not location:
            log_action("WARNING: Image not found on screen within timeout period.")
            return
    else:
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        except pyautogui.ImageNotFoundException:
            location = None

    if location:
        center = pyautogui.center(location)
        # If image_wait is True, wait for the specified sleep time before clicking.
        if action.get("image_wait", False):
            try:
                wait_sleep = float(action.get("image_wait_sleep", "0"))
            except Exception as e:
                log_action(f"Error parsing image_wait_sleep: {e}. Using 0")
                wait_sleep = 0
            log_action(f"Waiting for {wait_sleep} seconds before clicking.")
            time.sleep(wait_sleep)
        # Move the mouse to the center of the located image.
        pyautogui.moveTo(center)
        log_action(f"Moved mouse to image at {center}.")
        # If image_click is True, perform a click.
        if action.get("image_click", False):
            # Determine which button to click.
            if "mouse_event" in action:
                button = "left" if action.get("mouse_event", "Left").lower() == "left" else "right"
            elif "image_click_LR" in action:
                button = "left" if action.get("image_click_LR", "Left").lower() == "left" else "right"
            else:
                button = "left"
            # Determine the number of clicks.
            try:
                clicks = int(action.get("mouse_click_qty", "1"))
            except ValueError:
                clicks = get_clicks(action.get("mouse_click_qty", "1"))
            pyautogui.click(clicks=clicks, button=button)
            log_action(f"Clicked {clicks} time(s) with {button} button at {center}.")
        else:
            log_action("Image click flag not set; no click performed.")
        # Wait after clicking if image_sleep is specified.
        try:
            sleep_time = float(action.get("image_sleep", "0"))
        except Exception as e:
            log_action(f"Error parsing image_sleep: {e}. Using 0")
            sleep_time = 0
        if sleep_time > 0:
            log_action(f"Sleeping for {sleep_time} seconds after clicking.")
            time.sleep(sleep_time)
    else:
        log_action(f"WARNING: Image not found on screen with confidence {confidence}.")


def process_data_step(step_config, step_number, tab_name):
    """
    Process a 'data' step by operating on an Excel file.
    Expected configuration keys:
      - data_path: The Excel file path.
      - data_cell: The cell (e.g., "A3") to operate on.
      - data_copy_paste: If equal to "Paste To" (case-insensitive), the clipboard contents are pasted into the cell.
                         If equal to "Copy To", the cell value is copied to the clipboard.
      - data_select_all: Boolean; if True, simulate a 'select all' keystroke.
      - Optionally, data_sheet to specify the sheet name. If not provided, the first sheet is used.
    """
    action = step_config.get("data", {})
    log_action(f"[Tab {tab_name} | Step {step_number}] Processing data: {action}")

    file_path = action.get("data_path", "")
    cell = action.get("data_cell", "")
    copy_paste_action = action.get("data_copy_paste", "")
    select_all = action.get("data_select_all", False)
    sheet_name = action.get("data_sheet", None)

    if not file_path or not os.path.exists(file_path):
        log_action("Data step: Invalid or missing file path.")
        return

    try:
        wb = load_workbook(file_path)
        if sheet_name is None:
            # Default to the first sheet if none specified.
            sheet_name = wb.sheetnames[0]
        if sheet_name not in wb.sheetnames:
            log_action(f"Sheet {sheet_name} not found in {file_path}.")
            return

        sheet = wb[sheet_name]

        if copy_paste_action.lower() == "paste to":
            # Paste clipboard content into the cell.
            clipboard_value = pyperclip.paste()
            sheet[cell].value = clipboard_value
            wb.save(file_path)
            log_action(f"Pasted clipboard value '{clipboard_value}' into cell {cell} in {sheet_name} of {file_path}.")
        elif copy_paste_action.lower() == "copy from":
            # Copy the cell's value to the clipboard.
            cell_value = sheet[cell].value
            pyperclip.copy(str(cell_value))
            log_action(f"Copied value '{cell_value}' from cell {cell} in {sheet_name} of {file_path} to clipboard.")
        else:
            log_action(f"Data step: Unknown data_copy_paste action '{copy_paste_action}'.")

        # If data_select_all is True, simulate a 'select all' keystroke.
        if select_all:
            if sys.platform == "darwin":
                pyautogui.hotkey("command", "a")
            else:
                pyautogui.hotkey("ctrl", "a")
            log_action("Executed select all command.")

    except Exception as e:
        log_action(f"Error processing data step: {e}")

def process_position_step(step_config, step_number, tab_name):
    pos = step_config.get("position", "")
    log_action(f"[Tab {tab_name} | Step {step_number}] Processing position: {pos}")
    if pos:
        try:
            x_str, y_str = pos.split("x")
            x, y = int(x_str), int(y_str)
            pyautogui.moveTo(x, y)
            log_action(f"Moved mouse to ({x}, {y}).")
        except Exception as e:
            log_action(f"Error processing position: {e}")
    else:
        log_action("Position step: No position provided.")

def process_step(tab_name, step_number, step_config):
    if "position" in step_config:
        process_position_step(step_config, step_number, tab_name)
    if "input" in step_config:
        process_input_step(step_config, step_number, tab_name)
    if "image" in step_config:
        process_image_step(step_config, step_number, tab_name)
    if "data" in step_config:
        process_data_step(step_config, step_number, tab_name)

def process_recursivity(rec_config):
    r_steps_str = rec_config.get("r_steps", "")
    r_repeat = rec_config.get("r_repeat", 1)
    if not r_steps_str:
        log_action("Recursivity: No steps specified.")
        return
    steps_to_repeat = [s.strip() for s in r_steps_str.split(",") if s.strip()]
    log_action(f"Recursivity: Repeating steps {', '.join(steps_to_repeat)} {r_repeat} times")
    for rep in range(1, r_repeat + 1):
        log_action(f"Recursivity iteration {rep} started.")
        for tab_name, steps in global_config.get("tab_n", {}).items():
            for step_key, step_config in steps.items():
                step_num = step_key.split("_")[1]
                if step_num in steps_to_repeat:
                    process_step(tab_name, step_num, step_config)
        log_action(f"Recursivity iteration {rep} completed.")

# -----------------------------
# Main processing function (run the script)
# -----------------------------
def run_script():
    log_action("RUN: Starting execution.")
    for tab_name in sorted(global_config.get("tab_n", {}).keys(), key=lambda t: int(t.split()[1])):
        log_action(f"RUN: Processing {tab_name}")
        steps = global_config["tab_n"][tab_name]
        for step_key in sorted(steps.keys(), key=lambda x: int(x.split('_')[1])):
            step_num = step_key.split("_")[1]
            step_config = steps[step_key]
            process_step(tab_name, step_num, step_config)
    if "recursivity" in global_config:
        process_recursivity(global_config["recursivity"])
    log_action("RUN: Execution completed.")

# -----------------------------
# "RUN" functionality: execute run_module.py synchronously (passing run.json as argument) and then rename run.json
# -----------------------------
def run_and_rename():
    log_action("RUN: Saving configuration to run.json...")
    run_filename = "run.json"
    try:
        with open(run_filename, "w", encoding="utf-8") as f:
            json.dump(global_config, f, ensure_ascii=False, indent=4, sort_keys=True)
        log_action(f"RUN: Configuration saved to {run_filename}.")
    except Exception as e:
        log_action(f"RUN: Error saving configuration: {e}")
        return

    log_action("RUN: Executing run_module.py with run.json as argument. This may take up to an hour...")
    try:
        # Call run_module.py with run.json as an argument.
        subprocess.run([sys.executable, "run_module.py", run_filename], check=True)
        log_action("RUN: run_module.py executed successfully.")
    except subprocess.CalledProcessError as e:
        log_action(f"RUN: Error executing run_module.py: {e}")
        return

    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"run_{timestamp}.json"
        os.rename(run_filename, new_filename)
        log_action(f"RUN: Configuration file renamed to {new_filename}.")
    except Exception as e:
        log_action(f"RUN: Failed to rename run.json: {e}")

    run_script()

# -----------------------------
# Main entry point (for the run module)
# -----------------------------
def main():
    # If no command-line argument is provided, default to "run.json"
    if len(sys.argv) < 2:
        config_file = "run.json"
    else:
        config_file = sys.argv[1]
        
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
            global global_config
            global_config = config
        log_action(f"Loaded configuration from {config_file}")
    except Exception as e:
        log_action(f"Error loading configuration from {config_file}: {e}")
        sys.exit(1)
    
    # Now call the processing function to execute the steps.
    run_script()

if __name__ == "__main__":
    main()