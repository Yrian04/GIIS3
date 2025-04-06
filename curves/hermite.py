from .base import Curve
from geometry import Point, Matrix

class HermiteCurve(Curve):
    MIN_POINTS = 4

    def __init__(self):
        super().__init__()
        self.color = "green"
        self.M = Matrix([
            [ 2, -2,  1,  1],
            [-3,  3, -2, -1],
            [ 0,  0,  1,  0],
            [ 1,  0,  0,  0]
        ])
    
    def add_point(self, x, y):
        if len(self.points) < 4: 
            super().add_point(x, y)
    
    def compute(self, t):
        if len(self.points) != 4:
            return None
        
        p0 = self.points[0]
        p1 = self.points[1]
        t0x = self.points[2].x
        t0y = self.points[2].y
        t1x = self.points[3].x
        t1y = self.points[3].y

        G = Matrix([
            [p0.x, p0.y], 
            [p1.x, p1.y],
            [t0x, t0y],
            [t1x, t1y]
        ])
        
        T_vec = [t**3, t**2, t, 1]
        
        M_T = self.M.transpose()
        G_T = G.transpose()
        temp_vec = M_T * T_vec
        coords = G_T * temp_vec

        if coords and len(coords) == 2:
            return Point(coords[0], coords[1])
        else:
            return None 