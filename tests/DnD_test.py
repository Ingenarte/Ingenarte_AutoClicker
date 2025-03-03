import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES

def main():
    root = TkinterDnD.Tk()  # Create a DnD-enabled root
    root.title("DnD Test")
    label = tk.Label(root, text="Drop a file here", bg="lightgrey", width=40, height=10)
    label.pack(padx=10, pady=10)

    label.drop_target_register(DND_FILES)
    def drop_handler(event):
        print("Dropped file:", event.data)
    label.dnd_bind("<<Drop>>", drop_handler)

    root.mainloop()

if __name__ == "__main__":
    main()