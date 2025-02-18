import customtkinter as ctk
from components.utils import get_next_id


class CustomBox(ctk.CTkEntry):
    def __init__(self, parent, box_type="text", **kwargs):
        self.box_type = box_type
        self.component_id = kwargs.pop("component_id", get_next_id())
        
        validate_command = parent.register(self._validate_input)
        kwargs["validate"] = "key"
        kwargs["validatecommand"] = (validate_command, "%P")

        super().__init__(parent, **kwargs)

    def _validate_input(self, value):
        if self.box_type == "integer":
            return value.isdigit() or value == ""
        elif self.box_type == "float":
            return value.replace('.', '', 1).isdigit() or value == ""
        return True

    def get_value(self):
        value = self.get()
        if self.box_type == "integer":
            return int(value) if value.isdigit() else 0
        elif self.box_type == "float":
            return float(value) if value.replace('.', '', 1).isdigit() else 0.0
        return value