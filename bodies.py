from math import sqrt
import random
import pygame as pg

from vector import Vector
from window import Window

from settings import SETTINGS

TRAIL_LEN = SETTINGS["trail"]["TRAIL_LEN"]
TRAIL_COLOR = SETTINGS["trail"]["TRAIL_COLOR"]
TRAIL_START_WIDTH = SETTINGS["trail"]["TRAIL_START_WIDTH"]
TRAIL_END_WIDTH = SETTINGS["trail"]["TRAIL_END_WIDTH"]

GRAV_CONST = SETTINGS["physics"]["GRAV_CONST"]

VELOCITY_CONST = SETTINGS["misc_constants"]["VELOCITY_CONST"]
SIZE_CONST = SETTINGS["misc_constants"]["SIZE_CONST"]

FONT_FILE = SETTINGS["font"]["FONT_FILE"]
FONT_SIZE = SETTINGS["font"]["FONT_SIZE"]
FONT_COLOR = SETTINGS["font"]["FONT_COLOR"]

BODY_ICON_SET = SETTINGS["other_visuals"]["BODY_ICON_SET"]
TEXT_OFFSET = SETTINGS["other_visuals"]["TEXT_OFFSET"]

ACCEL_VECT_COLOR = SETTINGS["vector_visuals"]["ACCEL_VECT_COLOR"]
VELOCITY_VECT_COLOR = SETTINGS["vector_visuals"]["VELOCITY_VECT_COLOR"]

# TODO: find a better way to share settings across scripts
# UPDATE: I dont wanna do that
pg.font.init()
FONT = pg.font.Font(FONT_FILE, FONT_SIZE)

VELOCITY_LINE_COLOR = SETTINGS["other_visuals"]["VELOCITY_LINE_COLOR"]
VELOCITY_LINE_THICKNESS = SETTINGS["other_visuals"]["VELOCITY_LINE_THICKNESS"]

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

    def draw_trail(self, surface:pg.surface.Surface, window:Window):
        '''draws the trail onto the given surface'''
        for i in range(len(self.trail_points) - 1):
            start = window.world_to_window(Vector(*self.trail_points[i]))
            end = window.world_to_window(Vector(*self.trail_points[i+1]))
            pg.draw.line(surface, self.color, start.components(), end.components(), int(self.start_width - i*self.width_increment))

class Body:
    '''
    A rigid body with mass and the ability to move idk how do i explain this.

    An Body can have one of 4 statuses, operational, setting mass, setting velocity, and
    fixed. An Body with the operational status works as normal. An Body has the setting mass status
    when it has been added in and the user is setting its mass. An Body has the setting velocity
    status when it has been added in and the user is setting its velocity. An Body that is fixed
    doesn't move, but it still exerts a gravitational force on other Objs. These statuses are 
    represented as strings, with "O", "M", "V", "F" for operational, changing mass, changing
    velocity, and fixed, respectively.
    '''
    def __init__(self, mass:float, pos:Vector, velocity:Vector=Vector(0, 0), status:str="O"):
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
        self.update_surf(0.1)

        self.trail = Trail(TRAIL_LEN, TRAIL_COLOR, TRAIL_START_WIDTH, TRAIL_END_WIDTH)

    def change_velocity(self, delta_time:float):
        '''Changes self.velocity in place using self.accel and change in time'''
        self.velocity += self.accel * delta_time

    def move(self, delta_time:float):
        '''
        Changes the position of the object using its velocity and change in time
        passed between last and current frame

        also updates its trail
        '''
        self.pos += self.velocity * delta_time

        self.trail.update_trail(self.pos.components())

    def display_attribute(self, surf, obj_attribute:str, window:Window):
        '''
        meant to display an attribute below an Body

        the attribute's value and units are inputted as a str
        '''
        font_surf = FONT.render(obj_attribute, True, FONT_COLOR) # a pygame surface of the text
        # calculates where the center of the text should be
        wdw_pos = window.world_to_window(self.pos)
        text_coords = (wdw_pos.x, wdw_pos.y + self.dia*window.zoom_amt/2 + TEXT_OFFSET)
        surf.blit(font_surf, center_surf(font_surf, text_coords)) # blits the text onto the screen

    def update_surf(self, zoom:float):
        '''
        updates the radius of the Body based on its mass

        used when the user adds celestial objects with specific masses to the simulation
        '''
        self.dia = sqrt(self.mass) * SIZE_CONST

        # diameter in window, adjusted for zoom
        wdw_dia = self.dia * zoom

        if type(self.icon) is str: # assume its an image file
            self.surf = pg.image.load(self.icon)
            self.surf = pg.transform.scale(self.surf, (wdw_dia, wdw_dia))
        else: # assuming its an rgb triplet
            self.surf = pg.surface.Surface((wdw_dia, wdw_dia), pg.SRCALPHA)
            pg.draw.circle(self.surf, self.icon, (wdw_dia/2, wdw_dia/2), wdw_dia/2)

    def draw(self, surf:pg.surface.Surface, window:Window, disp_vects:bool):
        '''
        draws the celestial object and it's trail onto the pygame display, as well as mass or
        initial velocity if the Body is being added to the simulation
        '''
        self.trail.draw_trail(surf, window)

        wdw_pos = window.world_to_window(self.pos)

        # draws the Body, regardless of its status
        surf.blit(self.surf, center_surf(self.surf, wdw_pos.components()))

        # draw velocity and accel vectors if disp_vects is true
        if disp_vects:
            self.accel.draw(surf, self.pos, ACCEL_VECT_COLOR, window)
            self.velocity.draw(surf, self.pos, VELOCITY_VECT_COLOR, window)
        
        # if the Body's mass is being set
        if self.status == "M":
            mass = f"{self.mass:.1f} kg" # rounds mass and turns it to a string w/ units
            self.display_attribute(surf, mass, window)

        # if the Body's velocity is being set
        elif self.status == "V":
            # gets mouse pos for velocity calculations and drawing a line
            mouse_pos = pg.mouse.get_pos()

            dist = Vector(*mouse_pos) - wdw_pos

            velocity = f"{dist.magnitude * VELOCITY_CONST:.2f} m/s"
            self.display_attribute(surf, velocity, window)

            # draws a line to display the direction of the velocity
            pg.draw.line(surf, VELOCITY_LINE_COLOR, wdw_pos.components(), mouse_pos, VELOCITY_LINE_THICKNESS)

# TODO: find a better place to put this
def center_surf(surface:pg.surface.Surface, coords:tuple) -> tuple:
    '''
    given the coordinates that the center of a pygame surface should be placed,
    this returns the coordinates that the top left corner of the surface should be placed
    (pygame uses the coordinates of the top left corner to blit surfaces)
    '''
    return (surface.get_width() / -2 + coords[0], surface.get_height() / -2 + coords[1])