# components/label_checkbox_component.py
import customtkinter as ctk
from components.utils import get_next_id

class LabelCheckbox(ctk.CTkFrame):
    def __init__(self, parent, text, **kwargs):
        self.component_id = kwargs.pop("component_id", get_next_id())
        super().__init__(parent, **kwargs)

        self.var = ctk.BooleanVar()
        self.label = ctk.CTkLabel(self, text=text)
        self.checkbox = ctk.CTkCheckBox(self, variable=self.var, text="")

        self.label.pack(side="left", padx=5)
        self.checkbox.pack(side="right", padx=5)

    def get_value(self):
        return self.var.get()