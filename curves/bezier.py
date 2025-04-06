import math
from .base import Curve
from geometry import Point

class BezierCurve(Curve):
    MIN_POINTS = 2

    def __init__(self):
        super().__init__()
        self.color = "red"
    
    def compute(self, t):
        n = len(self.points)
        if n < 2:
            return None
        
        degree = n - 1
        x = y = 0.0
        
        for i in range(n):
            try:
                bernstein_coeff = math.comb(degree, i) 
            except ValueError:
                 continue
            
            B = bernstein_coeff * (t**i) * ((1 - t)**(degree - i))
            
            x += B * self.points[i].x
            y += B * self.points[i].y
        
        return Point(x, y) 