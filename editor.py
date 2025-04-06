import tkinter as tk
from tkinter import messagebox
from geometry import Point
from curves.base import Curve
from curves.hermite import HermiteCurve
from curves.bezier import BezierCurve
from curves.bspline import BSplineCurve

class CurveEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Редактор кривых")
        
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.toolbar = tk.Frame(root)
        self.toolbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.curve_type = tk.StringVar(value="bezier")
        tk.Label(self.toolbar, text="Тип кривой:").pack(anchor=tk.W, pady=5)
        
        self.curve_classes = {
            "hermite": HermiteCurve,
            "bezier": BezierCurve,
            "bspline": BSplineCurve
        }
        
        for name, cls in self.curve_classes.items():
            label_text = getattr(cls, 'DISPLAY_NAME', name.capitalize()) 
            tk.Radiobutton(self.toolbar, text=label_text, variable=self.curve_type, value=name).pack(anchor=tk.W)

        tk.Button(self.toolbar, text="Новая кривая", command=self.new_curve).pack(pady=5)
        tk.Button(self.toolbar, text="Удалить кривую", command=self.delete_curve).pack(pady=5)
        tk.Button(self.toolbar, text="Очистить всё", command=self.clear_all).pack(pady=5)
        
        self.snap_distance = 10
        self.snap_enabled = tk.BooleanVar(value=True)
        tk.Checkbutton(self.toolbar, text="Стыковка точек", variable=self.snap_enabled).pack(pady=5)
        
        self.curves = []
        self.active_curve = None
        self.selected_curve = None
        self.drag_data = {"point_idx": -1, "x": 0, "y": 0}
        
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_right_click)
        
        self.new_curve()
    
    def new_curve(self):
        curve_type_name = self.curve_type.get()
        CurveClass = self.curve_classes.get(curve_type_name)
        
        if CurveClass:
            curve = CurveClass()
            self.curves.append(curve)
            self.active_curve = curve
            self.selected_curve = None
            self.redraw()
        else:
            messagebox.showerror("Ошибка", f"Неизвестный тип кривой: {curve_type_name}")

    def delete_curve(self):
        if self.active_curve in self.curves:
            self.curves.remove(self.active_curve)
            self.active_curve = self.curves[-1] if self.curves else None
            self.selected_curve = None
            self.redraw()
        elif self.curves:
             messagebox.showinfo("Информация", "Кривая для удаления не выбрана. Кликните правой кнопкой мыши на точку кривой, чтобы сделать ее активной.")
        else:
             messagebox.showinfo("Информация", "Нет кривых для удаления.")

    def clear_all(self):
        if not self.curves:
            messagebox.showinfo("Информация", "Холст уже пуст.")
            return
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить все кривые?"):
            self.curves.clear()
            self.active_curve = None
            self.selected_curve = None
            self.redraw()
    
    def on_right_click(self, event):
        clicked_on_point = False
        for curve in reversed(self.curves):
            for point in curve.points:
                if abs(event.x - point.x) <= 5 and abs(event.y - point.y) <= 5:
                    if self.active_curve != curve:
                       self.active_curve = curve
                       self.redraw()
                    clicked_on_point = True
                    return

    def find_nearest_point(self, x, y, exclude_curve=None):
        min_dist_sq = self.snap_distance**2
        nearest_point = None
        
        for curve in self.curves:
            if curve == exclude_curve:
                continue
            for point in curve.points:
                dist_sq = (point.x - x)**2 + (point.y - y)**2
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    nearest_point = point
        
        return nearest_point 

    def on_click(self, event):
        for curve in reversed(self.curves):
            for i, point in enumerate(curve.points):
                if abs(event.x - point.x) <= 5 and abs(event.y - point.y) <= 5:
                    self.selected_curve = curve
                    self.drag_data["point_idx"] = i
                    self.drag_data["x"] = event.x
                    self.drag_data["y"] = event.y
                    if self.active_curve != curve:
                        self.active_curve = curve
                        self.redraw()
                    return
        
        if self.active_curve:
            add_x, add_y = event.x, event.y
            if self.snap_enabled.get():
                nearest_point = self.find_nearest_point(event.x, event.y, exclude_curve=self.active_curve)
                if nearest_point:
                    add_x, add_y = nearest_point.x, nearest_point.y
            
            self.active_curve.add_point(add_x, add_y)
            self.redraw()
        else:
             messagebox.showinfo("Информация", "Нет активной кривой для добавления точки. Создайте новую кривую или выберите существующую правым кликом.")

    def on_drag(self, event):
        if self.selected_curve and self.drag_data["point_idx"] != -1:
            idx = self.drag_data["point_idx"]
            move_x, move_y = event.x, event.y

            if self.snap_enabled.get():
                nearest_point = self.find_nearest_point(event.x, event.y, exclude_curve=self.selected_curve)
                if nearest_point:
                    move_x, move_y = nearest_point.x, nearest_point.y

            self.selected_curve.move_point(idx, move_x, move_y)
            
            self.drag_data["x"] = move_x
            self.drag_data["y"] = move_y
            
            self.redraw()
    
    def on_release(self, event):
        self.selected_curve = None 
        self.drag_data["point_idx"] = -1
    
    def redraw(self):
        self.canvas.delete("all")
        
        for curve in self.curves:
            is_active = curve == self.active_curve
            line_width = 3 if is_active else 1.5
            point_fill = "blue" if is_active else "black"
            point_radius = 4 if is_active else 3

            if len(curve.points) >= getattr(curve, 'MIN_POINTS', 1):
                points_coords = curve.get_points(steps=100)
                if len(points_coords) >= 2:
                    flat_coords = []
                    for p in points_coords:
                        flat_coords.extend(p)
                    
                    self.canvas.create_line(flat_coords, fill=curve.color, width=line_width, smooth=True)
            
            for point in curve.points:
                x, y = point.x, point.y
                self.canvas.create_oval(
                    x - point_radius, y - point_radius,
                    x + point_radius, y + point_radius,
                    fill=point_fill, 
                    outline=curve.color,
                    width=1
                )