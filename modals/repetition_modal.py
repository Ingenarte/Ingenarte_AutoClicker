import tkinter as tk
import customtkinter as ctk

def open_repetition_modal(root, global_config, set_repetition_time_callback):
    """
    Opens a modal window that lets the user specify a repetition interval for running the program.
    
    Parameters:
      root: The main Tkinter window.
      global_config: The configuration dict to store the repetition settings.
      set_repetition_time_callback: A function accepting the repetition interval in seconds;
                                    it should set the global repetition time and start the runner.
                                    If None is passed, then the repetition is cleared.
    """
    modal = tk.Toplevel(root)
    modal.title("Repetition")
    modal.transient(root)
    modal.grab_set()
    
    tk.Label(modal, text="Enter repetition interval:").pack(padx=10, pady=5)
    
    frame = tk.Frame(modal)
    frame.pack(padx=10, pady=5)
    
    tk.Label(frame, text="Hours:").grid(row=0, column=0, padx=5, pady=5)
    hours_entry = tk.Entry(frame, width=5)
    hours_entry.grid(row=0, column=1, padx=5, pady=5)
    
    tk.Label(frame, text="Minutes:").grid(row=0, column=2, padx=5, pady=5)
    minutes_entry = tk.Entry(frame, width=5)
    minutes_entry.grid(row=0, column=3, padx=5, pady=5)
    
    tk.Label(frame, text="Seconds:").grid(row=0, column=4, padx=5, pady=5)
    seconds_entry = tk.Entry(frame, width=5)
    seconds_entry.grid(row=0, column=5, padx=5, pady=5)
    
    # Pre-fill with default values (for example, 0h 0m 60s)
    hours_entry.insert(0, "0")
    minutes_entry.insert(0, "0")
    seconds_entry.insert(0, "60")
    
    def on_ok():
        try:
            hours = int(hours_entry.get())
            minutes = int(minutes_entry.get())
            seconds = int(seconds_entry.get())
        except Exception as e:
            print("Invalid input. Please enter integer values for hours, minutes, and seconds.")
            return
        
        total_seconds = hours * 3600 + minutes * 60 + seconds
        if total_seconds <= 0:
            print("The repetition interval must be greater than 0.")
            return
        
        # Save the repetition settings in the configuration.
        global_config["repetition"] = {"hours": hours, "minutes": minutes, "seconds": seconds}
        # Pass the total repetition interval (in seconds) to the callback.
        set_repetition_time_callback(total_seconds)
        print(f"Program repetition set to every {hours}h {minutes}m {seconds}s.")
        modal.destroy()

    def on_reset():
        # Remove the repetition settings from the configuration.
        if "repetition" in global_config:
            del global_config["repetition"]
        # Notify via the callback that the repetition is cleared.
        set_repetition_time_callback(None)
        print("Repetition cleared.")
        modal.destroy()
    
    # Create buttons with the same style as in your other modals.
    ok_btn = ctk.CTkButton(modal, text="OK", command=on_ok, fg_color="#1F6AA5", text_color="white")
    ok_btn.pack(padx=10, pady=5)
    
    reset_btn = ctk.CTkButton(modal, text="Reset", command=on_reset, fg_color="#1F6AA5", text_color="white")
    reset_btn.pack(padx=10, pady=5)
    
    # Center the modal relative to the root window.
    modal.update_idletasks()
    root_x = root.winfo_rootx()
    root_y = root.winfo_rooty()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    modal_width = modal.winfo_width()
    modal_height = modal.winfo_height()
    x = root_x + (root_width - modal_width) // 2
    y = root_y + (root_height - modal_height) // 2
    modal.geometry(f"+{x}+{y}")