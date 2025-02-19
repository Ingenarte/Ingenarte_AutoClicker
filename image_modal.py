# image_modal.py
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD,DND_FILES  # Requires tkinterdnd2 package
from components.utils import get_next_id
from components.switch_component import CustomSwitch
from components.label_checkbox_component import LabelCheckbox

def open_image_modal(step_id):
    modal = TkinterDnD.Tk()  # DnD-enabled Toplevel
    modal.title("Image Modal " + str(step_id))
    modal.geometry("600x500")
    modal.grab_set()


    # Attempt to load tkdnd (this may fail on macOS)
    try:
        modal.tk.eval('package require tkdnd')
        dnd_available = True
        print("tkdnd package loaded successfully.")
    except tk.TclError as e:
        print("tkdnd package not available:", e)
        dnd_available = False

    main_frame = ctk.CTkFrame(modal)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # --- Row 1: Title ---
    title_label = ctk.CTkLabel(main_frame, text="Image to Search (Step " + str(step_id) + ")", font=("Arial", 18))
    title_label.pack(pady=(0, 10))
    title_label.component_id = f"image_modal_title_{step_id}"

    # --- Row 2: Drag & Drop Area and Open File Explorer Button ---
    row2_frame = ctk.CTkFrame(main_frame)
    row2_frame.pack(fill="x", pady=5)
    dragdrop_label = ctk.CTkLabel(row2_frame, text="Drag&Drop your .png here", height= 60)
    dragdrop_label.pack(side="left", padx=5, pady=5, fill="x", expand=True)
    dragdrop_label.component_id = f"image_modal_dragdrop_{step_id}"
    
    # --- Define a variable for the image path widget in the closure ---
    # (It will be assigned later in Row 3.)
    image_path_value = None  

    if dnd_available:
        try:
            dragdrop_label.drop_target_register(DND_FILES)
            def drop_event_handler(event):
                print("Drop event data:", event.data)  # Debug print
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

    # --- Row 3: Image Path ---
    row3_frame = ctk.CTkFrame(main_frame)
    row3_frame.pack(fill="x", pady=5)
    image_path_label = ctk.CTkLabel(row3_frame, text="Image Path:")
    image_path_label.pack(side="left", padx=5)
    image_path_label.component_id = f"image_modal_path_label_{step_id}"
    # Now we assign the image_path_value widget so that drop_event_handler can update it.
    image_path_value = ctk.CTkLabel(row3_frame, text="", anchor="w")
    image_path_value.pack(side="left", fill="x", expand=True, padx=5)
    image_path_value.component_id = f"image_modal_path_value_{step_id}"

    # --- Row 4: Confidence ---
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

    # --- Row 5: Wait for it? and Loop Time ---
    row5_frame = ctk.CTkFrame(main_frame)
    row5_frame.pack(fill="x", pady=5)
    wait_for_it_checkbox = LabelCheckbox(row5_frame, text="Wait for it?")
    wait_for_it_checkbox.pack(side="left", padx=5)
    wait_for_it_checkbox.component_id = f"image_modal_wait_checkbox_{step_id}"
    loop_time_label = ctk.CTkLabel(row5_frame, text="Loop Time [sec]:")
    loop_time_label.pack(side="left", padx=5)
    loop_time_label.component_id = f"image_modal_loop_label_{step_id}"
    loop_time_spin = tk.Spinbox(row5_frame, from_=0, to=120, increment=1, width=8)
    loop_time_spin.delete(0, "end")
    loop_time_spin.insert(0, "0")
    loop_time_spin.pack(side="left", padx=5)
    loop_time_spin.component_id = f"image_modal_loop_spinbox_{step_id}"

    # --- Row 6: Click When Found? and Switch Left | Right ---
    row6_frame = ctk.CTkFrame(main_frame)
    row6_frame.pack(fill="x", pady=5)
    click_when_found_checkbox = LabelCheckbox(row6_frame, text="Click When Found?")
    click_when_found_checkbox.pack(side="left", padx=5)
    click_when_found_checkbox.component_id = f"image_modal_click_checkbox_{step_id}"
    click_switch = CustomSwitch(row6_frame, options=["Left", "Right"])
    click_switch.pack(side="left", padx=5)
    click_switch.component_id = f"image_modal_click_switch_{step_id}"

    # --- Row 7: TimeOut ---
    row7_frame = ctk.CTkFrame(main_frame)
    row7_frame.pack(fill="x", pady=5)
    timeout_label = ctk.CTkLabel(row7_frame, text="TimeOut [sec] (0 = infinite):")
    timeout_label.pack(side="left", padx=5)
    timeout_label.component_id = f"image_modal_timeout_label_{step_id}"
    timeout_spin = tk.Spinbox(row7_frame, from_=0, to=200, increment=1, width=8)
    timeout_spin.delete(0, "end")
    timeout_spin.insert(0, "0")
    timeout_spin.pack(side="left", padx=5)
    timeout_spin.component_id = f"image_modal_timeout_spinbox_{step_id}"

    # --- Row 8: Wait before next process ---
    row8_frame = ctk.CTkFrame(main_frame)
    row8_frame.pack(fill="x", pady=5)
    wait_next_label = ctk.CTkLabel(row8_frame, text="Wait before next process [sec]:")
    wait_next_label.pack(side="left", padx=5)
    wait_next_label.component_id = f"image_modal_wait_next_label_{step_id}"
    wait_next_spin = tk.Spinbox(row8_frame, from_=0, to=200, increment=1, width=8)
    wait_next_spin.delete(0, "end")
    wait_next_spin.insert(0, "0")
    wait_next_spin.pack(side="left", padx=5)
    wait_next_spin.component_id = f"image_modal_wait_next_spinbox_{step_id}"

    # --- Row 9: OK Button ---
    row9_frame = ctk.CTkFrame(main_frame)
    row9_frame.pack(fill="x", pady=5)
    ok_button = ctk.CTkButton(row9_frame, text="OK", command=modal.destroy, height=30)
    ok_button.pack(side="right", padx=5, pady=30)
    ok_button.component_id = f"image_modal_ok_button_{step_id}"

    modal.mainloop()

if __name__ == "__main__":
    # For independent testing, use a standard Tk root.
    root = tk.Tk()
    open_image_modal(1)