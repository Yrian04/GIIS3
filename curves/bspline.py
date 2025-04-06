from .base import Curve
from geometry import Point, Matrix

class BSplineCurve(Curve):
    MIN_POINTS = 4

    def __init__(self):
        super().__init__()
        self.color = "blue"
        
        self.M = Matrix([
            [-1,  3, -3,  1],
            [ 3, -6,  3,  0],
            [-3,  0,  3,  0],
            [ 1,  4,  1,  0]
        ]) * (1/6)
    
    def compute(self, t):
        n = len(self.points)
        if n < 4:
            return None

        num_segments = n - 3 
        t = max(0.0, min(1.0 - 1e-9, t)) 
        segment_t_total = t * num_segments
        i = int(segment_t_total)
        local_t = segment_t_total - i

        p0 = self.points[i]
        p1 = self.points[i+1]
        p2 = self.points[i+2]
        p3 = self.points[i+3]

        G = Matrix([
            [p0.x, p0.y],
            [p1.x, p1.y],
            [p2.x, p2.y],
            [p3.x, p3.y]
        ])

        T_vec = [local_t**3, local_t**2, local_t, 1]
        
        M_T = self.M.transpose()
        G_T = G.transpose()
        temp_vec = M_T * T_vec  
        coords = G_T * temp_vec

        if coords and len(coords) == 2:
             return Point(coords[0], coords[1])
        else:
             print(f"Ошибка вычисления B-сплайна при t={t}, local_t={local_t}, i={i}")
             return None 