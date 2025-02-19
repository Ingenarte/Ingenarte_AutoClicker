# modal_input.py
import customtkinter as ctk
from components.utils import get_next_id
from components.label_checkbox_component import LabelCheckbox
from components.switch_component import CustomSwitch 
import tkinter as tk

def open_input_modal(step_id):
    modal = ctk.CTkToplevel()
    title = "Input " + str(step_id)
    modal.title(title)
    modal.geometry("500x450")
    modal.grab_set()  # Bloquea la interacción con la ventana principal

    main_frame = ctk.CTkFrame(modal)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Título centrado
    title_label = ctk.CTkLabel(main_frame, text=title, font=("Arial", 18))
    title_label.pack(pady=(0, 10))
    title_label.component_id = f"step_{step_id}_title"

    # Primer renglón: Switch Teclado / Mouse
    switch = CustomSwitch(main_frame, options=["Teclado", "Mouse"])
    switch.pack(fill="x", pady=5)
    switch.component_id = f"step_{step_id}_switch"

    # Contenedor para el contenido variable (Teclado o Mouse)
    content_frame = ctk.CTkFrame(main_frame)
    content_frame.pack(fill="both", expand=True, pady=5)

    # --- Campos para Teclado ---
    keyboard_frame = ctk.CTkFrame(content_frame)
    # Segundo renglón: Key
    kb_row = ctk.CTkFrame(keyboard_frame)
    kb_row.pack(fill="x", pady=5)
    key_label = ctk.CTkLabel(kb_row, text="Key:")
    key_label.pack(side="left")
    key_label.component_id = f"step_{step_id}_key_label"
    key_entry = ctk.CTkEntry(kb_row)
    key_entry.insert(0, "Press the key or key combination to be recorded")
    key_entry.pack(side="left", fill="x", expand=True, padx=5)
    key_entry.component_id = f"step_{step_id}_key_entry"
    # Tercer renglón: Repeat
    kb_repeat = ctk.CTkFrame(keyboard_frame)
    kb_repeat.pack(fill="x", pady=5)
    repeat_label = ctk.CTkLabel(kb_repeat, text="Repeat [0-20]:")
    repeat_label.pack(side="left")
    repeat_label.component_id = f"step_{step_id}_repeat_label"
    kb_spin = tk.Spinbox(kb_repeat, from_=0, to=20)
    kb_spin.pack(side="left", padx=5)
    kb_spin.component_id = f"step_{step_id}_repeat_spinbox"

    # --- Campos para Mouse ---
    mouse_frame = ctk.CTkFrame(content_frame)
    # Segundo renglón: Mouse Stitch
    mouse_row = ctk.CTkFrame(mouse_frame)
    mouse_row.pack(fill="x", pady=5)
    mouse_label = ctk.CTkLabel(mouse_row, text="Mouse Stitch:")
    mouse_label.pack(side="left")
    mouse_label.component_id = f"step_{step_id}_mouse_label"
    mouse_switch = CustomSwitch(mouse_row, options=["Left", "Middle", "Right"])
    mouse_switch.pack(side="left", fill="x", expand=True, padx=5)
    mouse_switch.component_id = f"step_{step_id}_mouse_switch"
    # Tercer renglón: Clicking
    mouse_clicking = ctk.CTkFrame(mouse_frame)
    mouse_clicking.pack(fill="x", pady=5)
    clicking_label = ctk.CTkLabel(mouse_clicking, text="Clicking:")
    clicking_label.pack(side="left")
    clicking_label.component_id = f"step_{step_id}_clicking_label"
    clicking_switch = CustomSwitch(mouse_clicking, options=["One", "Two", "Three"])
    clicking_switch.pack(side="left", fill="x", expand=True, padx=5)
    clicking_switch.component_id = f"step_{step_id}_clicking_switch"
    # Cuarto renglón: Moving
    mouse_moving = ctk.CTkFrame(mouse_frame)
    mouse_moving.pack(fill="x", pady=5)
    moving_label = ctk.CTkLabel(mouse_moving, text="Moving [-left | +right][px]:")
    moving_label.pack(side="left")
    moving_label.component_id = f"step_{step_id}_moving_label"
    initial_value = tk.IntVar(value=0)
    moving_spin = tk.Spinbox(mouse_moving, from_=-1000, to=1000, textvariable=initial_value)
    moving_spin.pack(side="left", padx=5)
    moving_spin.component_id = f"step_{step_id}_moving_spinbox"
    # Quinto renglón: Keep pressed when moving
    keep_pressed = LabelCheckbox(mouse_frame, text="Keep pressed when moving?")
    keep_pressed.pack(fill="x", pady=5)
    keep_pressed.component_id = f"step_{step_id}_keep_pressed"

    # Inicialmente mostramos el contenido de Teclado
    keyboard_frame.pack(fill="both", expand=True, pady=5)

    # Función para actualizar el contenido en el contenedor según la selección
    def update_modal_fields(*args):
        # Primero, eliminamos todo lo que hay en content_frame
        for widget in content_frame.winfo_children():
            widget.forget()
        if switch.get_value() == "Teclado":
            keyboard_frame.pack(fill="both", expand=True, pady=5)
        else:
            mouse_frame.pack(fill="both", expand=True, pady=5)

    switch.var.trace("w", update_modal_fields)

    # --- Sexto renglón: Wait before next process [sec] (para ambos) ---
    wait_frame = ctk.CTkFrame(main_frame)
    wait_frame.pack(fill="x", pady=5)
    wait_label = ctk.CTkLabel(wait_frame, text="Wait before next process [sec]:")
    wait_label.pack(side="left")
    wait_label.component_id = f"step_{step_id}_wait_label"
    wait_spin = tk.Spinbox(wait_frame, from_=0, to=60)
    wait_spin.pack(side="left", padx=5)
    wait_spin.component_id = f"step_{step_id}_wait_spinbox"

    # --- Séptimo renglón: Botón OK ---
    ok_frame = ctk.CTkFrame(main_frame)
    ok_frame.pack(fill="x", pady=5)
    ok_button = ctk.CTkButton(ok_frame, text="Ok", command=modal.destroy)
    ok_button.pack(side="right")
    ok_button.component_id = f"step_{step_id}_ok_button"

    modal.mainloop()