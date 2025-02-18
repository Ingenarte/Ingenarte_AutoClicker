import customtkinter as ctk
from components.utils import get_next_id

class CustomSwitch(ctk.CTkFrame):
    def __init__(self, parent, options, height=30, padx=5, pady=5, **kwargs):
        self.component_id = kwargs.pop("component_id", get_next_id())
        super().__init__(parent, **kwargs)

        self.options = options
        self.var = ctk.StringVar(value=options[0])
        self.buttons = []

        self.switch_background = ctk.CTkFrame(self, fg_color="#666666", corner_radius=25)
        self.switch_background.pack(fill="x", padx=padx, pady=pady)

        self.indicator = ctk.CTkFrame(self.switch_background, fg_color="#1E90FF", corner_radius=25)
        self.indicator.place(relx=0, rely=0, relheight=1, relwidth=1 / len(options))

        for index, option in enumerate(options):
            btn = ctk.CTkButton(
                self.switch_background,
                text=option,
                command=lambda opt=option, idx=index: self.select_option(opt, idx),
                corner_radius=0,
                fg_color="transparent",
                height=height
            )
            btn.pack(side="left", fill="both", expand=True)
            self.buttons.append(btn)

        self.update_button_styles()

    def select_option(self, option, index):
        self.var.set(option)
        self.indicator.place(relx=index / len(self.options), rely=0, relheight=1, relwidth=1 / len(self.options))
        self.update_button_styles()

    def update_button_styles(self):
        for btn in self.buttons:
            if btn.cget("text") == self.var.get():
                btn.configure(text_color="white")
            else:
                btn.configure(text_color="black")

    def get_value(self):
        return self.var.get()