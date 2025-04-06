import tkinter as tk
from tkinter import messagebox
from geometry import Point
# Импортируем все типы кривых
from curves.base import Curve # Хотя Curve напрямую не используется, он нужен для isinstance
from curves.hermite import HermiteCurve
from curves.bezier import BezierCurve
from curves.bspline import BSplineCurve

class CurveEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Редактор кривых")
        
        # Создаем холст
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Создаем панель инструментов
        self.toolbar = tk.Frame(root)
        self.toolbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Тип кривой
        self.curve_type = tk.StringVar(value="bezier") # Начинаем с Безье
        tk.Label(self.toolbar, text="Тип кривой:").pack(anchor=tk.W, pady=5)
        # Словарь для связи имени типа с классом кривой
        self.curve_classes = {
            "hermite": HermiteCurve,
            "bezier": BezierCurve,
            "bspline": BSplineCurve
        }
        # Создаем Radiobutton динамически
        for name, cls in self.curve_classes.items():
            # Используем текст заголовка из самого класса или имени ключа
            label_text = getattr(cls, 'DISPLAY_NAME', name.capitalize()) 
            tk.Radiobutton(self.toolbar, text=label_text, variable=self.curve_type, value=name).pack(anchor=tk.W)

        # Кнопки управления
        tk.Button(self.toolbar, text="Новая кривая", command=self.new_curve).pack(pady=5)
        tk.Button(self.toolbar, text="Удалить кривую", command=self.delete_curve).pack(pady=5)
        tk.Button(self.toolbar, text="Очистить всё", command=self.clear_all).pack(pady=5)
        
        # Стыковка точек
        self.snap_distance = 10  # Расстояние для стыковки точек
        self.snap_enabled = tk.BooleanVar(value=True)
        tk.Checkbutton(self.toolbar, text="Стыковка точек", variable=self.snap_enabled).pack(pady=5)
        
        # Инициализация данных
        self.curves = []  # список всех кривых
        self.active_curve = None  # активная кривая для добавления точек
        self.selected_curve = None  # выбранная кривая (для перетаскивания точек)
        self.drag_data = {"point_idx": -1, "x": 0, "y": 0}
        
        # Привязка событий
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_right_click)  # для выбора активной кривой
        
        # Создаем первую кривую
        self.new_curve()
    
    def new_curve(self):
        """Создает новую кривую выбранного типа"""
        curve_type_name = self.curve_type.get()
        CurveClass = self.curve_classes.get(curve_type_name) # Получаем класс по имени
        
        if CurveClass:
            curve = CurveClass() # Создаем экземпляр класса
            self.curves.append(curve)
            self.active_curve = curve # Новая кривая становится активной
            self.selected_curve = None # Сбрасываем выбор для перетаскивания
            self.redraw()
        else:
            messagebox.showerror("Ошибка", f"Неизвестный тип кривой: {curve_type_name}")

    def delete_curve(self):
        """Удаляет активную кривую"""
        if self.active_curve in self.curves:
            self.curves.remove(self.active_curve)
            # Если остались кривые, делаем последнюю активной, иначе None
            self.active_curve = self.curves[-1] if self.curves else None
            self.selected_curve = None # Сбрасываем выбор для перетаскивания
            self.redraw()
        elif self.curves: # Если активной не было, но кривые есть
             messagebox.showinfo("Информация", "Кривая для удаления не выбрана. Кликните правой кнопкой мыши на точку кривой, чтобы сделать ее активной.")
        else: # Если кривых нет вообще
             messagebox.showinfo("Информация", "Нет кривых для удаления.")

    
    def clear_all(self):
        """Очищает все кривые"""
        if not self.curves:
            messagebox.showinfo("Информация", "Холст уже пуст.")
            return
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить все кривые?"):
            self.curves.clear()
            self.active_curve = None
            self.selected_curve = None
            self.redraw()
    
    def on_right_click(self, event):
        """Обработка правого клика для выбора активной кривой"""
        clicked_on_point = False
        # Ищем с конца, чтобы верхние кривые выбирались первыми
        for curve in reversed(self.curves):
            for point in curve.points:
                if abs(event.x - point.x) <= 5 and abs(event.y - point.y) <= 5:
                    if self.active_curve != curve:
                       self.active_curve = curve
                       self.redraw() # Перерисовываем, чтобы показать активную кривую
                    clicked_on_point = True
                    return # Выходим, как только нашли точку
        # Если кликнули не по точке, можно сбросить активную кривую (опционально)
        # if not clicked_on_point and self.active_curve:
        #    self.active_curve = None
        #    self.redraw()


    def find_nearest_point(self, x, y, exclude_curve=None):
        """Находит ближайшую точку среди всех кривых, учитывая snap_distance"""
        min_dist_sq = self.snap_distance**2 # Сравниваем квадраты расстояний
        nearest_point = None
        
        for curve in self.curves:
            if curve == exclude_curve: # Не ищем точки на той же кривой, к которой добавляем/перетаскиваем
                continue
            for point in curve.points:
                dist_sq = (point.x - x)**2 + (point.y - y)**2
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    nearest_point = point # Запоминаем саму точку
        
        # Возвращаем найденную ближайшую точку или None
        return nearest_point 

    def on_click(self, event):
        """Обработка клика левой кнопкой мыши"""
        # 1. Проверка на перетаскивание существующей точки
        for curve in reversed(self.curves):
            for i, point in enumerate(curve.points):
                if abs(event.x - point.x) <= 5 and abs(event.y - point.y) <= 5:
                    self.selected_curve = curve # Запоминаем кривую для перетаскивания
                    self.drag_data["point_idx"] = i
                    self.drag_data["x"] = event.x # Начальные координаты для drag
                    self.drag_data["y"] = event.y
                    # Если кликнули на точку неактивной кривой, можно сделать ее активной
                    if self.active_curve != curve:
                        self.active_curve = curve
                        self.redraw()
                    return # Нашли точку, выходим
        
        # 2. Добавление новой точки к активной кривой
        if self.active_curve:
            add_x, add_y = event.x, event.y
            # Проверяем стыковку, если включена
            if self.snap_enabled.get():
                # Ищем ближайшую точку на *других* кривых
                nearest_point = self.find_nearest_point(event.x, event.y, exclude_curve=self.active_curve)
                if nearest_point:
                    add_x, add_y = nearest_point.x, nearest_point.y # Используем координаты ближайшей точки
            
            # Добавляем точку (пристыкованную или по клику)
            self.active_curve.add_point(add_x, add_y)
            self.redraw()
        else:
             messagebox.showinfo("Информация", "Нет активной кривой для добавления точки. Создайте новую кривую или выберите существующую правым кликом.")

    def on_drag(self, event):
        """Перетаскивание точки левой кнопкой мыши"""
        if self.selected_curve and self.drag_data["point_idx"] != -1:
            idx = self.drag_data["point_idx"]
            move_x, move_y = event.x, event.y # По умолчанию двигаем в позицию курсора

            # Проверяем стыковку при перетаскивании, если включена
            if self.snap_enabled.get():
                 # Ищем ближайшую точку на *других* кривых
                nearest_point = self.find_nearest_point(event.x, event.y, exclude_curve=self.selected_curve)
                if nearest_point:
                    move_x, move_y = nearest_point.x, nearest_point.y # Прилипаем к ней

            # Перемещаем точку выбранной кривой
            self.selected_curve.move_point(idx, move_x, move_y)
            
            # Обновляем позицию для следующего события перетаскивания (не обязательно)
            self.drag_data["x"] = move_x
            self.drag_data["y"] = move_y
            
            # Перерисовываем холст
            self.redraw()
    
    def on_release(self, event):
        """Окончание перетаскивания (отпускание левой кнопки)"""
        # Сбрасываем данные о перетаскивании
        self.selected_curve = None 
        self.drag_data["point_idx"] = -1
    
    def redraw(self):
        """Перерисовка всего содержимого холста"""
        self.canvas.delete("all")
        
        for curve in self.curves:
            is_active = curve == self.active_curve
            line_width = 3 if is_active else 1.5 # Делаем активную кривую толще
            point_fill = "blue" if is_active else "black" # Цвет заливки точек
            point_radius = 4 if is_active else 3 # Размер точек

            # Рисуем саму кривую, если достаточно точек
            if len(curve.points) >= getattr(curve, 'MIN_POINTS', 1):
                points_coords = curve.get_points(steps=100) # Получаем точки для отрисовки (возможно из кэша)
                if len(points_coords) >= 2:
                    flat_coords = []
                    for p in points_coords:
                        flat_coords.extend(p) # Преобразуем [Point(x1,y1), Point(x2,y2)] в [x1, y1, x2, y2, ...]
                    
                    # Используем create_line для рисования кривой
                    self.canvas.create_line(flat_coords, fill=curve.color, width=line_width, smooth=True)
            
            # Рисуем опорные точки поверх кривой
            for point in curve.points:
                x, y = point.x, point.y
                self.canvas.create_oval(
                    x - point_radius, y - point_radius,
                    x + point_radius, y + point_radius,
                    fill=point_fill, 
                    outline=curve.color, # Контур точки цветом кривой
                    width=1
                ) 