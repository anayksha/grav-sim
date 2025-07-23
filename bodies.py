import math
import random
import pygame as pg
from physics import Vector

from settings import SETTINGS

BODY_ICON_SET = SETTINGS["misc"]["BODY_ICON_SET"]

VELOCITY_CONST = SETTINGS["physics"]["VELOCITY_CONST"]

TRAIL_LEN = SETTINGS["trail"]["TRAIL_LEN"]
TRAIL_COLOR = SETTINGS["trail"]["TRAIL_COLOR"]
TRAIL_START_WIDTH = SETTINGS["trail"]["TRAIL_START_WIDTH"]
TRAIL_END_WIDTH = SETTINGS["trail"]["TRAIL_END_WIDTH"]

COLLISION_CONST = SETTINGS["physics"]["COLLISION_CONST"]
GRAV_CONST = SETTINGS["physics"]["GRAV_CONST"]
SIZE_CONST = SETTINGS["physics"]["SIZE_CONST"]

FONT_FILE = SETTINGS["font"]["FONT_FILE"]
FONT_SIZE = SETTINGS["font"]["FONT_SIZE"]
FONT_COLOR = SETTINGS["font"]["FONT_COLOR"]
TEXT_OFFSET = SETTINGS["font"]["TEXT_OFFSET"]

# find a better way to share settings across scripts
pg.font.init()
FONT = pg.font.Font(FONT_FILE, FONT_SIZE)

VELOCITY_LINE_COLOR = SETTINGS["misc"]["VELOCITY_LINE_COLOR"]
VELOCITY_LINE_THICKNESS = SETTINGS["misc"]["VELOCITY_LINE_THICKNESS"]

class Trail:
    '''
    a visual trail of an object's movement. basically a series of lines with
    a starting width that narrows down to an end width
    '''
    def __init__(self, length:int, color:tuple, start_width:int, end_width:int):
        '''Initializes a trail with a certain length, color, starting width, and ending width'''
        self.length = length # num of points in the trail
        self.color = color
        self.start_width = start_width
        self.end_width = end_width

        self.width_increment = (self.start_width - self.end_width) / (self.length - 1)
        self.trail_points = []

    def update_trail(self, point):
        '''
        updates the trail by adding a point to the front of the points list and removing
        the last point if the trail is too long
        '''
        self.trail_points.insert(0, point)

        if len(self.trail_points) > self.length:
            self.trail_points.pop()

    def draw_trail(self, surface:pg.surface.Surface):
        '''draws the trail onto the given surface'''
        for i in range(len(self.trail_points) - 1):
            start = self.trail_points[i]
            end = self.trail_points[i+1]
            pg.draw.line(surface, self.color, start, end, int(self.start_width - i*self.width_increment))

