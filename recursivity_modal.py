import customtkinter as ctk
import tkinter as tk

def open_recursivity_modal(steps_data_all):
    """
    Opens a modal window for Recursivity configuration.
    
    Title: "Recursivity - All Steps"
    
    Displays a scrollable list of all steps (from steps_data_all) that have any loaded configuration.
    Each step is labeled as "Step X" (where X is the absolute step number) and is shown with a checkbox.
    
    Below the list, a label "Repetition [times] (1-200):" and a standard Tkinter Spinbox are displayed.
    
    When the user clicks OK, the modal returns a dictionary:
        {"r_steps": "<comma-separated step numbers>", "r_repeat": <repetition number>}
    
    Only steps whose configuration dictionaries contain at least one of "input", "image", "data", or "position" are shown.
    """
    modal = ctk.CTkToplevel()
    modal.grab_set()
    modal.title("Recursivity - All Steps")
    modal.geometry("300x400")
    
    header = ctk.CTkLabel(modal, text="Recursivity - All Steps", font=("Arial", 16))
    header.pack(pady=10)
    
    # Create a scrollable frame for the steps list.
    scroll_frame = ctk.CTkScrollableFrame(modal, width=280, height=200)
    scroll_frame.pack(padx=10, pady=5, fill="both", expand=False)
    
    check_vars = {}
    # Iterate over all tabs (keys) and then steps within each tab.
    for tab in sorted(steps_data_all.keys(), key=lambda t: int(t.split()[1])):
        tab_steps = steps_data_all[tab]
        for step_key in sorted(tab_steps.keys(), key=lambda x: int(x.split('_')[1])):
            # Skip the "recursivity" key if present
            if step_key.lower() == "recursivity":
                continue
            conf = tab_steps[step_key]
            if conf and ("input" in conf or "image" in conf or "data" in conf or "position" in conf):
                # Extract absolute step number from "step_X"
                step_num = int(step_key.split('_')[1])
                # Create checkbox with label "Step X"
                var = tk.BooleanVar()
                cb = ctk.CTkCheckBox(scroll_frame, text=f"Step {step_num}", variable=var)
                cb.pack(anchor="w", pady=2)
                check_vars[step_num] = var

    # Repetition frame
    repetition_frame = ctk.CTkFrame(modal)
    repetition_frame.pack(fill="x", padx=10, pady=5)
    rep_label = ctk.CTkLabel(repetition_frame, text="Repetition [times] (1-200):")
    rep_label.pack(side="left")
    rep_var = tk.IntVar(value=1)
    # Use standard Tkinter Spinbox (since CTkSpinbox is not available)
    rep_spin = tk.Spinbox(repetition_frame, from_=1, to=200, textvariable=rep_var, width=5)
    rep_spin.pack(side="left", padx=5)
    
    def on_ok():
        # Sort the selected step numbers in ascending order
        selected = sorted([str(num) for num, var in check_vars.items() if var.get()], key=lambda s: int(s))
        r_steps = ",".join(selected)
        r_repeat = rep_var.get()
        modal.recursivity_result = {"r_steps": r_steps, "r_repeat": r_repeat}
        modal.destroy()
    
    ok_btn = ctk.CTkButton(modal, text="OK", command=on_ok)
    ok_btn.pack(side="right", padx=10, pady=10)
    
    modal.wait_window()
    return modal.recursivity_result

if __name__ == "__main__":
    app = ctk.CTk()
    app.withdraw()
    # Sample aggregated steps_data_all representing configurations across all tabs.
    sample_steps_data_all = {
        "Tab 1": {
            "step_1": {"input": "Example", "position": "100x200"},
            "step_2": {},
            "step_3": {"data": "Some data"},
            "step_4": {"input": "Test"},
            "step_5": {"image": "Image data"}
        },
        "Tab 2": {
            "step_11": {"input": "Extra step"},
            "step_12": {"image": "Extra image"},
            "step_13": {"data": "More data"}
        },
        "Tab 3": {
            "step_21": {"position": "150x250", "input": "Another example"},
            "step_22": {"data": "Additional data"}
        }
    }
    result = open_recursivity_modal(sample_steps_data_all)
    print("Recursivity result:", result)
    app.destroy()