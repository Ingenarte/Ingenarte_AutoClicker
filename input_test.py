import time
import pyautogui

def get_clicks(value_str):
    """Convert a numeric string or word to an integer."""
    try:
        return int(value_str)
    except ValueError:
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
            # For a single key or text input, type it out.
            pyautogui.write(text)
            log_action(f"Keyboard input: {text}")
    else:
        log_action("Input step: Unknown input source.")

def log_action(message):
    """Log a message with a timestamp."""
    timestamp = time.strftime("%Y-%m-%d | %H:%M:%S")
    log_line = f"{timestamp} | {message}"
    print(log_line)

# Example usage:
if __name__ == "__main__":
    # Example configuration for a key combination:
    step_config = {
        "input": {
            "input_from": "Keyboard",
            "keyboard_ascii": "Command + V",  # Intended to simulate Copy on macOS
            "keyboard_repeat": "0",
            "mouse_click_qty": "",
            "mouse_event": "",
            "mouse_movement": ""
        }
    }
    # Replace these parameters with your actual tab and step number.
    process_input_step(step_config, step_number=1, tab_name="Tab 1")