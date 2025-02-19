# data_modal.py
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES  # Requires tkinterdnd2 package
from components.utils import get_next_id
from components.switch_component import CustomSwitch
from components.label_checkbox_component import LabelCheckbox

def open_data_modal(step_id):
    # Create modal using TkinterDnD.Tk() for DnD-enabled support
    modal = TkinterDnD.Tk()  
    modal.title("Data Modal " + str(step_id))
    modal.geometry("500x400")
    modal.grab_set()  # Block interactions with the main window

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

    # ----------------------- Row 1: Drag & Drop + OR + Open File Explorer (for .xlsx) -----------------------
    row1 = ctk.CTkFrame(main_frame, height=30)
    row1.pack(fill="x", pady=5)
    # Configure grid: 60% for DnD, 10% for "OR", 30% for button.
    row1.grid_columnconfigure(0, weight=6)
    row1.grid_columnconfigure(1, weight=1)
    row1.grid_columnconfigure(2, weight=3)

    dnd_label = ctk.CTkLabel(row1, text="Drag&Drop your .xlsx here", height=60)
    dnd_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    dnd_label.component_id = f"data_modal_dragdrop_{step_id}"

    or_label = ctk.CTkLabel(row1, text="OR", height=60)
    or_label.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
    or_label.component_id = f"data_modal_or_{step_id}"

    def open_file_explorer():
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if file_path:
            excel_path_value.configure(text=file_path)
            print("File Explorer selected:", file_path)
    file_explorer_button = ctk.CTkButton(row1, text="Open File Explorer", command=open_file_explorer, height=30)
    file_explorer_button.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
    file_explorer_button.component_id = f"data_modal_open_file_{step_id}"

    # Register DnD on the drag&drop label (if available)
    # We'll update the Excel Path value below.
    excel_path_value = None  
    if dnd_available:
        try:
            dnd_label.drop_target_register(DND_FILES)
            def drop_handler(event):
                print("Drop event data:", event.data)
                file_path = event.data.strip('{}')
                if file_path.lower().endswith('.xlsx'):
                    if excel_path_value is not None:
                        excel_path_value.configure(text=file_path)
                    else:
                        print("excel_path_value not defined yet!")
                else:
                    if excel_path_value is not None:
                        excel_path_value.configure(text="Please drop a .xlsx file.")
                    else:
                        print("excel_path_value not defined yet!")
            dnd_label.dnd_bind("<<Drop>>", drop_handler)
        except Exception as e:
            print("Error registering drop target:", e)
    else:
        print("Drag & drop is disabled because tkdnd is not available on this system.")

    # ----------------------- Row 2: Excel Path -----------------------
    row2 = ctk.CTkFrame(main_frame, height=60)
    row2.pack(fill="x", pady=5)
    excel_path_label = ctk.CTkLabel(row2, text="Excel Path:", height=50)
    excel_path_label.pack(side="left", padx=5)
    excel_path_label.component_id = f"data_modal_path_label_{step_id}"
    excel_path_value = ctk.CTkLabel(row2, text="", anchor="w", height=30)
    excel_path_value.pack(side="left", fill="x", expand=True, padx=5)
    excel_path_value.component_id = f"data_modal_path_value_{step_id}"

    # ----------------------- Row 3: Select All First Checkbox -----------------------
    row3 = ctk.CTkFrame(main_frame, height=30)
    row3.pack(fill="x", pady=5)
    select_all_label = ctk.CTkLabel(row3, text="Select All First", height=30, padx=80)
    select_all_label.pack(side="left", padx=5)
    select_all_label.component_id = f"data_modal_select_all_label_{step_id}"
    select_all_checkbox = LabelCheckbox(row3, text="", height=30)
    select_all_checkbox.pack(side="left", padx=5)
    select_all_checkbox.component_id = f"data_modal_select_all_checkbox_{step_id}"

    # ----------------------- Row 4: Cell & Switch -----------------------
    row4 = ctk.CTkFrame(main_frame, height=30)
    row4.pack(fill="x", pady=5)
    cell_label = ctk.CTkLabel(row4, text="Cell", height=30)
    cell_label.pack(side="left", padx=5)
    cell_label.component_id = f"data_modal_cell_label_{step_id}"
    cell_entry = ctk.CTkEntry(row4, width=50)  # 5 characters wide approximately
    cell_entry.pack(side="left", padx=5)
    cell_entry.component_id = f"data_modal_cell_entry_{step_id}"
    # Switch for "Copy From | Paste To"
    cell_switch = CustomSwitch(row4, options=["Copy From", "Paste To"], height=30)
    cell_switch.pack(side="left", padx=5)
    cell_switch.component_id = f"data_modal_cell_switch_{step_id}"

        # ----------------------- Row 5: Wait before next process -----------------------
    row5 = ctk.CTkFrame(main_frame, height=30)
    row5.pack(fill="x", pady=5)
    wait_next_label = ctk.CTkLabel(row5, text="Wait before next process [sec]:", height=30)
    wait_next_label.pack(side="left", padx=5)
    wait_next_label.component_id = f"data_modal_wait_next_label_{step_id}"
    wait_next_spin = tk.Spinbox(row5, from_=0, to=200, increment=1, width=8)
    wait_next_spin.delete(0, "end")
    wait_next_spin.insert(0, "0")
    wait_next_spin.pack(side="left", padx=5)
    wait_next_spin.component_id = f"data_modal_wait_next_spinbox_{step_id}"


    # ----------------------- Row 6: OK Button -----------------------
    # Place OK button at the bottom right.
    row6 = ctk.CTkFrame(main_frame, height=60)
    row6.pack(fill="x", pady=5)
    ok_button = ctk.CTkButton(row6, text="OK", command=modal.destroy, height=40)
    ok_button.pack(side="right", padx=5, pady=15)
    ok_button.component_id = f"data_modal_ok_button_{step_id}"

    modal.mainloop()

if __name__ == "__main__":
    # For independent testing, use a standard Tk root.
    root = tk.Tk()
    open_data_modal(1)