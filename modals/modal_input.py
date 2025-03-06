import customtkinter as ctk
import tkinter as tk
import logging

# If you have your own CustomSwitch or LabelCheckbox, you can remove the dummy definitions below.
# -------------------------------------------------------------------------
# DUMMY IMPLEMENTATIONS: CustomSwitch, if you already have it, remove this.
class CustomSwitch(ctk.CTkFrame):
    def __init__(self, master, options=[], button_width=120, button_height=40, **kwargs):
        super().__init__(master, **kwargs)
        self.var = tk.StringVar(value=options[0] if options else "")
        self.options = options
        self.buttons = []
        for i, opt in enumerate(options):
            btn = ctk.CTkButton(
                self,
                text=opt,
                command=lambda o=opt: self.select(o),
                width=button_width,
                height=button_height
            )
            btn.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            self.buttons.append(btn)
            self.grid_columnconfigure(i, weight=1)
        self.update_buttons()

    def select(self, option):
        self.var.set(option)
        self.update_buttons()

    def update_buttons(self):
        for btn in self.buttons:
            if btn.cget("text") == self.var.get():
                btn.configure(fg_color="green", text_color="white")
            else:
                btn.configure(fg_color="gray", text_color="black")

    def get_value(self):
        return self.var.get()

# -------------------------------------------------------------------------
# Logging Configuration
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def open_input_modal(step_id, callback, existing_data=None):
    """
    Opens the input modal for a given step (Keyboard or Mouse).
    When OK is pressed, a dictionary with the input data is passed to 'callback'.
    'existing_data' can be used to prefill the fields if editing an existing step.
    """
    # We'll store pressed modifiers in this dict:
    modifiers_pressed = {
        "Shift": False,
        "Ctrl":  False,
        "Alt":   False,
        "Cmd":   False  # For macOS Command/Meta
    }

    modal = ctk.CTkToplevel()
    title = f"Input {step_id}"
    modal.title(title)
    modal.geometry("500x450")
    modal.grab_set()  # Make it modal

    main_frame = ctk.CTkFrame(modal)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Title
    title_label = ctk.CTkLabel(main_frame, text=title, font=("Arial", 18))
    title_label.pack(pady=(0, 10))

    # Switch: Keyboard vs Mouse
    switch = CustomSwitch(main_frame, options=["Keyboard", "Mouse"])
    switch.pack(fill="x", pady=5)
    # Prefill if existing_data
    if existing_data and existing_data.get("input_from"):
        switch.var.set(existing_data["input_from"])
        switch.update_buttons()

    # Container for the variable content
    content_frame = ctk.CTkFrame(main_frame)
    content_frame.pack(fill="both", expand=True, pady=5)

    # --- KEYBOARD FRAME ---
    keyboard_frame = ctk.CTkFrame(content_frame)

    # Keyboard "Key" row
    kb_key_row = ctk.CTkFrame(keyboard_frame)
    kb_key_row.pack(fill="x", pady=5)
    key_label = ctk.CTkLabel(kb_key_row, text="Key:")
    key_label.pack(side="left")
    key_entry = ctk.CTkEntry(kb_key_row)
    default_key_text = "Press the key or combination..."
    key_entry.insert(0, default_key_text)
    key_entry.pack(side="left", fill="x", expand=True, padx=5)

    # If existing_data has keyboard_ascii, prefill
    if existing_data and existing_data.get("input_from") == "Keyboard":
        key_entry.delete(0, tk.END)
        key_entry.insert(0, existing_data.get("keyboard_ascii", default_key_text))

    # Keyboard spinbox for "Repeat"
    kb_repeat_frame = ctk.CTkFrame(keyboard_frame)
    kb_repeat_frame.pack(fill="x", pady=5)
    repeat_label = ctk.CTkLabel(kb_repeat_frame, text="Repeat [0-20]:")
    repeat_label.pack(side="left")
    kb_repeat_spin = tk.Spinbox(kb_repeat_frame, from_=0, to=20)
    kb_repeat_spin.pack(side="left", padx=5)
    # If existing_data has a keyboard_repeat
    if existing_data and existing_data.get("input_from") == "Keyboard":
        kb_repeat_spin.delete(0, tk.END)
        kb_repeat_spin.insert(0, existing_data.get("keyboard_repeat", "0"))

    # --- MOUSE FRAME ---
    mouse_frame = ctk.CTkFrame(content_frame)

    # Mouse row: which button?
    mouse_row = ctk.CTkFrame(mouse_frame)
    mouse_row.pack(fill="x", pady=5)
    mouse_label = ctk.CTkLabel(mouse_row, text="Mouse Button:")
    mouse_label.pack(side="left")
    mouse_switch = CustomSwitch(mouse_row, options=["Left", "Middle", "Right"])
    mouse_switch.pack(side="left", fill="x", expand=True, padx=5)
    if existing_data and existing_data.get("input_from") == "Mouse":
        mouse_switch.var.set(existing_data.get("mouse_event", "Left"))
        mouse_switch.update_buttons()

    # Mouse row: Clicking (One/Two/Three)
    mouse_click_frame = ctk.CTkFrame(mouse_frame)
    mouse_click_frame.pack(fill="x", pady=5)
    click_label = ctk.CTkLabel(mouse_click_frame, text="Clicking:")
    click_label.pack(side="left")
    clicking_switch = CustomSwitch(mouse_click_frame, options=["One", "Two", "Three"])
    clicking_switch.pack(side="left", fill="x", expand=True, padx=5)
    if existing_data and existing_data.get("input_from") == "Mouse":
        clicking_switch.var.set(existing_data.get("mouse_click_qty", "One"))
        clicking_switch.update_buttons()

    # Mouse row: Movement
    mouse_move_frame = ctk.CTkFrame(mouse_frame)
    mouse_move_frame.pack(fill="x", pady=5)
    move_label = ctk.CTkLabel(mouse_move_frame, text="Moving [-left/+right px]:")
    move_label.pack(side="left")
    initial_value = tk.IntVar(value=0)
    move_spin = tk.Spinbox(mouse_move_frame, from_=-1000, to=1000, textvariable=initial_value)
    move_spin.pack(side="left", padx=5)
    if existing_data and existing_data.get("input_from") == "Mouse":
        move_spin.delete(0, tk.END)
        move_spin.insert(0, existing_data.get("mouse_movement", "0"))

    # Sleep (for both modes)
    sleep_frame = ctk.CTkFrame(main_frame)
    sleep_frame.pack(fill="x", pady=5)
    sleep_label = ctk.CTkLabel(sleep_frame, text="Wait before next process [sec]:")
    sleep_label.pack(side="left")
    sleep_spin = tk.Spinbox(sleep_frame, from_=0, to=60)
    sleep_spin.pack(side="left", padx=5)
    if existing_data:
        sleep_spin.delete(0, tk.END)
        sleep_spin.insert(0, existing_data.get("input_sleep", "0"))

    # -------------
    # KEY CAPTURE
    # -------------
    # We store pressed modifiers in "modifiers_pressed".
    # We'll do on <KeyPress> for storing state, on <KeyRelease> for building the combo.

    def on_key_press(event):
        """Handle modifier state toggling on key press."""
        # Common keysyms for Shift, Control, Alt(Option on mac), Command (Meta_L/Meta_R).
        if event.keysym in ("Shift_L", "Shift_R"):
            modifiers_pressed["Shift"] = True
        elif event.keysym in ("Control_L", "Control_R", "Ctrl_L", "Ctrl_R"):
            modifiers_pressed["Ctrl"] = True
        elif event.keysym in ("Alt_L", "Alt_R", "Option_l", "Option_r"):
            modifiers_pressed["Alt"] = True
        elif event.keysym in ("Meta_L", "Meta_R", "Command"):
            # If we see Command or Meta, treat that as "Cmd".
            modifiers_pressed["Cmd"] = True
        # Return nothing; no insertion by default for now
        return "break"

    def on_key_release(event):
        """Build the final combination on key release if it's not a pure modifier."""
        # If the released key is purely a modifier, we just set it to false.
        if event.keysym in ("Shift_L", "Shift_R"):
            modifiers_pressed["Shift"] = False
            return "break"
        elif event.keysym in ("Control_L", "Control_R", "Ctrl_L", "Ctrl_R"):
            modifiers_pressed["Ctrl"] = False
            return "break"
        elif event.keysym in ("Alt_L", "Alt_R", "Option_l", "Option_r"):
            modifiers_pressed["Alt"] = False
            return "break"
        elif event.keysym in ("Meta_L", "Meta_R", "Command"):
            modifiers_pressed["Cmd"] = False
            return "break"
        # Otherwise, it's a "normal" key release, so build the combo:
        combo = []
        # If we detect Command, we prefer that instead of Alt or Ctrl.
        # On mac we might see both "Alt" and "Cmd" if user pressed Option + Command, etc.
        # Adjust logic as needed.
        if modifiers_pressed["Cmd"]:
            combo.append("Command")
        else:
            if modifiers_pressed["Ctrl"]:
                combo.append("Ctrl")
            if modifiers_pressed["Alt"]:
                combo.append("Alt")
        if modifiers_pressed["Shift"]:
            combo.append("Shift")

        # The key symbol
        # `event.keysym` might be 'c' or 'C'; let's unify it:
        final_key = event.keysym.capitalize()
        combo.append(final_key)

        combo_str = " + ".join(combo)
        logging.info("Key release combination: %s", combo_str)

        key_entry.delete(0, tk.END)
        key_entry.insert(0, combo_str)

        # By default, do not re-insert anything
        return "break"

    # Bind the key press and release to the key_entry
    def bind_keyboard_capture(*_):
        key_entry.bind("<KeyPress>", on_key_press)
        key_entry.bind("<KeyRelease>", on_key_release)

    def unbind_keyboard_capture(*_):
        key_entry.unbind("<KeyPress>")
        key_entry.unbind("<KeyRelease>")

    # FocusIn: Start capturing, FocusOut: Stop capturing
    key_entry.bind("<FocusIn>", bind_keyboard_capture)
    key_entry.bind("<FocusOut>", unbind_keyboard_capture)

    # -------------
    # Switch logic to show keyboard_frame or mouse_frame
    def update_modal_fields(*_):
        for widget in content_frame.winfo_children():
            widget.forget()
        if switch.get_value() == "Keyboard":
            keyboard_frame.pack(fill="both", expand=True, pady=5)
        else:
            mouse_frame.pack(fill="both", expand=True, pady=5)

    switch.var.trace_add("write", update_modal_fields)
    update_modal_fields()

    # -------------
    # OK button
    def on_ok():
        mode = switch.get_value()
        data = {}
        if mode == "Keyboard":
            data["input_from"] = "Keyboard"
            data["keyboard_ascii"] = key_entry.get()
            data["keyboard_repeat"] = kb_repeat_spin.get()
            data["mouse_event"] = ""
            data["mouse_click_qty"] = ""
            data["mouse_movement"] = ""
        else:
            data["input_from"] = "Mouse"
            data["mouse_event"] = mouse_switch.get_value()
            data["mouse_click_qty"] = clicking_switch.get_value()
            data["mouse_movement"] = move_spin.get()
            data["keyboard_ascii"] = ""
            data["keyboard_repeat"] = ""
        data["input_sleep"] = sleep_spin.get()

        logging.info(f"Collected data for step {step_id}: {data}")
        callback(step_id, data)
        modal.destroy()

    ok_button = ctk.CTkButton(main_frame, text="OK", command=on_ok)
    ok_button.pack(side="right", pady=10)

    modal.mainloop()

# ------------------------------------------------------------------------------
# If running standalone (for local testing), add a dummy callback:
if __name__ == '__main__':
    def dummy_callback(step_id, data):
        logging.info("Step %s data: %s", step_id, data)

    root = tk.Tk()
    open_input_modal(1, dummy_callback, existing_data={
        "input_from": "Keyboard",
        "keyboard_ascii": "Command + C",
        "keyboard_repeat": "2",
        "input_sleep": "1",
    })
    root.mainloop()