import customtkinter as ctk
import pyautogui
import pyperclip
from pynput import mouse
import threading
from modal_input import open_input_modal  # Your modal implementations
from image_modal import open_image_modal
from data_modal import open_data_modal
import tkinter as tk

# CustomTkinter configuration
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Create main window
root = ctk.CTk()
root.update_idletasks()

# Dimensions and position of the window
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = int(screen_width * 0.30)   # 30% of screen width
window_height = int(screen_height * 0.60)  # 60% of screen height
pos_x = int(screen_width * 0.60)           # 60% from left edge
pos_y = int(screen_height * 0.20)          # 20% from top
root.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")
root.attributes('-alpha', 1)
root.title("Ingenarte AutoClicker")
root.resizable(True, True)

# Variables for dragging the window
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

# Draggable main frame
draggable_frame = ctk.CTkFrame(root, fg_color="#2E2E2E", corner_radius=20)
draggable_frame.pack(fill="both", expand=True)
draggable_frame.bind('<Button-1>', start_drag)
draggable_frame.bind('<B1-Motion>', move_app)

# --- Global variables for click capture ---
reading_mode = False         # True when waiting for a global click
current_callback = None      # Function to execute on global click

def capture_global_click():
    """Listen for a global click and execute the assigned callback."""
    def on_click(x, y, button, pressed):
        global reading_mode, current_callback
        if pressed and reading_mode and current_callback:
            current_callback(x, y)
            reading_mode = False
            return False  # stop listener
    from pynput import mouse
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

# --- Global "Read Position" functionality ---
def global_position_callback(x, y):
    position = f"{int(x)}x{int(y)}"
    pyperclip.copy(position)
    print(f"📍 Coordinates copied to clipboard: {position}")
    pointer_button.configure(text=position, fg_color="#333333")
    root.config(cursor="arrow")

def read_position():
    """Function for the global 'Read Position' button."""
    global reading_mode, current_callback
    if not reading_mode:
        pointer_button.configure(text="Reading...", fg_color="#FFA500")
        root.config(cursor="cross")
        reading_mode = True
        current_callback = global_position_callback
        threading.Thread(target=capture_global_click, daemon=True).start()

# Global "Read Position" button
pointer_button = ctk.CTkButton(
    draggable_frame, 
    text="Read Position", 
    command=read_position, 
    fg_color="#1F6AA5"
)
pointer_button.place(relx=0.3, rely=0.05, anchor="w")

# --- Functionality for "Position" buttons in each step ---
def step_position_callback(x, y, button, entry):
    position = f"{int(x)}x{int(y)}"
    print(f"📍 Captured coordinates: {position}")
    def update():
        entry.delete(0, "end")
        entry.insert(0, position)
        button.configure(text="Position", fg_color="green")
        root.config(cursor="arrow")
        root.deiconify()  # restore window if minimized
    root.after(0, update)

def step_read_position(button, entry):
    """Activate global click capture for a step and minimize window."""
    global reading_mode, current_callback
    if not reading_mode:
        reading_mode = True
        root.iconify()  # minimize window
        current_callback = lambda x, y: step_position_callback(x, y, button, entry)
        button.configure(text="Reading...", fg_color="#FFA500")
        root.config(cursor="cross")
        threading.Thread(target=capture_global_click, daemon=True).start()

# --- Global configuration dictionary ---
global_config = {"tab_n": {}}
# Dictionary to hold button references for each step
step_buttons = {}

def input_callback(step_id, data):
    """Update the global configuration when the input modal is closed."""
    step_key = f"step_{step_id}"
    if step_key not in global_config["tab_n"]:
        global_config["tab_n"][step_key] = {}
    global_config["tab_n"][step_key]["input"] = data
    print("Configuration updated for", step_key)
    print(global_config)
    # Update the "Input" button's background
    if step_key in step_buttons and "input" in step_buttons[step_key]:
        step_buttons[step_key]["input"].configure(fg_color="green")

def image_callback(step_id, data):
    """Update the global configuration when the image modal is closed."""
    step_key = f"step_{step_id}"
    if step_key not in global_config["tab_n"]:
        global_config["tab_n"][step_key] = {}
    global_config["tab_n"][step_key]["image"] = data
    print("Image configuration updated for", step_key)
    print(global_config)
    # Update the "Image" button's background
    if step_key in step_buttons and "image" in step_buttons[step_key]:
        step_buttons[step_key]["image"].configure(fg_color="green")

