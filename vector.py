from math import hypot, sin, cos, atan2, pi
import pygame as pg

from settings import SETTINGS

VECT_PX_PER_UNIT = SETTINGS["vector_visuals"]["VECT_PX_PER_UNIT"]
VECT_HEAD_LEN = SETTINGS["vector_visuals"]["VECT_HEAD_LEN"]
VECT_THKNS = SETTINGS["vector_visuals"]["VECT_THKNS"]

class Vector:
    '''
    2D vectors yayayaya
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
        self.y = magnitude * sin(angle)

    @angle.setter
    def angle(self, angle):
        magnitude = self.magnitude
        self.x = magnitude * cos(angle)
        self.y = magnitude * sin(angle)

    def __add__(self, other:"Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other:"Vector") -> "Vector":
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other:float):
        return Vector(self.x * other, self.y * other)

    def __truediv__(self, other:float):
        return Vector(self.x / other, self.y / other)
    
    def __neg__(self):
        return Vector(-self.x, -self.y)
    
    def __str__(self):
        return f"Mag: {self.magnitude}\tAng: {self.angle}\tX: {self.x}\tY: {self.y}"

    def cross(self, other:"Vector") -> float:
        '''
        cross product of 2 vectors; dont know how to implement a cross product resulting
        in a vector bc this is supposed to be 2D vectors only
        '''
        return self.magnitude * other.magnitude * sin(other.angle - self.angle)

    def dot(self, other:"Vector") -> float:
        '''dot product of 2 vectors'''
        return self.x * other.x + self.y * other.y
    
    def components(self) -> list:
        '''x and y components of vector as a list'''
        return [self.x, self.y]

    def draw(self, surf:pg.surface.Surface, pos:"Vector", color:list, window:"Window"): # type: ignore
        '''draws a vector onto a surf'''
        # main segment
        wdw_pos = window.world_to_window(pos)
        wdw_end_pos = wdw_pos + self * VECT_PX_PER_UNIT * window.zoom_amt
        pg.draw.line(surf, color, wdw_pos.components(), wdw_end_pos.components(), width=VECT_THKNS)

        # arrowhead of drawn vector
        left_head_end = wdw_end_pos + Vector(VECT_HEAD_LEN * window.zoom_amt, self.angle + 3*pi/4, input_angle=True)
        right_head_end = wdw_end_pos + Vector(VECT_HEAD_LEN * window.zoom_amt, self.angle - 3*pi/4, input_angle=True)
        pg.draw.line(surf, color, wdw_end_pos.components(), left_head_end.components(), width=VECT_THKNS)
        pg.draw.line(surf, color, wdw_end_pos.components(), right_head_end.components(), width=VECT_THKNS)
