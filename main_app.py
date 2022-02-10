import tkinter as tk
from app_class import App

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x800")
    app = App(root)
    root.title("Cell Analyser")
    root.tk.call('wm', 'iconphoto', root._w,
                 tk.PhotoImage(file='bacteria-icon.png'))
    root.mainloop()
