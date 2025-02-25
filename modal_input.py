# modal_input.py
import customtkinter as ctk
from components.utils import get_next_id
from components.label_checkbox_component import LabelCheckbox
from components.switch_component import CustomSwitch 
import tkinter as tk

def open_input_modal(step_id):
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

    # First row: Keyboard / Mouse switch
    switch = CustomSwitch(main_frame, options=["Keyboard", "Mouse"])
    switch.pack(fill="x", pady=5)
    switch.component_id = f"step_{step_id}_switch"

    # Container for variable content (Keyboard or Mouse)
    content_frame = ctk.CTkFrame(main_frame)
    content_frame.pack(fill="both", expand=True, pady=5)

    # --- Keyboard Fields ---
    keyboard_frame = ctk.CTkFrame(content_frame)
    # Second row: Key
    kb_row = ctk.CTkFrame(keyboard_frame)
    kb_row.pack(fill="x", pady=5)
    key_label = ctk.CTkLabel(kb_row, text="Key:")
    key_label.pack(side="left")
    key_label.component_id = f"step_{step_id}_key_label"

    # Clear default text when entry is focused
    def clear_default_text(event):
        default_text = "Press the key or key combination to be recorded"
        if key_entry.get() == default_text:
            key_entry.delete(0, tk.END)

    key_entry = ctk.CTkEntry(kb_row)
    key_entry.insert(0, "Press the key or key combination to be recorded")
    key_entry.pack(side="left", fill="x", expand=True, padx=5)
    key_entry.component_id = f"step_{step_id}_key_entry"

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
        print("Combination detected:", combo_str)
        return "break"  # Prevent default insertion

    # Bind key event only when entry is focused
    def bind_key_event(event):
        key_entry.bind("<KeyPress>", on_key_press)

    def unbind_key_event(event):
        key_entry.unbind("<KeyPress>")

    key_entry.bind("<FocusIn>", clear_default_text)
    key_entry.bind("<FocusIn>", bind_key_event)
    key_entry.bind("<FocusOut>", unbind_key_event)

    # Third row: Repeat
    kb_repeat = ctk.CTkFrame(keyboard_frame)
    kb_repeat.pack(fill="x", pady=5)
    repeat_label = ctk.CTkLabel(kb_repeat, text="Repeat [0-20]:")
    repeat_label.pack(side="left")
    repeat_label.component_id = f"step_{step_id}_repeat_label"
    kb_spin = tk.Spinbox(kb_repeat, from_=0, to=20)
    kb_spin.pack(side="left", padx=5)
    kb_spin.component_id = f"step_{step_id}_repeat_spinbox"

    # --- Mouse Fields ---
    mouse_frame = ctk.CTkFrame(content_frame)
    # Second row: Mouse Button
    mouse_row = ctk.CTkFrame(mouse_frame)
    mouse_row.pack(fill="x", pady=5)
    mouse_label = ctk.CTkLabel(mouse_row, text="Mouse Button:")
    mouse_label.pack(side="left")
    mouse_label.component_id = f"step_{step_id}_mouse_label"
    mouse_switch = CustomSwitch(mouse_row, options=["Left", "Middle", "Right"])
    mouse_switch.pack(side="left", fill="x", expand=True, padx=5)
    mouse_switch.component_id = f"step_{step_id}_mouse_switch"
    # Third row: Clicking
    mouse_clicking = ctk.CTkFrame(mouse_frame)
    mouse_clicking.pack(fill="x", pady=5)
    clicking_label = ctk.CTkLabel(mouse_clicking, text="Clicking:")
    clicking_label.pack(side="left")
    clicking_label.component_id = f"step_{step_id}_clicking_label"
    clicking_switch = CustomSwitch(mouse_clicking, options=["One", "Two", "Three"])
    clicking_switch.pack(side="left", fill="x", expand=True, padx=5)
    clicking_switch.component_id = f"step_{step_id}_clicking_switch"
    # Fourth row: Moving
    mouse_moving = ctk.CTkFrame(mouse_frame)
    mouse_moving.pack(fill="x", pady=5)
    moving_label = ctk.CTkLabel(mouse_moving, text="Moving [-left | +right][px]:")
    moving_label.pack(side="left")
    moving_label.component_id = f"step_{step_id}_moving_label"
    initial_value = tk.IntVar(value=0)
    moving_spin = tk.Spinbox(mouse_moving, from_=-1000, to=1000, textvariable=initial_value)
    moving_spin.pack(side="left", padx=5)
    moving_spin.component_id = f"step_{step_id}_moving_spinbox"
    # Fifth row: Keep pressed when moving
    keep_pressed = LabelCheckbox(mouse_frame, text="Keep pressed when moving?")
    keep_pressed.pack(fill="x", pady=5)
    keep_pressed.component_id = f"step_{step_id}_keep_pressed"

    # Initially show Keyboard content
    keyboard_frame.pack(fill="both", expand=True, pady=5)

    # Update content based on selection and clear fields
    def update_modal_fields(*args):
        for widget in content_frame.winfo_children():
            widget.forget()
        clear_fields()
        # Debug: print the current value of the main switch
        print("Main switch value:", switch.get_value())
        if switch.get_value() == "Keyboard":
            keyboard_frame.pack(fill="both", expand=True, pady=5)
        else:
            mouse_frame.pack(fill="both", expand=True, pady=5)

    def clear_fields():
        # Clear fields in Keyboard frame
        key_entry.delete(0, tk.END)
        key_entry.insert(0, "Press the key or key combination to be recorded")
        kb_spin.delete(0, tk.END)
        kb_spin.insert(0, "0")
        # Clear fields in Mouse frame
        if hasattr(mouse_switch, "variable"):
            mouse_switch.variable.set("")
        if hasattr(clicking_switch, "variable"):
            clicking_switch.variable.set("")
        moving_spin.delete(0, tk.END)
        moving_spin.insert(0, "0")
        
        # For LabelCheckbox, try to deselect it
        if hasattr(keep_pressed, "deselect"):
            keep_pressed.deselect()
        elif hasattr(keep_pressed, "variable"):
            keep_pressed.variable.set(False)

    # Bind the trace for switch variable once (do not rebind inside clear_fields)
    switch.var.trace("w", update_modal_fields)

    # Wait before next process [sec]
    wait_frame = ctk.CTkFrame(main_frame)
    wait_frame.pack(fill="x", pady=5)
    wait_label = ctk.CTkLabel(wait_frame, text="Wait before next process [sec]:")
    wait_label.pack(side="left")
    wait_label.component_id = f"step_{step_id}_wait_label"
    wait_spin = tk.Spinbox(wait_frame, from_=0, to=60)
    wait_spin.pack(side="left", padx=5)
    wait_spin.component_id = f"step_{step_id}_wait_spinbox"

    # OK Button
    ok_frame = ctk.CTkFrame(main_frame)
    ok_frame.pack(fill="x", pady=5)
    ok_button = ctk.CTkButton(ok_frame, text="Ok", command=modal.destroy)
    ok_button.pack(side="right")
    ok_button.component_id = f"step_{step_id}_ok_button"

    modal.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    open_input_modal(1)