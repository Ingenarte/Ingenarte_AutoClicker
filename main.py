# main.py
import customtkinter as ctk
import pyautogui
import pyperclip
from pynput import mouse
import threading
from modal_input import open_input_modal  # Importa el modal
from image_modal import open_image_modal  # Importa el modal
from data_modal import open_data_modal  # Importa el modal

# Configuración de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.update_idletasks()

# Dimensiones y posición de la ventana
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

window_width = int(screen_width * 0.30)   # 30% del ancho
window_height = int(screen_height * 0.60)   # 60% del alto
pos_x = int(screen_width * 0.60)            # 60% desde el borde izquierdo
pos_y = int(screen_height * 0.20)           # 20% desde la parte superior

root.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")
root.attributes('-alpha', 1)
root.title("Ingenarte AutoClicker")
root.resizable(True, True)

# Variables para arrastrar la ventana
start_x = 0
start_y = 0

def start_drag(e):
    global start_x, start_y
    start_x = e.x
    start_y = e.y

def move_app(e):
    x = e.x_root - start_x
    y = e.y_root - start_y
    root.geometry(f"+{x}+{y}")

# Frame principal arrastrable
draggable_frame = ctk.CTkFrame(root, fg_color="#2E2E2E", corner_radius=20)
draggable_frame.pack(fill="both", expand=True)
draggable_frame.bind('<Button-1>', start_drag)
draggable_frame.bind('<B1-Motion>', move_app)

# --- Variables globales para la captura ---
reading_mode = False         # Indica si se está esperando un clic global
current_callback = None      # Función a ejecutar al capturar el clic

def capture_global_click():
    """Escucha un clic global y, al ocurrir, ejecuta la función callback asignada."""
    def on_click(x, y, button, pressed):
        global reading_mode, current_callback
        if pressed and reading_mode and current_callback:
            current_callback(x, y)
            reading_mode = False
            return False  # Detiene el listener
    from pynput import mouse
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

# --- Funcionalidad para el botón global "Read Position" ---
def global_position_callback(x, y):
    position = f"{int(x)}x{int(y)}"
    pyperclip.copy(position)
    print(f"📍 Coordenadas copiadas al portapapeles: {position}")
    pointer_button.configure(text=position, fg_color="#333333")
    root.config(cursor="arrow")

def read_position():
    """Función para el botón global 'Read Position'."""
    global reading_mode, current_callback
    if not reading_mode:
        pointer_button.configure(text="Reading...", fg_color="#FFA500")
        root.config(cursor="cross")
        reading_mode = True
        current_callback = global_position_callback
        threading.Thread(target=capture_global_click, daemon=True).start()

# Botón global "Read Position"
pointer_button = ctk.CTkButton(
    draggable_frame, 
    text="Read Position", 
    command=read_position, 
    fg_color="#1F6AA5"
)
pointer_button.place(relx=0.3, rely=0.05, anchor="w")

# --- Funcionalidad para los botones "Position" de cada step ---
def step_position_callback(x, y, button, entry):
    position = f"{int(x)}x{int(y)}"
    print(f"📍 Coordenadas capturadas: {position}")
    def update():
        entry.delete(0, "end")
        entry.insert(0, position)
        button.configure(text="Position", fg_color="#333333")
        root.config(cursor="arrow")
        root.deiconify()  # Restaura la ventana
    root.after(0, update)

def step_read_position(button, entry):
    """Activa la captura global para un step y minimiza la ventana para dejar libre la pantalla."""
    global reading_mode, current_callback
    if not reading_mode:
        reading_mode = True
        root.iconify()  # Minimiza la ventana
        current_callback = lambda x, y: step_position_callback(x, y, button, entry)
        button.configure(text="Reading...", fg_color="#FFA500")
        root.config(cursor="cross")
        threading.Thread(target=capture_global_click, daemon=True).start()

# --- Interfaz: Creación de 10 steps ---
empty_label = ctk.CTkLabel(draggable_frame, text="")
empty_label.grid(row=0, column=0, pady=30)

for step in range(1, 11):
    step_label = ctk.CTkLabel(draggable_frame, text=f"Step {step}:", font=("Arial", 14))
    step_label.grid(row=step, column=0, padx=5, pady=5, sticky="w")
    
    # Botón Position
    position_button = ctk.CTkButton(draggable_frame, text="Position", width=100, height=30)
    position_button.grid(row=step, column=1, padx=3, pady=5, sticky="ew")
    
    # Entry para la posición
    position_textbox = ctk.CTkEntry(draggable_frame, width=90)
    position_textbox.grid(row=step, column=2, padx=3, pady=5, sticky="ew")
    
    # Asignar la funcionalidad de lectura
    position_button.configure(
        command=lambda b=position_button, t=position_textbox: step_read_position(b, t)
    )
    
    # Botón Input: Al presionarlo se abre el modal y se pasa el id del step
    input_button = ctk.CTkButton(
        draggable_frame, 
        text="Input", 
        width=80, 
        height=30, 
        command=lambda s=step: open_input_modal(s)
    )
    input_button.grid(row=step, column=3, padx=3, pady=5, sticky="ew")
    
    # main.py snippet for Image button
    image_button = ctk.CTkButton(
        draggable_frame, 
        text="Image", 
        width=80, 
        height=30,
        command=lambda s=step: open_image_modal(s))    
    image_button.grid(row=step, column=4, padx=3, pady=5, sticky="ew")
    
    data_button = ctk.CTkButton(
    draggable_frame, 
    text="Data", 
    width=80, 
    height=30,
    command=lambda s=step: open_data_modal(s))
    data_button.grid(row=step, column=5, padx=3, pady=5, sticky="ew")

# Ajustar columnas para repartir el espacio
for i in range(6):
    draggable_frame.grid_columnconfigure(i, weight=1)

# Botón Save Config (funcionalidad original)
save_button = ctk.CTkButton(
    draggable_frame,
    text="Save Config",
    command=lambda: print("⚙️ Configuración guardada")
)
save_button.place(relx=0.5, rely=0.95, anchor="center")

def initialize_imkclient():
    root.focus_force()

root.after(100, initialize_imkclient)
root.mainloop()