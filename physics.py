import math

class Vector:
    '''
    2D vectors
    '''
    def __init__(self, val1:float, val2:float, input_angle:bool=False):
        '''
        if input_angle is True, val1 and val2 are magnitude and angle, respectively

        if input_angle is False, val1 and val2 are x and y components, respectively
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
    
    def __neg__(self):
        return Vector(-self.x, -self.y)

    def cross(self, other:"Vector") -> float:
        '''
        cross product of 2 vectors; dont know how to implement a cross product resulting
        in a vector bc this is supposed to be 2D vectors only
        '''
        return self.magnitude * other.magnitude * math.sin(other.angle - self.angle)

    def dot(self, other:"Vector") -> float:
        '''
        dot product of 2 vectors
        '''
        return self.x * other.x + self.y * other.y
    