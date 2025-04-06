from .base import Curve
from geometry import Point, Matrix

class HermiteCurve(Curve):
    MIN_POINTS = 4 # Минимальное количество точек для кривой Эрмита

    def __init__(self):
        super().__init__()
        self.color = "green"
        # Матрица коэффициентов Эрмита
        self.M = Matrix([
            [ 2, -2,  1,  1],
            [-3,  3, -2, -1],
            [ 0,  0,  1,  0],
            [ 1,  0,  0,  0]
        ]) # Стандартная матрица Эрмита
    
    def add_point(self, x, y):
        # Ограничиваем 4 точками (P0, P1, T0, T1)
        if len(self.points) < 4: 
            super().add_point(x, y)
    
    def compute(self, t):
        if len(self.points) != 4:
            return None
        
        p0 = self.points[0]
        p1 = self.points[1]
        # Точки 2 и 3 используются для определения векторов касательных
        # T0 = P2 - P0, T1 = P3 - P1 (или просто как векторы от начала координат)
        t0x = self.points[2].x #- p0.x # Закомментировано, если точки P2, P3 задают векторы напрямую
        t0y = self.points[2].y #- p0.y
        t1x = self.points[3].x #- p1.x
        t1y = self.points[3].y #- p1.y

        # Геометрическая матрица (P0, P1, T0, T1)
        G = Matrix([
            [p0.x, p0.y], 
            [p1.x, p1.y],
            [t0x, t0y], # Вектор T0
            [t1x, t1y]  # Вектор T1
        ])
        
        # Вектор параметра T = [t³, t², t, 1]
        T_vec = [t**3, t**2, t, 1]
        
        # P(t)^T = G^T * M^T * T^T
        M_T = self.M.transpose()
        G_T = G.transpose()
        temp_vec = M_T * T_vec
        coords = G_T * temp_vec

        if coords and len(coords) == 2:
            return Point(coords[0], coords[1])
        else:
            return None 