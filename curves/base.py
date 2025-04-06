from geometry import Point

class Curve:
    def __init__(self):
        self.points = []
        self.color = "black"
        self._points_cache = []
    
    def add_point(self, x, y):
        self.points.append(Point(x, y))
        self._points_cache = []
    
    def move_point(self, index, x, y):
        if 0 <= index < len(self.points):
            self.points[index].x = float(x)
            self.points[index].y = float(y)
            self._points_cache = []
    
    def compute(self, t):
        raise NotImplementedError
    
    def get_points(self, steps=100):
        if not self._points_cache:
            self._points_cache = []
            min_points = getattr(self, 'MIN_POINTS', 1)
            if len(self.points) >= min_points:
                for i in range(steps + 1):
                    t = i / steps
                    point = self.compute(t)
                    if point:
                        self._points_cache.append(point)
            
        return self._points_cache 