def data_callback(step_id, data):
    """Update the global configuration when the data modal is closed."""
    step_key = f"step_{step_id}"
    if step_key not in global_config["tab_n"]:
        global_config["tab_n"][step_key] = {}
    global_config["tab_n"][step_key]["data"] = data
    print("Data configuration updated for", step_key)
    print(global_config)
    # Update the "Data" button's background
    if step_key in step_buttons and "data" in step_buttons[step_key]:
        step_buttons[step_key]["data"].configure(fg_color="green")

def open_input_for_step(step_id):
    """Open the input modal for a given step, preloading existing data if available."""
    step_key = f"step_{step_id}"
    existing_data = None
    if step_key in global_config["tab_n"]:
        existing_data = global_config["tab_n"][step_key].get("input")
    open_input_modal(step_id, input_callback, existing_data)

def open_image_for_step(step_id):
    """Open the image modal for a given step, preloading existing image data if available."""
    step_key = f"step_{step_id}"
    existing_data = None
    if step_key in global_config["tab_n"]:
        existing_data = global_config["tab_n"][step_key].get("image")
    open_image_modal(step_id, image_callback, existing_data)

def open_data_for_step(step_id):
    """Open the data modal for a given step, preloading existing data if available."""
    step_key = f"step_{step_id}"
    existing_data = None
    if step_key in global_config["tab_n"]:
        existing_data = global_config["tab_n"][step_key].get("data")
    open_data_modal(step_id, data_callback, existing_data)

# --- Interface: Create 10 steps ---
empty_label = ctk.CTkLabel(draggable_frame, text="")
empty_label.grid(row=0, column=0, pady=30)

# Create buttons for each step and store their references
for step in range(1, 11):
    step_key = f"step_{step}"
    # Create a container dictionary for this step's buttons
    step_buttons[step_key] = {}

    # Step label
    step_label = ctk.CTkLabel(draggable_frame, text=f"Step {step}:", font=("Arial", 14))
    step_label.grid(row=step, column=0, padx=5, pady=5, sticky="w")

    # "Position" button and position entry
    pos_btn = ctk.CTkButton(draggable_frame, text="Position", width=100, height=30)
    pos_btn.grid(row=step, column=1, padx=3, pady=5, sticky="ew")
    # Store the position button reference
    step_buttons[step_key]["position"] = pos_btn

    position_textbox = ctk.CTkEntry(draggable_frame, width=90)
    position_textbox.grid(row=step, column=2, padx=3, pady=5, sticky="ew")
    pos_btn.configure(
        command=lambda b=pos_btn, t=position_textbox: step_read_position(b, t)
    )

    # "Input" button
    inp_btn = ctk.CTkButton(draggable_frame, text="Input", width=80, height=30,
                            command=lambda s=step: open_input_for_step(s))
    inp_btn.grid(row=step, column=3, padx=3, pady=5, sticky="ew")
    step_buttons[step_key]["input"] = inp_btn

    # "Image" button
    img_btn = ctk.CTkButton(draggable_frame, text="Image", width=80, height=30,
                            command=lambda s=step: open_image_for_step(s))
    img_btn.grid(row=step, column=4, padx=3, pady=5, sticky="ew")
    step_buttons[step_key]["image"] = img_btn

    # "Data" button
    dat_btn = ctk.CTkButton(draggable_frame, text="Data", width=80, height=30,
                            command=lambda s=step: open_data_for_step(s))
    dat_btn.grid(row=step, column=5, padx=3, pady=5, sticky="ew")
    step_buttons[step_key]["data"] = dat_btn

# Adjust columns to distribute space evenly.
for i in range(6):
    draggable_frame.grid_columnconfigure(i, weight=1)

# "Save Config" button (original functionality)
save_button = ctk.CTkButton(draggable_frame, text="Save Config",
                            command=lambda: print("⚙️ Configuration saved"))
save_button.place(relx=0.5, rely=0.95, anchor="center")

def initialize_imkclient():
    root.focus_force()

root.after(100, initialize_imkclient)
root.mainloop()