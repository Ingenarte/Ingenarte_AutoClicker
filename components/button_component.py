import customtkinter as ctk
from components.utils import get_next_id

class CustomButton(ctk.CTkButton):
    def __init__(self, parent, text="", command=None, shape="rounded", size=60, **kwargs):
        self.component_id = kwargs.pop("component_id", get_next_id())
        
        if shape == "circular":
            kwargs["corner_radius"] = size // 2
            kwargs["width"] = size
            kwargs["height"] = size
            kwargs.setdefault("anchor", "center")
        else:
            kwargs["corner_radius"] = 20

        super().__init__(parent, text=text, command=command, **kwargs)