import math

class Vector:

    def __init__(self, val1:float, val2:float, input_angle:bool=False):
        '''
        val1 and val2 can either be magnitude and angle or x and y components
        '''
        if input_angle:
            self._angle = val2
            self.magnitude = val1
        else:
            self._x = val1
            self.y = val2

    @property
    def magnitude(self):
        return self._magnitude
    
    @property
    def angle(self):
        return self._angle
    
    @property
    def x(self):
        return self._x
    
    @property
    def y(self):
        return self._y
    
    @magnitude.setter
    def magnitude(self, magnitude):
        self._magnitude = magnitude
        self._x = self.magnitude * math.cos(self.angle)
        self._y = self.magnitude * math.sin(self.angle)
    
    @angle.setter
    def angle(self, angle):
        self._angle = angle
        self._x = self.magnitude * math.cos(self.angle)
        self._y = self.magnitude * math.sin(self.angle)
    
    @x.setter
    def x(self, x):
        self._x = x
        self._magnitude = math.hypot(self.x, self.y)
        self._angle = math.atan2(self.y, self.x)
    
    @y.setter
    def y(self, y):
        self._y = y
        self._magnitude = math.hypot(self.x, self.y)
        self._angle = math.atan2(self.y, self.x)

    def __add__(self, other:"Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other:"Vector") -> "Vector":
        return Vector(self.x - other.x, self.y - other.y)
    
    def __mul__(self, other):
        return Vector(self.x * other, self.y * other)
    
    def __truediv__(self, other):
        return Vector(self.x / other, self.y / other)


def split_vector(magnitude:float, angle:float) -> tuple:
    '''
    returns a vector as a x and y component when inputted
    its direction and magnitude
    '''
    return (magnitude * math.cos(angle), magnitude * math.sin(angle))
    