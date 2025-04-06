class Point:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
    
    def __iter__(self):
        return iter((self.x, self.y))

class Matrix:
    def __init__(self, data):
        self.data = data
        self.rows = len(data)
        self.cols = len(data[0]) if self.rows > 0 else 0
    
    def __mul__(self, other):
        """Умножение матриц или матрицы на вектор"""
        if isinstance(other, Matrix):
            if self.cols != other.rows:
                raise ValueError("Несовместимые размеры матриц")
            
            result = [[0 for _ in range(other.cols)] for _ in range(self.rows)]
            for i in range(self.rows):
                for j in range(other.cols):
                    for k in range(self.cols):
                        result[i][j] += self.data[i][k] * other.data[k][j]
            return Matrix(result)
        elif isinstance(other, (list, tuple)):
            # Умножение матрицы на вектор
            if self.cols != len(other):
                raise ValueError("Несовместимые размеры")
            
            result = [0] * self.rows
            for i in range(self.rows):
                for j in range(self.cols):
                    result[i] += self.data[i][j] * other[j]
            return result
        else:
            # Умножение на скаляр
            result = [[self.data[i][j] * other for j in range(self.cols)] 
                     for i in range(self.rows)]
            return Matrix(result)
    
    def transpose(self):
        """Транспонирование матрицы"""
        result = [[self.data[j][i] for j in range(self.rows)] 
                 for i in range(self.cols)]
        return Matrix(result) 