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

TODO: add comments for trail, center of mass, and other stuff
'''
import math
import pygame as pg

from physics import Vector

from bodies import Body

from settings import SETTINGS


def on_event(event:pg.event.Event):
    '''
    A function that performs a specific action for specific events inputted
    '''
    global running
    # stop running quit if the pygame window is closed
    if event.type == pg.QUIT:
        running = False

    # if celestial_obj isn't populated, this should only check for a mouse click
    if not celestial_objs:
        # add an Body if there isn't one in celestial_objs and a mouse click is detected
        if event.type == pg.MOUSEBUTTONDOWN:
            celestial_objs.append(Body(STARTING_MASS, list(event.pos), Vector(0, 0), "M"))
        # stop the function, since it will throw an error with an unpopulated celestial_objs
        return

    last_obj = celestial_objs[-1] # the last Body appended to celestial_objs

    # create a new object if there isn't one being created and add it to celestial_objs
    if event.type == pg.MOUSEBUTTONDOWN and last_obj.status in ["O", "F"]:
        celestial_objs.append(Body(STARTING_MASS, list(event.pos), Vector(0, 0), "M"))

    # changes the mass and radius of an object being added in by changing
    # it with respect to the distance between the Body and the cursor
    elif event.type == pg.MOUSEMOTION and last_obj.status == "M":
        dist_x = event.pos[0] - last_obj.pos[0]
        dist_y = event.pos[1] - last_obj.pos[1]
        last_obj.mass = math.hypot(dist_x, dist_y) * MASS_CONST
        last_obj.update_surf()

    # If the last obj is an Body that was setting its mass and left click is released,
    # change its status to setting velocity
    elif event.type == pg.MOUSEBUTTONUP and last_obj.status == "M":
        last_obj.status = "V"

    # set the last_obj's velocity with respect to the distance between the mouse and the cursor
    # if the last_obj's mode was setting velocity. Also change the Body's status to operational
    elif event.type == pg.MOUSEBUTTONDOWN and last_obj.status == "V":
        dist_x = event.pos[0] - last_obj.pos[0]
        dist_y = event.pos[1] - last_obj.pos[1]
        last_obj.velocity = Vector(dist_x, dist_y) * VELOCITY_CONST
        last_obj.status = "O"

def calculate_mvt(delta_time:float):
    '''
    changes the position of each object by calculating the accel
    caused by every other object, summing the accels, and then
    calculating velocity and changing position
    '''
    # for each Body in celestial_objs, calculate the accel caused by all other Objs
    for i in range(len(celestial_objs) - 1):

        for j in range(i + 1, len(celestial_objs)):
            # if obj and other_obj are not the same, calculate accel
            force = celestial_objs[i].calc_grav_force(celestial_objs[j])
            celestial_objs[i].accel += force / celestial_objs[i].mass
            celestial_objs[j].accel += -force / celestial_objs[j].mass

    # once the accels for all Objs are calculated, move them all
    # this is separated from the main loop because moving the objects
    # as calculating the motions of the other objects would change the calculations
    for obj in celestial_objs:
        obj.change_velocity(delta_time)
        obj.move(delta_time)
        obj.accel = Vector(0, 0)

def display_com(objs:list, surface:pg.surface.Surface):
    '''
    draws the center of mass of a list of objs on a surface as a hollow circle
    '''
    total_mass = sum(obj.mass for obj in objs)
    com_x = sum(obj.mass * obj.pos[0] for obj in objs) / total_mass
    com_y = sum(obj.mass * obj.pos[1] for obj in objs) / total_mass

    pg.draw.circle(surface, COM_COLOR, (com_x, com_y), COM_CIRCLE_RADIUS, COM_CIRCLE_WIDTH)

def display():
    '''
    displays everything in the pygame window, including the motion
    of the Objs
    '''
    screen.blit(background, (0, 0)) # draws background every frame to reset screen

    # draws each Body in celestial_objs
    for obj in celestial_objs:
        obj.draw(screen)

    # if celestial_objs:
    #     display_com(celestial_objs, screen)

    pg.display.flip() # display everything on the screen

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
        calculate_mvt(delta_time)

        # and then display them on the screen
        display()

    # quit pygame when the simulation is no longer running
    pg.quit()

def create_obj_circle(num:int, radius:int, center:tuple, mass:int=200, spd:float=0, state:str="F"):
    '''
    adds a circle with a certain radius of num objects with a certan mass, with a velocity
    perpendicular to the radius of the circle
    '''
    for i in range(num):
        angle = i * 2 * math.pi / num # angle of the object in radians
        pos = [center[0] + (radius * math.cos(angle)), center[1] + (radius * math.sin(angle))]
        vel = [spd * -math.sin(angle), spd * math.cos(angle)]
        celestial_objs.append(Body(mass, pos, vel, state))

if __name__ == "__main__":

    MASS_CONST = SETTINGS["physics"]["MASS_CONST"]
    STARTING_MASS = SETTINGS["physics"]["STARTING_MASS"]
    VELOCITY_CONST = SETTINGS["physics"]["VELOCITY_CONST"]

    # visual constants
    FPS = SETTINGS["window"]["FPS"]
    SCREEN_SIZE = SETTINGS["window"]["SCREEN_SIZE"]
    WINDOW_TITLE = SETTINGS["window"]["WINDOW_TITLE"]
    BACKGROUND_IMG = SETTINGS["window"]["BACKGROUND_IMG"]

    # Center of mass settings
    COM_CIRCLE_RADIUS = SETTINGS["COM"]["COM_CIRCLE_RADIUS"]
    COM_CIRCLE_WIDTH = SETTINGS["COM"]["COM_CIRCLE_WIDTH"]
    COM_COLOR = SETTINGS["COM"]["COM_COLOR"]

    # sets up pygame
    pg.init()

    # sets up the window that will render everything
    screen = pg.display.set_mode(SCREEN_SIZE)
    pg.display.set_caption(WINDOW_TITLE)
    background = pg.image.load(BACKGROUND_IMG)
    background = pg.transform.scale(background, SCREEN_SIZE)

    celestial_objs = [] # creates a list of Objs that can be iterated through to simulate gravity

    clock = pg.time.Clock() # sets up the clock so time can be used for calculations

    running = True # setting running to True allows for the simulation to start

    simulate()