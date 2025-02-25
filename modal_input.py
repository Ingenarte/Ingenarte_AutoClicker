import customtkinter as ctk
import tkinter as tk
import logging
from components.utils import get_next_id
from components.label_checkbox_component import LabelCheckbox
# If you have your own CustomSwitch, comment out the dummy implementation below.
# Otherwise, this improved version will be used.

class CustomSwitch(ctk.CTkFrame):
    def __init__(self, master, options=[], button_width=120, button_height=40, **kwargs):
        super().__init__(master, **kwargs)
        self.var = tk.StringVar(value=options[0] if options else "")
        self.options = options
        self.buttons = []
        # Use grid so that each button is placed in its own column with equal weight.
        for i, opt in enumerate(options):
            btn = ctk.CTkButton(self,
                                text=opt,
                                command=lambda o=opt: self.select(o),
                                width=button_width,
                                height=button_height)
            btn.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            self.buttons.append(btn)
            self.grid_columnconfigure(i, weight=1)
        self.update_buttons()

    def select(self, option):
        self.var.set(option)
        self.update_buttons()

    def update_buttons(self):
        # Update each button's appearance based on the current selection.
        for btn in self.buttons:
            if btn.cget("text") == self.var.get():
                # Selected button style
                btn.configure(fg_color="green", text_color="white")
            else:
                # Unselected button style
                btn.configure(fg_color="gray", text_color="black")

    def get_value(self):
        return self.var.get()

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def open_input_modal(step_id, callback, existing_data=None):
    """
    Opens the input modal for a given step.
    When OK is pressed, a dictionary with the input data is passed to the callback.
    Optionally, existing_data is used to prefill the fields.
    """
    modal = ctk.CTkToplevel()
    title = "Input " + str(step_id)
    modal.title(title)
    modal.geometry("500x450")
    modal.grab_set()  # Block interaction with main window

    main_frame = ctk.CTkFrame(modal)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Centered title
    title_label = ctk.CTkLabel(main_frame, text=title, font=("Arial", 18))
    title_label.pack(pady=(0, 10))
    title_label.component_id = f"step_{step_id}_title"

    # Main switch for Keyboard/Mouse
    switch = CustomSwitch(main_frame, options=["Keyboard", "Mouse"])
    switch.pack(fill="x", pady=5)
    switch.component_id = f"step_{step_id}_switch"
    # Prefill switch if data exists
    if existing_data and "input_from" in existing_data:
        switch.var.set(existing_data["input_from"])
        switch.update_buttons()

    # Container for variable content (Keyboard or Mouse)
    content_frame = ctk.CTkFrame(main_frame)
    content_frame.pack(fill="both", expand=True, pady=5)

    # --- Keyboard Fields ---
    keyboard_frame = ctk.CTkFrame(content_frame)
    # Row: Key Entry
    kb_row = ctk.CTkFrame(keyboard_frame)
    kb_row.pack(fill="x", pady=5)
    key_label = ctk.CTkLabel(kb_row, text="Key:")
    key_label.pack(side="left")
    key_label.component_id = f"step_{step_id}_key_label"
    key_entry = ctk.CTkEntry(kb_row)
    default_key_text = "Press the key or key combination to be recorded"
    key_entry.insert(0, default_key_text)
    key_entry.pack(side="left", fill="x", expand=True, padx=5)
    key_entry.component_id = f"step_{step_id}_key_entry"

    def clear_default_text(event):
        if key_entry.get() == default_key_text:
            key_entry.delete(0, tk.END)
    key_entry.bind("<FocusIn>", clear_default_text)

    # Prefill key entry if existing_data is provided for Keyboard
    if existing_data and existing_data.get("input_from") == "Keyboard":
        key_entry.delete(0, tk.END)
        key_entry.insert(0, existing_data.get("keyboard_ascii", default_key_text))

    def on_key_press(event):
        combination = []
        # Detect modifiers (values may vary by system)
        if event.state & 0x0001:  # Shift
            combination.append("Shift")
        if event.state & 0x0004:  # Ctrl
            combination.append("Ctrl")
        if event.state & 0x0008:  # Alt
            combination.append("Alt")
        # Append pressed key
        combination.append(event.keysym.capitalize())
        
        combo_str = " + ".join(combination)
        key_entry.delete(0, tk.END)
        key_entry.insert(0, combo_str)
        logging.info("Combination detected: %s", combo_str)
        return "break"  # Prevent default insertion

    # Bind key event only when entry is focused
    def bind_key_event(event):
        key_entry.bind("<KeyPress>", on_key_press)

    def unbind_key_event(event):
        key_entry.unbind("<KeyPress>")

    key_entry.bind("<FocusIn>", bind_key_event)
    key_entry.bind("<FocusOut>", unbind_key_event)

    # Row: Repeat Spinbox
    kb_repeat = ctk.CTkFrame(keyboard_frame)
    kb_repeat.pack(fill="x", pady=5)
    repeat_label = ctk.CTkLabel(kb_repeat, text="Repeat [0-20]:")
    repeat_label.pack(side="left")
    repeat_label.component_id = f"step_{step_id}_repeat_label"
    kb_spin = tk.Spinbox(kb_repeat, from_=0, to=20)
    kb_spin.pack(side="left", padx=5)
    kb_spin.component_id = f"step_{step_id}_repeat_spinbox"
    if existing_data and existing_data.get("input_from") == "Keyboard":
        kb_spin.delete(0, tk.END)
        kb_spin.insert(0, existing_data.get("keyboard_repeat", "0"))

    # --- Mouse Fields ---
    mouse_frame = ctk.CTkFrame(content_frame)
    # Row: Mouse Button
    mouse_row = ctk.CTkFrame(mouse_frame)
    mouse_row.pack(fill="x", pady=5)
    mouse_label = ctk.CTkLabel(mouse_row, text="Mouse Button:")
    mouse_label.pack(side="left")
    mouse_label.component_id = f"step_{step_id}_mouse_label"
    mouse_switch = CustomSwitch(mouse_row, options=["Left", "Middle", "Right"])
    mouse_switch.pack(side="left", fill="x", expand=True, padx=5)
    mouse_switch.component_id = f"step_{step_id}_mouse_switch"
    if existing_data and existing_data.get("input_from") == "Mouse":
        mouse_switch.var.set(existing_data.get("mouse_event", "Left"))
        mouse_switch.update_buttons()

    # Row: Clicking selection
    mouse_clicking = ctk.CTkFrame(mouse_frame)
    mouse_clicking.pack(fill="x", pady=5)
    clicking_label = ctk.CTkLabel(mouse_clicking, text="Clicking:")
    clicking_label.pack(side="left")
    clicking_label.component_id = f"step_{step_id}_clicking_label"
    clicking_switch = CustomSwitch(mouse_clicking, options=["One", "Two", "Three"])
    clicking_switch.pack(side="left", fill="x", expand=True, padx=5)
    clicking_switch.component_id = f"step_{step_id}_clicking_switch"
    if existing_data and existing_data.get("input_from") == "Mouse":
        clicking_switch.var.set(existing_data.get("mouse_click_qty", "One"))
        clicking_switch.update_buttons()

    # Row: Mouse Movement
    mouse_moving = ctk.CTkFrame(mouse_frame)
    mouse_moving.pack(fill="x", pady=5)
    moving_label = ctk.CTkLabel(mouse_moving, text="Moving [-left | +right][px]:")
    moving_label.pack(side="left")
    moving_label.component_id = f"step_{step_id}_moving_label"
    initial_value = tk.IntVar(value=0)
    moving_spin = tk.Spinbox(mouse_moving, from_=-1000, to=1000, textvariable=initial_value)
    moving_spin.pack(side="left", padx=5)
    moving_spin.component_id = f"step_{step_id}_moving_spinbox"
    if existing_data and existing_data.get("input_from") == "Mouse":
        moving_spin.delete(0, tk.END)
        moving_spin.insert(0, existing_data.get("mouse_movement", "0"))

    # --- Sleep Field (for input_sleep) ---
    sleep_frame = ctk.CTkFrame(main_frame)
    sleep_frame.pack(fill="x", pady=5)
    sleep_label = ctk.CTkLabel(sleep_frame, text="Wait before next process [sec]:")
    sleep_label.pack(side="left")
    sleep_label.component_id = f"step_{step_id}_sleep_label"
    wait_spin = tk.Spinbox(sleep_frame, from_=0, to=60)
    wait_spin.pack(side="left", padx=5)
    wait_spin.component_id = f"step_{step_id}_wait_spinbox"
    if existing_data:
        wait_spin.delete(0, tk.END)
        wait_spin.insert(0, existing_data.get("input_sleep", "0"))

    # Update content frame based on the main switch selection
    def update_modal_fields(*args):
        for widget in content_frame.winfo_children():
            widget.forget()
        logging.debug("Main switch value: %s", switch.get_value())
        if switch.get_value() == "Keyboard":
            keyboard_frame.pack(fill="both", expand=True, pady=5)
        else:
            mouse_frame.pack(fill="both", expand=True, pady=5)
    switch.var.trace("w", update_modal_fields)
    update_modal_fields()

    # When OK is pressed, collect the data and invoke the callback.
    def on_ok():
        mode = switch.get_value()
        data = {}
        if mode == "Keyboard":
            data["input_from"] = "Keyboard"
            data["keyboard_ascii"] = key_entry.get()
            data["keyboard_repeat"] = kb_spin.get()
            data["mouse_event"] = ""
            data["mouse_click_qty"] = ""
            data["mouse_movement"] = ""
        else:
            data["input_from"] = "Mouse"
            data["mouse_event"] = mouse_switch.get_value()  # Assumes CustomSwitch provides get_value()
            data["mouse_click_qty"] = clicking_switch.get_value()
            data["mouse_movement"] = moving_spin.get()
            data["keyboard_ascii"] = ""
            data["keyboard_repeat"] = ""
        data["input_sleep"] = wait_spin.get()
        logging.info("Collected data for step %s: %s", step_id, data)
        callback(step_id, data)
        modal.destroy()

    ok_button = ctk.CTkButton(main_frame, text="Ok", command=on_ok)
    ok_button.pack(side="right",pady=10)

    modal.mainloop()

if __name__ == '__main__':
    root = tk.Tk()
    def dummy_callback(step_id, data):
         logging.info("Step %s data: %s", step_id, data)
    open_input_modal(1, dummy_callback)
    root.mainloop()