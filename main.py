'''
This program uses the math and random python libraries as well as pygame,
and the font used is from fonts.google.com
This program was created individually.

This is basically a simulation that simulates the motion of celestial objects with
gravity in a 2D plane. This simulation uses some real formulas to simulate this motion.

When run, the program prompts the user to answer whether the celestial
objects should be neon colors. Type "yes" or "no" with the keyboard to answer.

To create a celestial object, click, hold, and drag to add one and set its mass. When the
desired mass has been set, release the left mouse button. To set the object's velocity, click
anywhere on the screen. The line shown while changing the object's velocity shows its
direction, and its length shows its speed.
'''
from math import sin, cos, pi
import pygame as pg

from physics import Vector
from bodies import Body
from world import World

from settings import SETTINGS


def on_event(event:pg.event.Event):
    '''
    A function that performs a specific action for specific events inputted
    '''
    global running
    # stop running quit if the pygame window is closed
    if event.type == pg.QUIT:
        running = False
        return

    # if world.bodies isn't populated, this should only check for a mouse click
    if not world.bodies:
        # add an Body if there isn't one in world.bodies and a mouse click is detected
        if event.type == pg.MOUSEBUTTONDOWN:
            world.bodies.append(Body(STARTING_MASS, Vector(*event.pos), Vector(0, 0), "M"))
        # stop the function, since it will throw an error with an unpopulated world.bodies
        return

    last_obj = world.bodies[-1] # the last Body appended to world.bodies

    # create a new object if there isn't one being created and add it to world.bodies
    if event.type == pg.MOUSEBUTTONDOWN and last_obj.status in ["O", "F"]:
        world.bodies.append(Body(STARTING_MASS, Vector(*event.pos), Vector(0, 0), "M"))

    # changes the mass and radius of an object being added in by changing
    # it with respect to the distance between the Body and the cursor
    elif event.type == pg.MOUSEMOTION and last_obj.status == "M":
        dist = Vector(*event.pos) - last_obj.pos
        last_obj.mass = dist.magnitude * MASS_CONST
        last_obj.update_surf()

    # If the last obj is an Body that was setting its mass and left click is released,
    # change its status to setting velocity
    elif event.type == pg.MOUSEBUTTONUP and last_obj.status == "M":
        last_obj.status = "V"

    # set the last_obj's velocity with respect to the distance between the mouse and the cursor
    # if the last_obj's mode was setting velocity. Also change the Body's status to operational
    elif event.type == pg.MOUSEBUTTONDOWN and last_obj.status == "V":
        dist = Vector(*event.pos) - last_obj.pos
        last_obj.velocity = dist * VELOCITY_CONST
        last_obj.status = "O"

def simulate():
    '''
    actually simulates the motion of the Objs, by calculating accel,
    changing velocity, and moving each Body
    '''
    while running:
        # delta_time is time passed between last and current frame in seconds
        # clock.tick() also limits the frames per second the simulation runs at
        delta_time = clock.tick(FPS) / 1000

        # responds to events that occur during the simulation
        for event in pg.event.get():
            on_event(event)

        # calculate motion of the Objs
        world.step(delta_time)

        # and then display them on the screen
        world.display(screen, background)

    # quit pygame when the simulation is no longer running
    pg.quit()

# TODO: move this to some diff module, mabye called goofy gimmicks idk 
def create_obj_circle(num:int, radius:int, center:tuple, mass:int=200, spd:float=0, state:str="F"):
    '''
    adds a circle with a certain radius of num objects with a certan mass, with a velocity
    perpendicular to the radius of the circle
    '''
    for i in range(num):
        angle = i * 2 * pi / num # angle of the object in radians
        pos = [center[0] + (radius * cos(angle)), center[1] + (radius * sin(angle))]
        vel = [spd * -sin(angle), spd * cos(angle)]
        world.bodies.append(Body(mass, pos, vel, state))

def world_pos():
    '''
    TODO: implement a function that yeilds a position in a world from
    position in a window by adjusting for zoom and camera panning
    '''
    pass

if __name__ == "__main__":

    MASS_CONST = SETTINGS["physics"]["MASS_CONST"]
    STARTING_MASS = SETTINGS["physics"]["STARTING_MASS"]
    VELOCITY_CONST = SETTINGS["physics"]["VELOCITY_CONST"]

    # visual constants
    FPS = SETTINGS["window"]["FPS"]
    SCREEN_SIZE = SETTINGS["window"]["SCREEN_SIZE"]
    WINDOW_TITLE = SETTINGS["window"]["WINDOW_TITLE"]
    BACKGROUND_IMG = SETTINGS["window"]["BACKGROUND_IMG"]

    # sets up pygame
    pg.init()

    # sets up the window that will render everything
    screen = pg.display.set_mode(SCREEN_SIZE)
    pg.display.set_caption(WINDOW_TITLE)
    background = pg.image.load(BACKGROUND_IMG)
    background = pg.transform.scale(background, SCREEN_SIZE)

    world = World() # creates a world of Objs that can be used to simulate gravity

    clock = pg.time.Clock() # sets up the clock so time can be used for calculations

    running = True # setting running to True allows for the simulation to start

    simulate()