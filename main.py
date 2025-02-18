import customtkinter as ctk
import pyautogui
import pyperclip
from pynput import mouse
import threading
import time

# Inicializar la ventana
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.update_idletasks()

# Obtener dimensiones de pantalla dinámicamente
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calcular tamaño y posición según requisitos
window_width = int(screen_width * 0.30)  # 30% del ancho
window_height = int(screen_height * 0.60)  # 60% del alto
pos_x = int(screen_width * 0.60)  # 60% desde el borde izquierdo
pos_y = int(screen_height * 0.20)  # 20% desde la parte superior

# Establecer tamaño y posición
root.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")
root.attributes('-alpha', 1)  # Transparencia completa
root.title("Ingenarte AutoClicker")

# Permitir que el usuario pueda cambiar el tamaño
root.resizable(True, True)

# Variables para el arrastre
start_x = 0
start_y = 0

# Iniciar arrastre
def start_drag(e):
    global start_x, start_y
    start_x = e.x
    start_y = e.y

# Mover ventana
def move_app(e):
    x = e.x_root - start_x
    y = e.y_root - start_y
    root.geometry(f"+{x}+{y}")

# Frame principal (arrastrable)
draggable_frame = ctk.CTkFrame(root, fg_color="#2E2E2E", corner_radius=20)
draggable_frame.pack(fill="both", expand=True)
draggable_frame.bind('<Button-1>', start_drag)
draggable_frame.bind('<B1-Motion>', move_app)

# Estado global para controlar el modo de lectura
reading_mode = False

# Función para iniciar la lectura de posición
def read_position():
    global reading_mode
    if not reading_mode:
        # Primer clic: cambia a "Reading..."
        pointer_button.configure(text="Reading...", fg_color="#FFA500")
        root.config(cursor="cross")
        reading_mode = True
        # Iniciar el listener global para capturar clics fuera de la aplicación
        threading.Thread(target=capture_global_click, daemon=True).start()

def capture_global_click():
    def on_click(x, y, button, pressed):
        global reading_mode
        if pressed and reading_mode:
            # Capturar coordenadas del clic
            position = f"{int(x)}x{int(y)}"
            pyperclip.copy(position)
            print(f"📍 Coordenadas copiadas al portapapeles: {position}")

            # Cambiar color del botón a gris oscuro y mostrar coordenadas
            pointer_button.configure(text=position, fg_color="#333333")
            root.config(cursor="arrow")

            reading_mode = False
            return False

    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

# Evento para detectar Ctrl+V y Cmd+V
def on_paste(event=None):
    print("📋 Se detectó un 'paste'")
    pointer_button.configure(text="Read Position", fg_color="#1F6AA5")

# Botón para iniciar lectura de posición
pointer_button = ctk.CTkButton(draggable_frame, text="Read Position", command=read_position, fg_color="#1F6AA5")
pointer_button.place(relx=0.3, rely=0.05, anchor="w")

# Agregar un espaciador para bajar los steps
empty_label = ctk.CTkLabel(draggable_frame, text="")
empty_label.grid(row=0, column=0, pady=30)

# Crear 10 steps con IDs únicos
for step in range(1, 11):
    step_label = ctk.CTkLabel(draggable_frame, text=f"Step {step}:", font=("Arial", 14))
    step_label.grid(row=step, column=0, padx=5, pady=5, sticky="w")

    position_button = ctk.CTkButton(draggable_frame, text="Position", width=100, height=30)
    position_button.grid(row=step, column=1, padx=3, pady=5, sticky="ew")

    position_textbox = ctk.CTkEntry(draggable_frame, width=80)
    position_textbox.grid(row=step, column=2, padx=3, pady=5, sticky="ew")

    input_button = ctk.CTkButton(draggable_frame, text="Input", width=80, height=30)
    input_button.grid(row=step, column=3, padx=3, pady=5, sticky="ew")

    image_button = ctk.CTkButton(draggable_frame, text="Image", width=80, height=30)
    image_button.grid(row=step, column=4, padx=3, pady=5, sticky="ew")

    data_button = ctk.CTkButton(draggable_frame, text="Data", width=80, height=30)
    data_button.grid(row=step, column=5, padx=3, pady=5, sticky="ew")

# Ajustar las columnas para repartir el espacio disponible
for i in range(6):
    draggable_frame.grid_columnconfigure(i, weight=1)

# Botón para guardar configuración
save_button = ctk.CTkButton(draggable_frame, text="Save Config", command=lambda: print("⚙️ Configuración guardada"))
save_button.place(relx=0.5, rely=0.95, anchor="center")

# Forzar el foco para inicializar el IMKClient sin interacción
def initialize_imkclient():
    root.focus_force()

root.after(100, initialize_imkclient)

# Detectar Ctrl+V y Cmd+V para restaurar el botón
root.bind("<Control-v>", on_paste)
root.bind("<Command-v>", on_paste)

# Iniciar la aplicación
root.mainloop()