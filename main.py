import customtkinter as ctk
import pyautogui
import pyperclip
from pynput import mouse
import threading
import json
import tkinter as tk
from tkinter import filedialog
import threading
from modals.schedule_modal import open_schedule_modal
from modals.schedule_runner import schedule_runner
from modals import recursivity_modal
from modals.modal_input import open_input_modal  # Your modal implementations
from modals.image_modal import open_image_modal
from modals.data_modal import open_data_modal
from modals.repetition_modal import open_repetition_modal
import subprocess
import sys
import datetime
import os
import time







# Global variable to store the repetition interval (in seconds)
global_repetition_interval = None
# Global reference for the repetition button
global_repetition_btn = None
# Global variable to store the scheduled datetime.
global_schedule_time = None
# Global reference for the schedule button.
global_schedule_btn = None



### Listener HotKey for process stoping and coming back to main window

import threading
from pynput import keyboard

# ——————————————————————————————————————————————————————————————
# Master hotkey: Ctrl+Shift+Q para cancelar la ejecución
# ——————————————————————————————————————————————————————————————

stop_event = threading.Event()
_current_mods = set()

def _on_key_press(key):
    # guardamos modifier keys
    if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r,
               keyboard.Key.shift,  keyboard.Key.shift_r):
        _current_mods.add(key)
    # si están Ctrl+Shift y presionamos 'q'
    if ((keyboard.Key.ctrl_l in _current_mods or keyboard.Key.ctrl_r in _current_mods)
        and (keyboard.Key.shift in _current_mods or keyboard.Key.shift_r in _current_mods)
        and getattr(key, "char", "").lower() == "q"):
        stop_event.set()


def _on_key_release(key):
    if key in _current_mods:
        _current_mods.remove(key)

def start_master_listener():
    listener = keyboard.Listener(
        on_press=_on_key_press,
        on_release=_on_key_release
    )
    listener.daemon = True
    listener.start()

# Arrancamos el listener ANTES del mainloop
start_master_listener()

### ---- Listener HotKey for process stoping and coming back to main window





# -----------------------------
# CustomTkinter configuration
# -----------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# -----------------------------
# Main window
# -----------------------------
root = ctk.CTk()
root.update_idletasks()
icon_image = tk.PhotoImage(file="public/ingenarte_icon.png")
root.iconphoto(False, icon_image)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = int(screen_width * 0.35)   # 35% of screen width
window_height = int(screen_height * 0.70)  # 70% of screen height
pos_x = int(screen_width * 0.60)           # 60% from left edge
pos_y = int(screen_height * 0.20)          # 20% from top
root.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")
root.attributes('-alpha', 1)
root.title("Ingenarte AutoClicker")
root.resizable(True, True)

# -----------------------------
# Main container: divided into top frame, steps area, and tab bar
# -----------------------------
main_frame = ctk.CTkFrame(root)
main_frame.pack(fill="both", expand=True)

# Top frame for fixed controls (pointer, load config, and save config buttons)
top_frame = ctk.CTkFrame(main_frame)
top_frame.pack(side="top", fill="x", padx=10, pady=(10, 0))

# Steps area (draggable container)
draggable_frame = ctk.CTkFrame(main_frame, fg_color="#2E2E2E", corner_radius=20)
draggable_frame.pack(side="top", fill="both", expand=True, padx=10, pady=(0, 0))

# Tab bar (like a browser's)
tab_bar_height = 40  # fixed height
tabs_frame = ctk.CTkFrame(main_frame, height=tab_bar_height, fg_color="#444444")
tabs_frame.pack(side="bottom", fill="x", padx=10, pady=(0, 10))
tabs_frame.pack_propagate(0)

# -----------------------------
# Pointer, Load Config, and Save Config Buttons (in top_frame)
# -----------------------------
pointer_button = ctk.CTkButton(top_frame, text="Get Mouse Position", fg_color="#1F6AA5", command=lambda: read_position())
pointer_button.pack(side="left", padx=5, pady=5)

load_config_button = ctk.CTkButton(top_frame, text="Load Config", fg_color="#1F6AA5", command=lambda: load_config())
load_config_button.pack(side="left", padx=5, pady=5)

