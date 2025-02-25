import tkinter as tk
import customtkinter as ctk

# Dummy implementation (if not already defined)
class LabelCheckbox(ctk.CTkFrame):
    def __init__(self, master, text="", **kwargs):
        super().__init__(master, **kwargs)
        self.variable = tk.BooleanVar(value=False)
        # onvalue and offvalue ensure that variable holds a Boolean.
        self.chk = ctk.CTkCheckBox(self, text=text, variable=self.variable, onvalue=True, offvalue=False)
        self.chk.pack()

root = tk.Tk()
root.geometry("300x100")

checkbox = LabelCheckbox(root, text="Select All First")
checkbox.pack(padx=20, pady=20)

def print_value():
    print("Checkbox variable value:", checkbox.variable.get())

btn = tk.Button(root, text="Print Value", command=print_value)
btn.pack()

root.mainloop()