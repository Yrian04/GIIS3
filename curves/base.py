from geometry import Point

class Curve:
    def __init__(self):
        self.points = []
        self.color = "black"
        self._points_cache = []
    
    def add_point(self, x, y):
        self.points.append(Point(x, y))
        self._points_cache = [] # Сброс кэша при добавлении точки
    
    def move_point(self, index, x, y):
        if 0 <= index < len(self.points):
            self.points[index].x = float(x)
            self.points[index].y = float(y)
            self._points_cache = [] # Сброс кэша при перемещении точки
    
    def compute(self, t):
        """Вычисляет точку на кривой для параметра t. Должен быть переопределен."""
        raise NotImplementedError
    
    def get_points(self, steps=100):
        """Возвращает список точек для отрисовки кривой, используя кэш."""
        # Перегенерация кэша, если он пуст
        if not self._points_cache:
            self._points_cache = []
            # Добавляем проверку на минимальное количество точек для вычисления
            min_points = getattr(self, 'MIN_POINTS', 1) # Получаем MIN_POINTS или используем 1 по умолчанию
            if len(self.points) >= min_points:
                for i in range(steps + 1):
                    t = i / steps
                    point = self.compute(t)
                    if point:
                        self._points_cache.append(point)
            # Если точек недостаточно, кэш останется пустым, get_points вернет []
            
        return self._points_cache 