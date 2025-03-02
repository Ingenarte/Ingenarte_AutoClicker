import customtkinter as ctk
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
from openpyxl import load_workbook  # For data processing

# Import your other modules (ensure these are correctly implemented)
import recursivity_modal  # must provide open_recursivity_modal(steps_data_all, prev_rec)
from modal_input import open_input_modal
from image_modal import open_image_modal
from data_modal import open_data_modal

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
def process_input_step(step_config, step_number, tab_name):
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
            try:
                clicks = int(action.get("mouse_click_qty", "1"))
            except:
                clicks = 1
            pyautogui.click(x=x, y=y, clicks=clicks, button=button)
            log_action(f"Mouse clicked at ({x}, {y}) {clicks} time(s) with {button} button.")
        else:
            log_action("Input step: No position specified for mouse click.")
    elif input_from == "keyboard":
        text = action.get("keyboard_ascii", "")
        pyautogui.write(text)
        log_action(f"Keyboard input: {text}")
    else:
        log_action("Input step: Unknown input source.")

def process_image_step(step_config, step_number, tab_name):
    action = step_config.get("image", {})
    log_action(f"[Tab {tab_name} | Step {step_number}] Processing image: {action}")
    image_path = action.get("image_path", "")
    if image_path:
        try:
            confidence = float(action.get("image_confidence", "1.0"))
        except:
            confidence = 1.0
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            center = pyautogui.center(location)
            pyautogui.click(center)
            log_action(f"Clicked on image at {center}.")
        else:
            log_action("Image not found on screen.")
    else:
        log_action("Image step: No image path specified.")

def process_data_step(step_config, step_number, tab_name):
    action = step_config.get("data", {})
    log_action(f"[Tab {tab_name} | Step {step_number}] Processing data: {action}")
    file_path = action.get("file_path", "")
    sheet_name = action.get("sheet_name", "")
    cell = action.get("cell", "")
    value = action.get("value", "")
    if file_path and os.path.exists(file_path):
        try:
            wb = load_workbook(file_path)
            if sheet_name in wb.sheetnames:
                sheet = wb[sheet_name]
                sheet[cell] = value
                wb.save(file_path)
                log_action(f"Updated {cell} in {sheet_name} of {file_path} with '{value}'.")
            else:
                log_action(f"Sheet {sheet_name} not found in {file_path}.")
        except Exception as e:
            log_action(f"Error processing data step: {e}")
    else:
        log_action("Data step: Invalid or missing file path.")

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