import math
from .base import Curve
from geometry import Point

class BezierCurve(Curve):
    MIN_POINTS = 2 # Минимальное количество точек для Безье

    def __init__(self):
        super().__init__()
        self.color = "red"
    
    def compute(self, t):
        n = len(self.points)
        if n < 2: # Требуется хотя бы 2 точки (начало и конец)
            return None
        
        degree = n - 1
        x = y = 0.0
        
        # Прямая формула с использованием полиномов Бернштейна
        for i in range(n):
            try:
                # Комбинаторный коэффициент (n choose i)
                bernstein_coeff = math.comb(degree, i) 
            except ValueError: # math.comb может вызвать ошибку, если i > n
                 continue # Пропустить итерацию, если что-то пошло не так
            
            # Вычисляем базисную функцию Бернштейна
            B = bernstein_coeff * (t**i) * ((1 - t)**(degree - i))
            
            x += B * self.points[i].x
            y += B * self.points[i].y
        
        return Point(x, y) 