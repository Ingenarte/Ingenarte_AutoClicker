import tkinter as tk
import customtkinter as ctk
import datetime

def open_schedule_modal(root, global_config, set_schedule_time_callback):
    """
    Opens a modal window that lets the user specify a date and time.
    
    Parameters:
      root: The main Tkinter window.
      global_config: The configuration dict to store the schedule.
      set_schedule_time_callback: A function accepting a datetime object; it should
                                  set the global schedule time and start the runner.
                                  If None is passed, then the schedule is cleared.
    """
    # Create the modal using a standard Toplevel.
    modal = tk.Toplevel(root)
    modal.title("Schedule Run")
    modal.transient(root)
    modal.grab_set()
    
    # Use Tkinter labels/entries (or switch these to CTkLabel/CTkEntry if desired)
    tk.Label(modal, text="Enter date (YYYY-MM-DD):").pack(padx=10, pady=5)
    date_entry = tk.Entry(modal)
    date_entry.pack(padx=10, pady=5)
    date_entry.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
    
    tk.Label(modal, text="Enter time (HH:MM:SS):").pack(padx=10, pady=5)
    time_entry = tk.Entry(modal)
    time_entry.pack(padx=10, pady=5)
    # Pre-fill with current time plus one minute.
    default_time = (datetime.datetime.now() + datetime.timedelta(minutes=1)).strftime("%H:%M:%S")
    time_entry.insert(0, default_time)
    
    def on_ok():
        date_str = date_entry.get()
        time_str = time_entry.get()
        try:
            scheduled_datetime = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print("Invalid date/time format. Please use YYYY-MM-DD and HH:MM:SS.")
            return
        
        if scheduled_datetime <= datetime.datetime.now():
            print("The scheduled time must be in the future.")
            return
        
        # Save the schedule in the configuration.
        global_config["schedule"] = {"date": date_str, "time": time_str}
        # Pass the scheduled datetime back via the callback.
        set_schedule_time_callback(scheduled_datetime)
        print(f"Program scheduled for {scheduled_datetime}.")
        modal.destroy()
    
    def on_reset():
        # Clear the schedule from the configuration.
        if "schedule" in global_config:
            del global_config["schedule"]
        # Notify via callback that the schedule is cleared.
        set_schedule_time_callback(None)
        print("Schedule cleared.")
        modal.destroy()
    
    # Create CustomTkinter buttons so that the colors match the rest of your UI.
    ok_btn = ctk.CTkButton(modal, text="OK", command=on_ok, fg_color="#1F6AA5", text_color="white")
    ok_btn.pack(padx=10, pady=5)
    
    reset_btn = ctk.CTkButton(modal, text="Reset", command=on_reset, fg_color="#1F6AA5", text_color="white")
    reset_btn.pack(padx=10, pady=5)
    
    # Center the modal relative to the root window.
    modal.update_idletasks()  # Ensure the modal's size is calculated.
    root_x = root.winfo_rootx()
    root_y = root.winfo_rooty()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    modal_width = modal.winfo_width()
    modal_height = modal.winfo_height()
    x = root_x + (root_width - modal_width) // 2
    y = root_y + (root_height - modal_height) // 2
    modal.geometry(f"+{x}+{y}")