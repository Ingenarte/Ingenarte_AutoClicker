import customtkinter as ctk
from components.utils import get_next_id
import logging
import traceback

class CustomSwitch(ctk.CTkFrame):
    def __init__(self, parent, options, height=30, padx=5, pady=5, **kwargs):
        self.component_id = kwargs.pop("component_id", get_next_id())
        super().__init__(parent, **kwargs)

        self.options = options
        self.var = ctk.StringVar(value=options[0])
        self.buttons = []
        self._is_destroyed = False
        self._animation_after_id = None

        try:
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
            logging.debug(f"CustomSwitch {self.component_id} initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing CustomSwitch {self.component_id}: {e}")
            logging.error(traceback.format_exc())

    def select_option(self, option, index):
        if self._is_destroyed:
            logging.warning(f"Attempted to select option on destroyed CustomSwitch {self.component_id}")
            return
        try:
            self.var.set(option)
            self.indicator.place(relx=index / len(self.options), rely=0, relheight=1, relwidth=1 / len(self.options))
            self.update_button_styles()
            self._start_click_animation()
            logging.debug(f"Option {option} selected on CustomSwitch {self.component_id}")
        except Exception as e:
            logging.error(f"Error selecting option on CustomSwitch {self.component_id}: {e}")
            logging.error(traceback.format_exc())

    def update_button_styles(self):
        if self._is_destroyed:
            logging.warning(f"Attempted to update styles on destroyed CustomSwitch {self.component_id}")
            return
        try:
            for btn in self.buttons:
                if btn.cget("text") == self.var.get():
                    btn.configure(text_color="white")
                else:
                    btn.configure(text_color="black")
            logging.debug(f"Button styles updated on CustomSwitch {self.component_id}")
        except Exception as e:
            logging.error(f"Error updating button styles on CustomSwitch {self.component_id}: {e}")
            logging.error(traceback.format_exc())

    def _start_click_animation(self):
        if self._animation_after_id:
            self.after_cancel(self._animation_after_id)
        self._click_animation()

    def _click_animation(self):
        if self._is_destroyed:
            return
        # Your animation code here
        if not self._is_destroyed:
            self._animation_after_id = self.after(10, self._click_animation)

    def get_value(self):
        return self.var.get()

    def destroy(self):
        logging.debug(f"Destroying CustomSwitch {self.component_id}")
        self._is_destroyed = True
        if self._animation_after_id:
            self.after_cancel(self._animation_after_id)
        for btn in self.buttons:
            btn.destroy()
        self.indicator.destroy()
        self.switch_background.destroy()
        super().destroy()