save_config_top_button = ctk.CTkButton(top_frame, text="Save Config", fg_color="#1F6AA5", command=lambda: save_config())
save_config_top_button.pack(side="left", padx=5, pady=5)

# -----------------------------
# Variables for window dragging
# -----------------------------
start_x = 0
start_y = 0
def start_drag(e):
    global start_x, start_y
    start_x = e.x
    start_y = e.y

def move_app(e):
    x = e.x_root - start_x
    y = e.y_root - start_y
    root.geometry(f"+{x}+{y}")

draggable_frame.bind('<Button-1>', start_drag)
draggable_frame.bind('<B1-Motion>', move_app)

# -----------------------------
# Global variables for click capture
# -----------------------------
reading_mode = False
current_callback = None

def capture_global_click():
    """Listen for a global click and execute the assigned callback."""
    def on_click(x, y, button, pressed):
        global reading_mode, current_callback
        if pressed and reading_mode and current_callback:
            current_callback(x, y)
            reading_mode = False
            return False
    from pynput import mouse
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

# -----------------------------
# "Read Position" functionality
# -----------------------------
def global_position_callback(x, y):
    position = f"{int(x)}x{int(y)}"
    pyperclip.copy(position)
    print(f"📍 Coordinates copied to clipboard: {position}")
    pointer_button.configure(text=position, fg_color="#333333")
    root.config(cursor="arrow")
    # Restore the window
    root.deiconify()
    # On Windows, maximize the window if desired.
    if sys.platform == "win32":
        root.state("zoomed")
    # On other platforms (macOS, Linux), you may simply deiconify.

def read_position():
    global reading_mode, current_callback
    if not reading_mode:
        pointer_button.configure(text="Reading...", fg_color="#FFA500")
        root.config(cursor="cross")
        # Hide the main window so the click is not blocked
        root.withdraw()
        reading_mode = True
        current_callback = global_position_callback
        threading.Thread(target=capture_global_click, daemon=True).start()

# -----------------------------
# Functionality for "Position" buttons for each step
# -----------------------------
def step_position_callback(x, y, button, entry, step_number):
    position = f"{int(x)}x{int(y)}"
    print(f"📍 Captured coordinates: {position}")
    def update():
        entry.delete(0, "end")
        entry.insert(0, position)
        button.configure(text="Position", fg_color="green")
        root.config(cursor="arrow")
        root.deiconify()
    tab_key = f"Tab {current_tab_index}"
    step_key = f"step_{step_number}"
    if tab_key in global_config["tab_n"]:
        if step_key not in global_config["tab_n"][tab_key]:
            global_config["tab_n"][tab_key][step_key] = {}
        global_config["tab_n"][tab_key][step_key]["position"] = position
    else:
        global_config["tab_n"][tab_key] = {step_key: {"position": position}}
    root.after(0, update)

def step_read_position(button, entry, step_number):
    global reading_mode, current_callback
    if not reading_mode:
        reading_mode = True
        root.iconify()
        current_callback = lambda x, y: step_position_callback(x, y, button, entry, step_number)
        button.configure(text="Reading...", fg_color="#FFA500")
        root.config(cursor="cross")
        threading.Thread(target=capture_global_click, daemon=True).start()

# -----------------------------
# Partial Save: Update entry to config on focus out.
# -----------------------------
def update_position_config(event, tab_key, step_number, entry):
    step_key = f"step_{step_number}"
    if tab_key not in global_config["tab_n"]:
        global_config["tab_n"][tab_key] = {}
    if step_key not in global_config["tab_n"][tab_key]:
        global_config["tab_n"][tab_key][step_key] = {}
    global_config["tab_n"][tab_key][step_key]["position"] = entry.get()
    print(f"Updated config for {tab_key} {step_key}: {entry.get()}")

# -----------------------------
# Global configuration and step_buttons dictionaries
# -----------------------------
global_config = {"tab_n": {}}
step_buttons = {}

