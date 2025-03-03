import customtkinter as ctk
import os
from components.button_component import CustomButton
from components.box_component import CustomBox
from components.label_checkbox_component import LabelCheckbox
from components.switch_component import CustomSwitch

# Suprimir warnings innecesarios
os.environ['PYTHONWARNINGS'] = 'ignore'

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

# Prueba de todos los componentes
frame_width = int(window_width * 0.20)  # 20% del ancho total

button_rounded = CustomButton(draggable_frame, text="Rounded Button", shape="rounded", width=frame_width)
button_rounded.pack(pady=10, anchor="w")

button_circular = CustomButton(draggable_frame, text="Circular", shape="circular", size=80)
button_circular.pack(pady=10)

box_text = CustomBox(draggable_frame, box_type="text")
box_text.pack(pady=10, fill="x")

box_int = CustomBox(draggable_frame, box_type="integer")
box_int.pack(pady=10, fill="x")

box_float = CustomBox(draggable_frame, box_type="float")
box_float.pack(pady=10, fill="x")

label_checkbox = LabelCheckbox(draggable_frame, text="Check me")
label_checkbox.pack(pady=10)

# Switch de 3 opciones
switch1 = CustomSwitch(draggable_frame, options=["Option 1", "Option 2", "Option 3"], padx=10, pady=5)
switch1.pack(pady=10, fill="x")

switch1 = CustomSwitch(draggable_frame, options=["Option 1", "Option 2"], height=30, width=100)
switch1.pack(pady=10)


# Forzar el foco para inicializar el IMKClient sin interacción
def initialize_imkclient():
    root.focus_force()

# Llamar a la función después de un pequeño retraso para que macOS cargue el IMKClient
root.after(100, initialize_imkclient)

# Iniciar la aplicación
root.mainloop()