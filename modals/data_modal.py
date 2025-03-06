import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES,TkinterDnD  # Requiere tkinterdnd2 package
from components.utils import get_next_id
from components.switch_component import CustomSwitch
import traceback
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Dummy implementation for LabelCheckbox ---
class LabelCheckbox(ctk.CTkFrame):
    def __init__(self, master, text="", **kwargs):
        super().__init__(master, **kwargs)
        self.variable = tk.StringVar(value="0")
        self.chk = ctk.CTkCheckBox(self, text=text, variable=self.variable, onvalue="1", offvalue="0")
        self.chk.pack()

# Diccionario global para evitar abrir múltiples modales de datos para un mismo paso.
open_data_modals = {}

def open_data_modal(step_id, callback, existing_data=None):
    try:
        # Si ya existe un modal para este paso y sigue abierto, no se abre otro.
        if step_id in open_data_modals and open_data_modals[step_id].winfo_exists():
            logging.info(f"Data modal for step {step_id} is already open.")
            return

        # Usamos Toplevel para crear la ventana modal.
        modal = TkinterDnD.Tk()
        open_data_modals[step_id] = modal
        modal.title("Data Modal " + str(step_id))
        modal.geometry("500x400")
        modal.grab_set()

        logging.debug(f"Modal created for step {step_id}")

        # Intentar cargar tkdnd (puede fallar en macOS)
        try:
            modal.tk.eval('package require tkdnd')
            dnd_available = True
            logging.info("tkdnd package loaded successfully.")
        except tk.TclError as e:
            logging.error(f"tkdnd package not available: {e}")
            dnd_available = False

        main_frame = ctk.CTkFrame(modal)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ----------------------- Row 1: Drag & Drop and File Explorer -----------------------
        row1 = ctk.CTkFrame(main_frame, height=30)
        row1.pack(fill="x", pady=5)
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
                logging.info(f"File Explorer selected: {file_path}")
        file_explorer_button = ctk.CTkButton(row1, text="Open File Explorer", command=open_file_explorer, height=30)
        file_explorer_button.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        file_explorer_button.component_id = f"data_modal_open_file_{step_id}"

        # Si está disponible, registrar DnD.
        excel_path_value = None
        if dnd_available:
            try:
                dnd_label.drop_target_register(DND_FILES)
                def drop_handler(event):
                    logging.info(f"Drop event data: {event.data}")
                    file_path = event.data.strip('{}')
                    if file_path.lower().endswith('.xlsx'):
                        if excel_path_value is not None:
                            excel_path_value.configure(text=file_path)
                        else:
                            logging.warning("excel_path_value not defined yet!")
                    else:
                        if excel_path_value is not None:
                            excel_path_value.configure(text="Please drop a .xlsx file.")
                        else:
                            logging.warning("excel_path_value not defined yet!")
                dnd_label.dnd_bind("<<Drop>>", drop_handler)
            except Exception as e:
                logging.error(f"Error registering drop target: {e}")
                logging.error(traceback.format_exc())
        else:
            logging.warning("Drag & drop is disabled because tkdnd is not available on this system.")

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

        # ----------------------- Row 4: Cell and Switch -----------------------
        row4 = ctk.CTkFrame(main_frame, height=30)
        row4.pack(fill="x", pady=5)
        cell_label = ctk.CTkLabel(row4, text="Cell", height=30)
        cell_label.pack(side="left", padx=5)
        cell_label.component_id = f"data_modal_cell_label_{step_id}"
        cell_entry = ctk.CTkEntry(row4, width=50)
        cell_entry.pack(side="left", padx=5)
        cell_entry.component_id = f"data_modal_cell_entry_{step_id}"
        
        def to_uppercase(event):
            current_text = cell_entry.get()
            cell_entry.delete(0, tk.END)
            cell_entry.insert(0, current_text.upper())
        cell_entry.bind("<KeyRelease>", to_uppercase)
        
        logging.debug(f"Creating CustomSwitch for step {step_id}")
        cell_switch = CustomSwitch(row4, options=["Copy From", "Paste To"], height=30)
        cell_switch.pack(side="left", padx=5)
        cell_switch.component_id = f"data_modal_cell_switch_{step_id}"
        logging.debug(f"CustomSwitch created with ID: {cell_switch.component_id}")

        # ----------------------- Row 5: OK Button (aligned right) -----------------------
        row5 = ctk.CTkFrame(main_frame, height=30)
        row5.pack(fill="x", pady=5)
        def on_ok():
            try:
                # Gather the data from the modal fields.
                data = {}
                data["data_path"] = excel_path_value.cget("text")
                data["data_cell"] = cell_entry.get().upper()
                try:
                    data["data_select_all"] = bool(int(select_all_checkbox.chk.get()))
                except Exception:
                    logging.error("Error getting checkbox state, defaulting to False")
                    data["data_select_all"] = False
                data["data_copy_paste"] = cell_switch.get_value()
                logging.info(f"Collected data for step {step_id}: {data}")
                # Call the callback function with the collected data.
                callback(step_id, data)
            except Exception as e:
                logging.error(f"Error in on_ok function: {e}")
                logging.error(traceback.format_exc())
            finally:
                try:
                    # Withdraw (hide) the modal to cancel any pending callbacks.
                    modal.withdraw()
                    logging.debug("Modal withdrawn")
                    # Destroy the modal.
                    modal.destroy()
                    logging.debug("Modal destroyed")
                    # **IMPORTANT:** Remove the modal from the global dictionary to avoid
                    # future calls to winfo_exists() on a destroyed widget.
                    if step_id in open_data_modals:
                        del open_data_modals[step_id]
                        logging.debug(f"Modal for step {step_id} removed from open_data_modals.")
                except Exception as e:
                    logging.error(f"Error destroying modal: {e}")
                    logging.error(traceback.format_exc())

        ok_button = ctk.CTkButton(row5, text="OK", command=on_ok, height=40)
        ok_button.pack(side="right", padx=5, pady=15)
        ok_button.component_id = f"data_modal_ok_button_{step_id}"

        # ----------------------- Prefill existing data if provided -----------------------
        if existing_data:
            try:
                excel_path_value.configure(text=existing_data.get("data_path", ""))
                cell_entry.delete(0, tk.END)
                cell_entry.insert(0, existing_data.get("data_cell", ""))
                select_all_checkbox.variable.set(existing_data.get("data_select_all", False))
                if existing_data.get("data_copy_paste", None):
                    cell_switch.var.set(existing_data.get("data_copy_paste"))
                    if hasattr(cell_switch, "update_button_styles"):
                        cell_switch.update_button_styles()
                    elif hasattr(cell_switch, "update_buttons"):
                        cell_switch.update_buttons()
            except Exception as e:
                logging.error(f"Error prefilling existing data: {e}")
                logging.error(traceback.format_exc())

        def on_closing():
            logging.debug("Window closing event triggered")
            on_ok()

        modal.protocol("WM_DELETE_WINDOW", on_closing)

        modal.mainloop()

    except Exception as e:
        logging.error(f"Unhandled exception in open_data_modal: {e}")
        logging.error(traceback.format_exc())

if __name__ == "__main__":
    def dummy_data_callback(step_id, data):
         logging.info(f"Step {step_id} data: {data}")
    open_data_modal(1, dummy_data_callback)