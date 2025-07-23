from math import hypot, sin, cos, atan2

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
            self.x = val1 * cos(val2)
            self.y = val1 * sin(val2)
        else:
            self.x = val1
            self.y = val2

    @property
    def magnitude(self):
        return hypot(self.x, self.y)

    @property
    def angle(self):
        return atan2(self.y, self.x)

    @magnitude.setter
    def magnitude(self, magnitude):
        angle = self.angle
        self.x = magnitude * cos(angle)
        self.y = magnitude * cos(angle)

    @angle.setter
    def angle(self, angle):
        magnitude = self.magnitude
        self.x = magnitude * cos(angle)
        self.y = magnitude * sin(angle)

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
        return self.magnitude * other.magnitude * sin(other.angle - self.angle)

    def dot(self, other:"Vector") -> float:
        '''
        dot product of 2 vectors
        '''
        return self.x * other.x + self.y * other.y
    
    def components(self):
        return [self.x, self.y]
    