# -----------------------------
# Modal callbacks for Input, Image, and Data
# -----------------------------
def input_callback(step_id, data):
    tab_key = f"Tab {current_tab_index}"
    if tab_key not in global_config["tab_n"]:
        global_config["tab_n"][tab_key] = {}
    step_key = f"step_{step_id}"
    global_config["tab_n"][tab_key][step_key] = global_config["tab_n"][tab_key].get(step_key, {})
    global_config["tab_n"][tab_key][step_key]["input"] = data
    print("Configuration updated for", tab_key, step_key)

    # if the modal payload still matches its defaults, do nothing
    if not _input_is_populated(data):
        return

    if tab_key in step_buttons and step_key in step_buttons[tab_key] and "input" in step_buttons[tab_key][step_key]:
        step_buttons[tab_key][step_key]["input"].configure(text="Input ✓", fg_color="green")

def image_callback(step_id, data):
    tab_key = f"Tab {current_tab_index}"
    if tab_key not in global_config["tab_n"]:
        global_config["tab_n"][tab_key] = {}
    step_key = f"step_{step_id}"
    global_config["tab_n"][tab_key][step_key] = global_config["tab_n"][tab_key].get(step_key, {})
    global_config["tab_n"][tab_key][step_key]["image"] = data
    print("Image configuration updated for", tab_key, step_key)
    
    # if the modal payload still matches its defaults, do nothing
    if not _image_is_populated(data):
        return

    if tab_key in step_buttons and step_key in step_buttons[tab_key] and "image" in step_buttons[tab_key][step_key]:
        step_buttons[tab_key][step_key]["image"].configure(text="Image ✓", fg_color="green")

def data_callback(step_id, data):
    tab_key = f"Tab {current_tab_index}"
    if tab_key not in global_config["tab_n"]:
        global_config["tab_n"][tab_key] = {}
    step_key = f"step_{step_id}"
    global_config["tab_n"][tab_key][step_key] = global_config["tab_n"][tab_key].get(step_key, {})
    global_config["tab_n"][tab_key][step_key]["data"] = data
    print("Data configuration updated for", tab_key, step_key)

        # if the modal payload still matches its defaults, do nothing
    if not _data_is_populated(data):
        return
    
    if tab_key in step_buttons and step_key in step_buttons[tab_key] and "data" in step_buttons[tab_key][step_key]:
        step_buttons[tab_key][step_key]["data"].configure(text="Data ✓", fg_color="green")

def open_input_for_step(step_id):
    tab_key = f"Tab {current_tab_index}"
    step_key = f"step_{step_id}"
    existing_data = None
    if tab_key in global_config["tab_n"]:
        existing_data = global_config["tab_n"][tab_key].get(step_key, {}).get("input")
    open_input_modal(step_id, input_callback, existing_data)

def open_image_for_step(step_id):
    tab_key = f"Tab {current_tab_index}"
    step_key = f"step_{step_id}"
    existing_data = None
    if tab_key in global_config["tab_n"]:
        existing_data = global_config["tab_n"][tab_key].get(step_key, {}).get("image")
    open_image_modal(step_id, image_callback, existing_data)

def open_data_for_step(step_id):
    tab_key = f"Tab {current_tab_index}"
    step_key = f"step_{step_id}"
    existing_data = None
    if tab_key in global_config["tab_n"]:
        existing_data = global_config["tab_n"][tab_key].get(step_key, {}).get("data")
    open_data_modal(step_id, data_callback, existing_data)

# -----------------------------
# Function to update steps view based on current tab
# -----------------------------
def clear_steps():
    global global_config
    # Clear the steps for all tabs (or for the current tab if preferred)
    global_config["tab_n"] = {}
    log_action("All steps cleared.")
    update_steps_view()


# ─── Defaults for each modal ───────────────────────────────────────────────────
_default_input = {
    "input_from":    "Keyboard",
    "keyboard_ascii": "Press the key or combination...",
    "keyboard_repeat":"0",
    "input_sleep":    "0",
    "mouse_event":    "",
    "mouse_click_qty":"",
    "mouse_movement":""
}

_default_image = {
    "image_click":      False,
    "image_click_LR":   "Left",
    "image_confidence": "1.00",
    "image_path":       "",
    "image_sleep":      "0",
    "image_timeout":    "0",
    "image_wait":       False,
    "image_wait_sleep": "0"
}