class Body:
    '''
    A celestial object with mass that exerts gravitational force on other objects.

    An Body can have one of 4 statuses, operational, setting mass, setting velocity, and
    fixed. An Body with the operational status works as normal. An Body has the setting mass status
    when it has been added in and the user is setting its mass. An Body has the setting velocity
    status when it has been added in and the user is setting its velocity. An Body that is fixed
    doesn't move, but it still exerts a gravitational force on other Objs. These statuses are 
    represented as strings, with "O", "M", "V", "F" for operational, changing mass, changing
    velocity, and fixed, respectively.
    '''
    def __init__(self, mass:float, pos:list, velocity:Vector=None, status:str="O"):
        '''
        Initializes an Body with a bunch of properties responsible for calculating
        the position of an Body over time as well as some visual properties

        velocity, accel, and pos are 2 item lists or tuples, with item at index
        0 being the x value and item at index 1 being the y value
        '''
        # necessary bc default arguments are shared by all instances of the class
        # so when we need to change it, it changes all instances
        if velocity is None:
            velocity = Vector(0, 0)

        # assigns the Body all of its properties that affect its behavior
        self.mass = mass
        self.pos = pos
        self.velocity = velocity
        self.accel = Vector(0, 0)
        self.status = status
        self.icon = random.choice(BODY_ICON_SET)

        # assumes each Body is made from the same material at a specific density so that
        # each kg of mass corresponds to a certain amount of surface area of the Body
        # Since radius and surface area are intertwined, the mass of the Body affects its radius
        self.update_surf()

        self.trail = Trail(TRAIL_LEN, TRAIL_COLOR, TRAIL_START_WIDTH, TRAIL_END_WIDTH)

    def calc_grav_force(self, other_obj:"Body") -> Vector:
        '''
        Calculates the acceleration one object faces due to the gravitational force
        between itself and one other object (other_obj) and then returns that
        '''
        # if the Body's status isn't operational, or other_obj is new and its status is
        # setting mass or setting velocity, the Body shouldn't accelerate
        if self.status != "O" or other_obj.status in ["M", "V"]:
            return Vector(0, 0)

        # calculates horizontal, vertical, and actual distance between the 2 Body to calculate accel
        dist_x = other_obj.pos[0] - self.pos[0]
        dist_y = other_obj.pos[1] - self.pos[1]
        dist = math.hypot(dist_x, dist_y)

        # only force is contact force if the 2 objects are inside each other
        if dist < (self.dia/2 + other_obj.dia/2):
            # random aah formula for contact acceleration as a function of distance the objs are inside eachother
            accel_magnitude = -COLLISION_CONST * (self.dia/2 + other_obj.dia/2 - dist)**2
            return Vector(accel_magnitude, math.atan2(dist_y, dist_x), input_angle=True)

        # uses an expression created from gravitation formula and F = ma to determine acceleration
        return Vector(GRAV_CONST * self.mass * other_obj.mass / dist**2, math.atan2(dist_y, dist_x), input_angle=True)

    def sum_accel(self, accelerations:list):
        '''Sums a list of acceleration lists and changes self.accel in place'''
        self.accel = sum(accelerations, Vector(0, 0))

    def change_velocity(self, delta_time:float):
        '''Changes self.velocity in place using self.accel and change in time'''
        self.velocity += self.accel * delta_time

    def move(self, delta_time:float):
        '''
        Changes the position of the object using its velocity and change in time
        passed between last and current frame

        also updates its trail
        '''
        self.pos[0] += self.velocity.x * delta_time
        self.pos[1] += self.velocity.y * delta_time

        self.trail.update_trail(tuple(self.pos))

    def display_attribute(self, surf, obj_attribute:str):
        '''
        meant to display an attribute below an Body

        the attribute's value and units are inputted as a str
        '''
        font_surf = FONT.render(obj_attribute, True, FONT_COLOR) # a pygame surface of the text
        # calculates where the center of the text should be
        text_coords = (self.pos[0], self.pos[1] + self.dia/2 + TEXT_OFFSET)
        surf.blit(font_surf, center_surf(font_surf, text_coords)) # blits the text onto the screen

    def update_surf(self):
        '''
        updates the radius of the Body based on its mass

        used when the user adds celestial objects with specific masses to the simulation
        '''
        self.dia = math.sqrt(self.mass) * SIZE_CONST

        if type(self.icon) is str: # assume its an image file
            self.surf = pg.image.load(self.icon)
            self.surf = pg.transform.scale(self.surf, (self.dia, self.dia))
        else: # assuming its an rgb triplet
            self.surf = pg.surface.Surface((self.dia, self.dia), pg.SRCALPHA)
            pg.draw.circle(self.surf, self.icon, (self.dia/2, self.dia/2), self.dia/2)

    def draw(self, surf:pg.surface.Surface):
        '''
        draws the celestial object and it's trail onto the pygame display, as well as mass or
        initial velocity if the Body is being added to the simulation
        '''
        self.trail.draw_trail(surf)

        # draws the Body, regardless of its status
        surf.blit(self.surf, center_surf(self.surf, self.pos))

        # if the Body's mass is being set
        if self.status == "M":
            mass = f"{self.mass:.1f} kg" # rounds mass and turns it to a string w/ units
            self.display_attribute(surf, mass)

        # if the Body's velocity is being set
        elif self.status == "V":
            # gets mouse pos for velocity calculations and drawing a line
            mouse_pos = pg.mouse.get_pos()

            dist_x = mouse_pos[0] - self.pos[0]
            dist_y = mouse_pos[1] - self.pos[1]

            velocity = f"{Vector(dist_x, dist_y).magnitude * VELOCITY_CONST:.2f} m/s"
            self.display_attribute(surf, velocity)

            # draws a line to display the direction of the velocity 
            pg.draw.line(surf, VELOCITY_LINE_COLOR, self.pos, mouse_pos, VELOCITY_LINE_THICKNESS)

# TODO: find a better place to put this
def center_surf(surface:pg.surface.Surface, coords:tuple) -> tuple:
    '''
    given the coordinates that the center of a pygame surface should be placed,
    this returns the coordinates that the top left corner of the surface should be placed
    (pygame uses the coordinates of the top left corner to blit surfaces)
    '''
    return (surface.get_width() / -2 + coords[0], surface.get_height() / -2 + coords[1])