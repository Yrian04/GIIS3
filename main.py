import tkinter as tk
from editor import CurveEditor

if __name__ == "__main__":
    root = tk.Tk()
    app = CurveEditor(root)
    root.mainloop()