_default_data = {
    "data_cell":         "",
    "data_copy_paste":   "Copy From",
    "data_path":         "",
    "data_select_all":   False
}

def _input_is_populated(data):
    # True if _any_ value differs from our empty defaults
    return any(data.get(k) != v for k, v in _default_input.items())

def _image_is_populated(data):
    return any(data.get(k) != v for k, v in _default_image.items())

def _data_is_populated(data):
    return any(data.get(k) != v for k, v in _default_data.items())




def update_steps_view():
    global global_schedule_btn, global_repetition_btn 
    for widget in draggable_frame.winfo_children():
        widget.destroy()
    # Determine step range for current tab (for Tab i, steps from (i-1)*10+1 to i*10)
    start_step = (current_tab_index - 1) * 10 + 1
    end_step = current_tab_index * 10
    tab_key = f"Tab {current_tab_index}"
    
    # Create a header frame for the title and the "Clear Steps" button
    header_frame = ctk.CTkFrame(draggable_frame)
    header_frame.grid(row=0, column=0, columnspan=7, pady=10, sticky="ew")
    header_frame.grid_columnconfigure(0, weight=1)
    header_frame.grid_columnconfigure(1, weight=0)
    
    header = ctk.CTkLabel(header_frame, text=f"Steps for {tab_key}", font=("Arial", 16))
    header.grid(row=0, column=0, sticky="w")
    
    clear_button = ctk.CTkButton(header_frame, text="Clear Steps", fg_color="OrangeRed3", command=clear_steps)
    clear_button.grid(row=0, column=1, sticky="e", padx=5)
    
    # Now create the steps starting from row 1
    row = 1
    for step in range(start_step, end_step + 1):
        step_key = f"step_{step}"
        if step_key not in step_buttons.get(tab_key, {}):
            if tab_key not in step_buttons:
                step_buttons[tab_key] = {}
            step_buttons[tab_key][step_key] = {}
        step_label = ctk.CTkLabel(draggable_frame, text=f"Step {step}:", font=("Arial", 14))
        step_label.grid(row=row, column=0, padx=5, pady=5, sticky="w")
        # "Position" button and entry
        pos_btn = ctk.CTkButton(draggable_frame, text="Position", width=100, height=30)
        pos_btn.grid(row=row, column=1, padx=3, pady=5, sticky="ew")
        step_buttons[tab_key][step_key]["position"] = pos_btn
        pos_entry = ctk.CTkEntry(draggable_frame, width=90)
        pos_entry.grid(row=row, column=2, padx=3, pady=5, sticky="ew")
        pos_btn.configure(command=lambda b=pos_btn, t=pos_entry, s=step: step_read_position(b, t, s))
        pos_entry.bind("<FocusOut>", lambda event, tab=tab_key, s=step, e=pos_entry: update_position_config(event, tab, s, e))
        if tab_key in global_config["tab_n"] and step_key in global_config["tab_n"][tab_key]:
            saved = global_config["tab_n"][tab_key][step_key]
            if "position" in saved:
                pos_entry.insert(0, saved["position"])
                pos_btn.configure(text="Position", fg_color="green")
        # "Input" button
        inp_btn = ctk.CTkButton(draggable_frame, text="Input", width=80, height=30,
                                command=lambda s=step: open_input_for_step(s))
        inp_btn.grid(row=row, column=3, padx=3, pady=5, sticky="ew")
        step_buttons[tab_key][step_key]["input"] = inp_btn
        if tab_key in global_config["tab_n"] and step_key in global_config["tab_n"][tab_key]:
            saved = global_config["tab_n"][tab_key][step_key]
            if "input" in saved and saved["input"]:
                inp_btn.configure(text="Input ✓", fg_color="green")
        # "Image" button
        img_btn = ctk.CTkButton(draggable_frame, text="Image", width=80, height=30,
                                command=lambda s=step: open_image_for_step(s))
        img_btn.grid(row=row, column=4, padx=3, pady=5, sticky="ew")
        step_buttons[tab_key][step_key]["image"] = img_btn
        if tab_key in global_config["tab_n"] and step_key in global_config["tab_n"][tab_key]:
            saved = global_config["tab_n"][tab_key][step_key]
            if "image" in saved and saved["image"]:
                img_btn.configure(text="Image ✓", fg_color="green")
        # "Data" button
        dat_btn = ctk.CTkButton(draggable_frame, text="Data", width=80, height=30,
                                command=lambda s=step: open_data_for_step(s))
        dat_btn.grid(row=row, column=5, padx=3, pady=5, sticky="ew")
        step_buttons[tab_key][step_key]["data"] = dat_btn
        if tab_key in global_config["tab_n"] and step_key in global_config["tab_n"][tab_key]:
            saved = global_config["tab_n"][tab_key][step_key]
            if "data" in saved and saved["data"]:
                dat_btn.configure(text="Data ✓", fg_color="green")
        row += 1

    for i in range(6):
        draggable_frame.grid_columnconfigure(i, weight=1)
    # Recursivity and RUN buttons
    rec_color = "green" if "recursivity" in global_config else "#1F6AA5"
    rec_btn = ctk.CTkButton(draggable_frame, text="Recursivity", command=lambda: open_recursivity(), fg_color=rec_color)
    rec_btn.place(relx=0.2, rely=0.88, anchor="center")
    # rec_btn = ctk.CTkButton(draggable_frame, text="Schedule", command=lambda: open_recursivity(), fg_color=rec_color)
    # rec_btn.place(relx=0.5, rely=0.88, anchor="center")
    # rec_btn = ctk.CTkButton(draggable_frame, text="Repetition", command=lambda: open_recursivity(), fg_color=rec_color)
    # rec_btn.place(relx=0.8, rely=0.88, anchor="center")

    global_schedule_btn = ctk.CTkButton(
    draggable_frame, 
    text="Schedule", 
    command=lambda: open_schedule_modal(root, global_config, set_schedule_time),
    fg_color="green" if global_schedule_time else "#1F6AA5")
    global_schedule_btn.place(relx=0.5, rely=0.88, anchor="center")

    global_repetition_btn = ctk.CTkButton(
    draggable_frame,
    text="Repetition",
    command=lambda: open_repetition_modal(root, global_config, set_repetition_time),
    fg_color="green" if global_repetition_interval else "#1F6AA5")
    global_repetition_btn.place(relx=0.8, rely=0.88, anchor="center")

    run_btn = ctk.CTkButton(draggable_frame, text="RUN ▶", command=run_script, fg_color="OrangeRed3")
    run_btn.place(relx=0.8, rely=0.95, anchor="center")

