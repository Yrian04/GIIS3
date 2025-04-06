import tkinter as tk
from editor import CurveEditor # Импортируем класс редактора

if __name__ == "__main__":
    root = tk.Tk()
    app = CurveEditor(root) # Создаем экземпляр редактора
    root.mainloop()         # Запускаем главный цикл Tkinter