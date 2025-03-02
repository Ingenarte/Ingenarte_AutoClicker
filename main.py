import customtkinter as ctk
import pyautogui
import pyperclip
from pynput import mouse
import threading
import json
import tkinter as tk
from tkinter import filedialog
import recursivity_modal  # This module must define open_recursivity_modal(steps_data_all, prev_rec)
from modal_input import open_input_modal  # Your modal implementations
from image_modal import open_image_modal
from data_modal import open_data_modal
import subprocess
import sys
import datetime
import os

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
pointer_button = ctk.CTkButton(top_frame, text="Read Position", fg_color="#1F6AA5", command=lambda: read_position())
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

def read_position():
    global reading_mode, current_callback
    if not reading_mode:
        pointer_button.configure(text="Reading...", fg_color="#FFA500")
        root.config(cursor="cross")
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
def update_steps_view():
    for widget in draggable_frame.winfo_children():
        widget.destroy()
    # Determine step range for current tab (for Tab i, steps from (i-1)*10+1 to i*10)
    start_step = (current_tab_index - 1) * 10 + 1
    end_step = current_tab_index * 10
    tab_key = f"Tab {current_tab_index}"
    if tab_key not in step_buttons:
        step_buttons[tab_key] = {}
    header = ctk.CTkLabel(draggable_frame, text=f"Steps for {tab_key}", font=("Arial", 16))
    header.grid(row=0, column=0, columnspan=6, pady=10)
    row = 1
    for step in range(start_step, end_step + 1):
        step_key = f"step_{step}"
        if step_key not in step_buttons[tab_key]:
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
    rec_btn.place(relx=0.8, rely=0.88, anchor="center")
    run_btn = ctk.CTkButton(draggable_frame, text="RUN ▶", command=run_script, fg_color="OrangeRed3")
    run_btn.place(relx=0.8, rely=0.95, anchor="center")

# -----------------------------
# "RUN" functionality (for testing, prints global_config)
# -----------------------------
def run_script():
    print("RUN: Starting execution.")

    # Save the current configuration to run.json
    run_filename = "run.json"
    try:
        with open(run_filename, "w", encoding="utf-8") as f:
            json.dump(global_config, f, ensure_ascii=False, indent=4, sort_keys=True)
        print(f"RUN: Configuration saved to {run_filename}.")
    except Exception as e:
        print(f"RUN: Error saving configuration: {e}")
        return

    # Execute run_module.py synchronously (blocking until finished)
    try:
        print("RUN: Executing run_module.py. This may take up to an hour...")
        subprocess.run([sys.executable, "run_module.py", run_filename], check=True)
        print("RUN: run_module.py executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"RUN: Error executing run_module.py: {e}")
        return

    # Rename run.json to include a timestamp
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"run_{timestamp}.json"
        os.rename(run_filename, new_filename)
        print(f"RUN: Configuration file renamed to {new_filename}.")
    except Exception as e:
        print(f"RUN: Error renaming configuration file: {e}")

    print("RUN: Execution completed.")

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
        global global_config, tabs, current_tab_index
        global_config = loaded_config
        # Set previous rec configuration for recursivity modal.
        recursivity_modal.open_recursivity_modal.prev_rec = global_config.get("recursivity", {})
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