# -----------------------------
# "RUN" functionality (for testing, prints global_config)
# -----------------------------


def log_action(message):
    """Append a log message with timestamp to run-log.txt and print it."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d | %H:%M:%S")
    log_line = f"{timestamp} | {message}"
    with open("run-log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(log_line + "\n")
    print(log_line)


def run_script():
    global in_repeater_mode

    # Sólo limpiamos stop_event si NO estamos en modo repetidor.
    # De este modo, cuando in_repeater_mode == True, no borramos la señal de Ctrl+Shift+Q.
    if not in_repeater_mode:
        stop_event.clear()

    # Ocultamos la UI y arrancamos la ejecución
    root.withdraw()
    root.update()
    log_action("RUN: Starting execution.")

    # 1) Guardar configuración a run.json
    run_filename = "run.json"
    try:
        with open(run_filename, "w", encoding="utf-8") as f:
            json.dump(global_config, f, ensure_ascii=False, indent=4, sort_keys=True)
        log_action(f"RUN: Configuration saved to {run_filename}.")
    except Exception as e:
        log_action(f"RUN: Error saving configuration: {e}")
        root.deiconify()
        return

    # 2) Último chequeo antes de lanzar: si ya se pulsó Ctrl+Shift+Q, volvemos a la UI
    if stop_event.is_set():
        log_action("🚩 Cancelled by hotkey before launch — returning to UI")
        root.deiconify()
        return

    # 3) Lanza run_module.py con stdout+stderr unidos, sin buffering
    log_action("RUN: Launching run_module.py …")
    proc = subprocess.Popen(
        [sys.executable, "-u", "run_module.py", run_filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # 4) Leer la salida en vivo y vigilar el hotkey
    for line in iter(proc.stdout.readline, ''):
        # Si en cualquier momento se presiona Ctrl+Shift+Q, detenemos el subproceso
        if stop_event.is_set():
            log_action("🚩 Hotkey pressed — terminating run_module.py")
            proc.terminate()
            break
        log_action("OUT: " + line.rstrip())

    proc.stdout.close()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()

    # 5) Informar código de retorno
    if proc.returncode != 0:
        log_action(f"RUN: run_module.py exited with code {proc.returncode}")
    else:
        log_action("RUN: run_module.py executed successfully.")

    # 6) Restaurar la ventana principal
    root.deiconify()
    log_action("Window restored.")



# -----------------------------
# "Save Config" functionality – open Save As dialog and write JSON file.
# -----------------------------
def save_config():
    filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
    if not filename:
        return
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(global_config, f, ensure_ascii=False, indent=4, sort_keys=True)
    print("⚙️ Configuration saved to", filename)

# -----------------------------
# Tab Bar functionality
# -----------------------------
tabs = ["Tab 1"]
current_tab_index = 1

def update_tab_bar():
    for widget in tabs_frame.winfo_children():
        widget.destroy()
    tabs_frame.update_idletasks()
    available_width = tabs_frame.winfo_width()
    num_tabs = len(tabs)
    padding = 10
    if num_tabs == 0:
        num_tabs = 1
    if num_tabs == 1:
        btn_width = max(int(available_width * 0.15), 50)
    else:
        btn_width = max(int((available_width - (num_tabs + 1) * padding) / num_tabs), 50)
        btn_width = min(btn_width, 120)
    for i, tab_name in enumerate(tabs, start=1):
        if i == current_tab_index:
            btn = ctk.CTkButton(tabs_frame, text=tab_name, fg_color="green", text_color="white",
                                command=lambda idx=i: select_tab(idx), width=btn_width)
        else:
            btn = ctk.CTkButton(tabs_frame, text=tab_name, fg_color="gray", text_color="black",
                                command=lambda idx=i: select_tab(idx), width=btn_width)
        btn.pack(side="left", padx=5, pady=5)
    plus_btn = ctk.CTkButton(tabs_frame, text="+", fg_color="green", command=add_tab, width=btn_width)
    plus_btn.pack(side="left", padx=5, pady=5)

def select_tab(index):
    root.focus_force()  # Force active widget to lose focus so FocusOut events trigger.
    global current_tab_index
    current_tab_index = index
    update_tab_bar()
    update_steps_view()

def add_tab():
    global current_tab_index
    new_tab = f"Tab {len(tabs) + 1}"
    tabs.append(new_tab)
    current_tab_index = len(tabs)
    update_tab_bar()
    if new_tab not in global_config["tab_n"]:
        global_config["tab_n"][new_tab] = {}
    update_steps_view()

update_tab_bar()
update_steps_view()




def set_schedule_time(scheduled_datetime):
    global global_schedule_time, global_schedule_btn
    global_schedule_time = scheduled_datetime
    # Update the button's appearance based on whether a schedule is set.
    if global_schedule_btn:
        if scheduled_datetime is None:
            global_schedule_btn.configure(fg_color="#1F6AA5")
        else:
            global_schedule_btn.configure(fg_color="green")
    # Only start the runner thread if we have a valid datetime.
    if scheduled_datetime is not None:
        import threading
        threading.Thread(
            target=schedule_runner,
            args=(global_schedule_time, run_script, global_config),
            daemon=True
        ).start()
    print(f"Program scheduled for {scheduled_datetime}.")


in_repeater_mode = False


def set_repetition_time(repetition_seconds):
    global global_repetition_interval, global_repetition_btn
    global repetition_thread, stop_repetition_event, in_repeater_mode

    global_repetition_interval = repetition_seconds

    # Update the button’s appearance
    if global_repetition_btn:
        if repetition_seconds is None:
            global_repetition_btn.configure(fg_color="#1F6AA5")
        else:
            global_repetition_btn.configure(fg_color="green")

    # If there is already a repetition thread running, stop it
    if 'repetition_thread' in globals() and repetition_thread.is_alive():
        stop_repetition_event.set()
        repetition_thread.join()

    # If a valid interval was provided, start a new thread that calls run_script() every N seconds
    if repetition_seconds:
        stop_repetition_event = threading.Event()

        def repeater():
            global in_repeater_mode

            # Enter “repeater mode” so run_script() does NOT clear stop_event
            in_repeater_mode = True

            while not stop_repetition_event.is_set():
                # If the user pressed Ctrl+Shift+Q at any time, break out
                if stop_event.is_set():
                    break

                log_action(f"Repetition: waiting {repetition_seconds}s for the next execution…")
                # Wait N seconds or until stop_repetition_event is set
                if stop_repetition_event.wait(timeout=repetition_seconds):
                    break

                # Before running, check the hotkey again
                if stop_event.is_set():
                    break

                # Call run_script(). Because in_repeater_mode == True, stop_event will not be cleared inside run_script()
                run_script()

            # When exiting the loop, leave “repeater mode”
            in_repeater_mode = False
            log_action("Repetition: stopped with Ctrl + Shift + Q.")

        repetition_thread = threading.Thread(target=repeater, daemon=True)
        repetition_thread.start()
        log_action(f"Repetition: started with interval {repetition_seconds}s.")
    else:
        log_action("Repetition: null interval, will not start repetition.")


# -----------------------------
# Recursivity functionality
# -----------------------------
def open_recursivity():
    # Pass previous rec configuration (if any) to the modal via an attribute.
    recursivity_modal.open_recursivity_modal.prev_rec = global_config.get("recursivity", {})
    # Aggregate all steps data from all tabs.
    steps_data_all = global_config.get("tab_n", {})
    result = recursivity_modal.open_recursivity_modal(steps_data_all, recursivity_modal.open_recursivity_modal.prev_rec)
    if result:
        global_config["recursivity"] = result
        update_steps_view()

# -----------------------------
# Load Config functionality
# -----------------------------
def load_config():
    filename = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if filename:
        with open(filename, "r", encoding="utf-8") as f:
            loaded_config = json.load(f)
        global global_config, tabs, current_tab_index, global_schedule_time, global_repetition_interval
        global_config = loaded_config
        # Set previous rec configuration for recursivity modal.
        recursivity_modal.open_recursivity_modal.prev_rec = global_config.get("recursivity", {})

        # If there's a schedule configuration, update global_schedule_time.
        if "schedule" in global_config:
            sched = global_config["schedule"]
            try:
                dt = datetime.datetime.strptime(f"{sched['date']} {sched['time']}", "%Y-%m-%d %H:%M:%S")
                global_schedule_time = dt
            except Exception as e:
                print("Error parsing schedule:", e)
                global_schedule_time = None
        else:
            global_schedule_time = None

        # If there's a repetition configuration, update global_repetition_interval.
        if "repetition" in global_config:
            rep = global_config["repetition"]
            try:
                hours = int(rep.get("hours", 0))
                minutes = int(rep.get("minutes", 0))
                seconds = int(rep.get("seconds", 0))
                total_seconds = hours * 3600 + minutes * 60 + seconds
                global_repetition_interval = total_seconds if total_seconds > 0 else None
            except Exception as e:
                print("Error parsing repetition:", e)
                global_repetition_interval = None
        else:
            global_repetition_interval = None

        # Update tabs if available.
        if "tab_n" in global_config:
            new_tabs = list(global_config["tab_n"].keys())
            new_tabs.sort(key=lambda x: int(x.split()[1]))
            tabs = new_tabs
            current_tab_index = 1

        update_tab_bar()
        update_steps_view()
        print("⚙️ Configuration loaded from", filename)

load_config_button.configure(command=load_config)

# -----------------------------
# Final initialization
# -----------------------------
def initialize_imkclient():
    root.focus_force()

root.after(100, initialize_imkclient)
root.mainloop() 