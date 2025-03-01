import customtkinter as ctk
import tkinter as tk

def open_recursivity_modal(steps_data_all, prev_rec=None):
    """
    Opens a modal window for Recursivity configuration.

    Title: "Recursivity - All Steps"

    Displays a scrollable list of all steps (from steps_data_all) that have any loaded configuration.
    Each step is labeled as "Step X" (where X is the absolute step number) and is shown with a checkbox.

    Below the list, a label "Repetition [times] (1-200):" and a standard Tkinter Spinbox are displayed.

    When the user clicks OK, the modal returns a dictionary:
        {"r_steps": "<comma-separated step numbers>", "r_repeat": <repetition number>}

    Only steps whose configuration dictionaries contain at least one of "input", "image", "data", or "position" are shown.

    If a previous recursivity configuration was provided via prev_rec, then the checkboxes and
    spinbox will be preselected accordingly.
    """
    if prev_rec is None:
        prev_rec = {}
    modal = ctk.CTkToplevel()
    modal.grab_set()
    modal.title("Recursivity - All Steps")
    modal.geometry("300x400")
    
    header = ctk.CTkLabel(modal, text="Recursivity - All Steps", font=("Arial", 16))
    header.pack(pady=10)
    
    # Parse previous rec configuration
    prev_steps = set()
    prev_repeat = 1
    if prev_rec:
        if "r_steps" in prev_rec:
            prev_steps = set(prev_rec["r_steps"].split(","))
        if "r_repeat" in prev_rec:
            prev_repeat = prev_rec["r_repeat"]
    
    # Create a scrollable frame for the steps list.
    scroll_frame = ctk.CTkScrollableFrame(modal, width=280, height=200)
    scroll_frame.pack(padx=10, pady=5, fill="both", expand=False)
    
    check_vars = {}
    # Iterate over all tabs and steps.
    for tab in sorted(steps_data_all.keys(), key=lambda t: int(t.split()[1])):
        tab_steps = steps_data_all[tab]
        for step_key in sorted(tab_steps.keys(), key=lambda x: int(x.split('_')[1])):
            # Skip the "recursivity" key if present.
            if step_key.lower() == "recursivity":
                continue
            conf = tab_steps[step_key]
            # Only show the step if there is any data.
            if conf and ("input" in conf or "image" in conf or "data" in conf or "position" in conf):
                # Extract the absolute step number from "step_X"
                step_num = step_key.split('_')[1]
                var = tk.BooleanVar(value=(step_num in prev_steps))
                cb = ctk.CTkCheckBox(scroll_frame, text=f"Step {step_num}", variable=var)
                cb.pack(anchor="w", pady=2)
                check_vars[step_num] = var

    # Repetition frame
    repetition_frame = ctk.CTkFrame(modal)
    repetition_frame.pack(fill="x", padx=10, pady=5)
    rep_label = ctk.CTkLabel(repetition_frame, text="Repetition [times] (1-200):")
    rep_label.pack(side="left")
    rep_var = tk.IntVar(value=prev_repeat)
    rep_spin = tk.Spinbox(repetition_frame, from_=1, to=200, textvariable=rep_var, width=5)
    rep_spin.pack(side="left", padx=5)
    
    # OK button
    def on_ok():
        # Get all selected step numbers (sorted in ascending order)
        selected = sorted([str(num) for num, var in check_vars.items() if var.get()], key=lambda s: int(s))
        r_steps = ",".join(selected)
        r_repeat = rep_var.get()
        modal.recursivity_result = {"r_steps": r_steps, "r_repeat": r_repeat}
        modal.destroy()
    
    ok_btn = ctk.CTkButton(modal, text="OK", command=on_ok)
    ok_btn.pack(side="right", padx=10, pady=10)
    
    modal.wait_window()
    return modal.recursivity_result