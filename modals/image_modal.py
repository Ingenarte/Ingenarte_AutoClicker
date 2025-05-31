import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES,TkinterDnD  # Requires tkinterdnd2 package
from components.utils import get_next_id
from components.switch_component import CustomSwitch
import sys

# Dummy implementation for LabelCheckbox.
# Replace this with your own if available.
class LabelCheckbox(ctk.CTkFrame):
    def __init__(self, master, text="", **kwargs):
        super().__init__(master, **kwargs)
        # We'll use a StringVar that holds "1" when selected and "0" when not.
        self.variable = tk.StringVar(value="0")
        self.chk = ctk.CTkCheckBox(self, text=text, variable=self.variable)
        self.chk.pack()

# Global dictionary to track open image modals by step ID.
open_image_modals = {}

def open_image_modal(step_id, callback, existing_data=None):
    # Prevent opening more than one modal for the same step.
    if step_id in open_image_modals and open_image_modals[step_id].winfo_exists():
        print(f"Image modal for step {step_id} is already open.")
        return

    # Create a new Toplevel window.
    modal = TkinterDnD.Tk()
    open_image_modals[step_id] = modal
    modal.title("Image Modal " + str(step_id))
    
    if sys.platform == "win32":
    # En Windows, le sumamos 130 píxeles extra de alto
        modal.geometry("600x630")
    else:
        modal.geometry("600x500")



    try:
        modal.grab_set()
    except tk.TclError as e:
        print("Grab failed:", e)

    # When the user closes the window via the X button, ensure cleanup.
    def on_close():
        modal.destroy()
        if step_id in open_image_modals:
            del open_image_modals[step_id]
    modal.protocol("WM_DELETE_WINDOW", on_close)

    # Attempt to load tkdnd package.
    try:
        modal.tk.eval('package require tkdnd')
        dnd_available = True
        print("tkdnd package loaded successfully.")
    except tk.TclError as e:
        print("tkdnd package not available:", e)
        dnd_available = False

    main_frame = ctk.CTkFrame(modal)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Row 1: Title
    title_label = ctk.CTkLabel(main_frame, text=f"Image to Search (Step {step_id})", font=("Arial", 18))
    title_label.pack(pady=(0, 10))
    title_label.component_id = f"image_modal_title_{step_id}"

    # Row 2: Drag & Drop Area and File Explorer Button
    row2_frame = ctk.CTkFrame(main_frame)
    row2_frame.pack(fill="x", pady=5)
    dragdrop_label = ctk.CTkLabel(row2_frame, text="Drag & Drop your .png here", height=60)
    dragdrop_label.pack(side="left", padx=5, pady=5, fill="x", expand=True)
    dragdrop_label.component_id = f"image_modal_dragdrop_{step_id}"
    image_path_value = None  # Will be assigned below.

    if dnd_available:
        try:
            dragdrop_label.drop_target_register(DND_FILES)
            def drop_event_handler(event):
                print("Drop event data:", event.data)
                file_path = event.data.strip('{}')
                if file_path.lower().endswith('.png'):
                    if image_path_value is not None:
                        image_path_value.configure(text=file_path)
                    else:
                        print("image_path_value not defined yet!")
                else:
                    if image_path_value is not None:
                        image_path_value.configure(text="Please drop a .png file.")
                    else:
                        print("image_path_value not defined yet!")
            dragdrop_label.dnd_bind("<<Drop>>", drop_event_handler)
        except Exception as e:
            print("Error registering drop target:", e)
    else:
        print("Drag & drop is disabled because tkdnd is not available on this system.")

    def open_file_explorer():
        file_path = filedialog.askopenfilename(filetypes=[("PNG Files", "*.png")])
        if file_path:
            if image_path_value is not None:
                image_path_value.configure(text=file_path)
            else:
                print("image_path_value not defined yet!")
    open_file_button = ctk.CTkButton(row2_frame, text="Open File Explorer", command=open_file_explorer, height=60)
    open_file_button.pack(side="left", padx=5, pady=5)
    open_file_button.component_id = f"image_modal_open_file_{step_id}"

    # Row 3: Image Path
    row3_frame = ctk.CTkFrame(main_frame)
    row3_frame.pack(fill="x", pady=5)
    image_path_label = ctk.CTkLabel(row3_frame, text="Image Path:")
    image_path_label.pack(side="left", padx=5)
    image_path_label.component_id = f"image_modal_path_label_{step_id}"
    image_path_value = ctk.CTkLabel(row3_frame, text="", anchor="w")
    image_path_value.pack(side="left", fill="x", expand=True, padx=5)
    image_path_value.component_id = f"image_modal_path_value_{step_id}"

    # Row 4: Confidence
    row4_frame = ctk.CTkFrame(main_frame)
    row4_frame.pack(fill="x", pady=5)
    confidence_label = ctk.CTkLabel(row4_frame, text="Confidence: [0.00 - 1.00]")
    confidence_label.pack(side="left", padx=5)
    confidence_label.component_id = f"image_modal_confidence_label_{step_id}"
    confidence_spin = tk.Spinbox(row4_frame, from_=0, to=1, increment=0.05, format="%.2f", width=8)
    confidence_spin.delete(0, "end")
    confidence_spin.insert(0, "1.00")
    confidence_spin.pack(side="left", padx=5)
    confidence_spin.component_id = f"image_modal_confidence_spinbox_{step_id}"

    # Row 5: Image Wait and Image Wait Sleep
    row5_frame = ctk.CTkFrame(main_frame)
    row5_frame.pack(fill="x", pady=5)
    image_wait_checkbox = LabelCheckbox(row5_frame, text="Image Wait")
    image_wait_checkbox.pack(side="left", padx=5)
    image_wait_checkbox.component_id = f"image_modal_wait_checkbox_{step_id}"
    image_wait_sleep_label = ctk.CTkLabel(row5_frame, text="Image Wait Sleep [sec]:")
    image_wait_sleep_label.pack(side="left", padx=5)
    image_wait_sleep_label.component_id = f"image_modal_wait_sleep_label_{step_id}"
    image_wait_sleep_spin = tk.Spinbox(row5_frame, from_=0, to=120, increment=1, width=8)
    image_wait_sleep_spin.delete(0, "end")
    image_wait_sleep_spin.insert(0, "0")
    image_wait_sleep_spin.pack(side="left", padx=5)
    image_wait_sleep_spin.component_id = f"image_modal_wait_sleep_spinbox_{step_id}"

    # Row 6: Image Click and Image Click LR
    row6_frame = ctk.CTkFrame(main_frame)
    row6_frame.pack(fill="x", pady=5)
    image_click_checkbox = LabelCheckbox(row6_frame, text="Image Click")
    image_click_checkbox.pack(side="left", padx=5)
    image_click_checkbox.component_id = f"image_modal_click_checkbox_{step_id}"
    click_switch = CustomSwitch(row6_frame, options=["Left", "Right"])
    click_switch.pack(side="left", padx=5)
    click_switch.component_id = f"image_modal_click_switch_{step_id}"
    if existing_data:
        click_switch.var.set(existing_data.get("image_click_LR", "Left"))
        if hasattr(click_switch, "update_button_styles"):
            click_switch.update_button_styles()
        elif hasattr(click_switch, "update_buttons"):
            click_switch.update_buttons()

    # Row 7: Image Timeout
    row7_frame = ctk.CTkFrame(main_frame)
    row7_frame.pack(fill="x", pady=5)
    timeout_label = ctk.CTkLabel(row7_frame, text="Image Timeout [sec] (0 = infinite):")
    timeout_label.pack(side="left", padx=5)
    timeout_label.component_id = f"image_modal_timeout_label_{step_id}"
    timeout_spin = tk.Spinbox(row7_frame, from_=0, to=200, increment=1, width=8)
    timeout_spin.delete(0, "end")
    timeout_spin.insert(0, "0")
    timeout_spin.pack(side="left", padx=5)
    timeout_spin.component_id = f"image_modal_timeout_spinbox_{step_id}"

    # Row 8: Image Sleep
    row8_frame = ctk.CTkFrame(main_frame)
    row8_frame.pack(fill="x", pady=5)
    sleep_next_label = ctk.CTkLabel(row8_frame, text="Image Sleep [sec]:")
    sleep_next_label.pack(side="left", padx=5)
    sleep_next_label.component_id = f"image_modal_sleep_label_{step_id}"
    sleep_next_spin = tk.Spinbox(row8_frame, from_=0, to=200, increment=1, width=8)
    sleep_next_spin.delete(0, "end")
    sleep_next_spin.insert(0, "0")
    sleep_next_spin.pack(side="left", padx=5)
    sleep_next_spin.component_id = f"image_modal_sleep_spinbox_{step_id}"

    # --- Prefill existing data if provided ---
    if existing_data:
        image_path_value.configure(text=existing_data.get("image_path", ""))
        confidence_spin.delete(0, "end")
        confidence_spin.insert(0, existing_data.get("image_confidence", "1.00"))
        # For checkboxes, use the underlying widget.
        try:
            if existing_data.get("image_wait", False):
                image_wait_checkbox.chk.select()
            else:
                image_wait_checkbox.chk.deselect()
        except Exception as e:
            print("Error preloading image_wait:", e)
        image_wait_sleep_spin.delete(0, "end")
        image_wait_sleep_spin.insert(0, existing_data.get("image_wait_sleep", "0"))
        try:
            if existing_data.get("image_click", False):
                image_click_checkbox.chk.select()
            else:
                image_click_checkbox.chk.deselect()
        except Exception as e:
            print("Error preloading image_click:", e)
        timeout_spin.delete(0, "end")
        timeout_spin.insert(0, existing_data.get("image_timeout", "0"))
        sleep_next_spin.delete(0, "end")
        sleep_next_spin.insert(0, existing_data.get("image_sleep", "0"))

    # Row 9: OK Button – collect and return the image configuration.
    row9_frame = ctk.CTkFrame(main_frame)
    row9_frame.pack(fill="x", pady=5)
    def on_ok():
        # Debug: print raw checkbox values.
        print("Raw image_wait value:", image_wait_checkbox.chk.get())
        print("Raw image_click value:", image_click_checkbox.chk.get())
        data = {}
        data["image_path"] = image_path_value.cget("text")
        data["image_confidence"] = confidence_spin.get()
        try:
            data["image_wait"] = bool(int(image_wait_checkbox.chk.get()))
        except Exception:
            data["image_wait"] = False
        data["image_wait_sleep"] = image_wait_sleep_spin.get()
        try:
            data["image_click"] = bool(int(image_click_checkbox.chk.get()))
        except Exception:
            data["image_click"] = False
        data["image_click_LR"] = click_switch.get_value()
        data["image_timeout"] = timeout_spin.get()
        data["image_sleep"] = sleep_next_spin.get()
        print("Collected image data for step", step_id, ":", data)
        callback(step_id, data)
        modal.destroy()
        if step_id in open_image_modals:
            del open_image_modals[step_id]
    ok_button = ctk.CTkButton(row9_frame, text="OK", command=on_ok, height=30)
    ok_button.pack(side="right", padx=5, pady=30)
    ok_button.component_id = f"image_modal_ok_button_{step_id}"

    modal.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    def dummy_image_callback(step_id, data):
         print("Step", step_id, "image data:", data)
    open_image_modal(1, dummy_image_callback)