'''
This is basically a simulation that simulates the motion of rigid bodies with
gravity in a 2D plane.

To create a celestial object, click, hold, and drag to add one and set its mass. When the
desired mass has been set, release the left mouse button. To set the object's velocity, click
anywhere on the screen. The line shown while setting the object's velocity shows its
direction, and its length shows its speed.
'''
from math import sin, cos, pi
import pygame as pg

from vector import Vector
from bodies import Body
from world import World
from window import Window

from settings import SETTINGS

GRAV_CONST = SETTINGS["physics"]["GRAV_CONST"]

MASS_CONST = SETTINGS["misc_constants"]["MASS_CONST"]
STARTING_MASS = SETTINGS["misc_constants"]["STARTING_MASS"]
VELOCITY_CONST = SETTINGS["misc_constants"]["VELOCITY_CONST"]

FPS = SETTINGS["window"]["FPS"]
SCREEN_SIZE = SETTINGS["window"]["SCREEN_SIZE"]
WINDOW_TITLE = SETTINGS["window"]["WINDOW_TITLE"]
BACKGROUND_IMG = SETTINGS["window"]["BACKGROUND_IMG"]
ZOOM_INCREMENT = SETTINGS["window"]["ZOOM_INCREMENT"]
PAN_INCREMENT = SETTINGS["window"]["PAN_INCREMENT"]

def on_event(event:pg.event.Event):
    '''
    A function that performs a specific action for specific events inputted
    '''
    global running, disp_vects

    # stop running quit if the pygame window is closed
    if event.type == pg.QUIT:
        running = False
        return

    if event.type == pg.MOUSEWHEEL:
        window.zoom(event.y * ZOOM_INCREMENT, world)
        return
    
    if event.type == pg.KEYDOWN:
        if event.unicode == "v":
            disp_vects = not disp_vects # toggle displaying velocity and acceleration vectors
        return

    # if world.bodies isn't populated, this should only check for a mouse click
    if not world.bodies:
        # add an Body if there isn't one in world.bodies and a mouse click is detected
        # the not in [4, 5] thing is needed bc apparently a scroll is also registered as a MOUSEBUTTONDOWN event
        if event.type == pg.MOUSEBUTTONDOWN and event.button not in [4, 5]:
            wld_pos = window.window_to_world(Vector(*event.pos))
            world.add_body(Body(STARTING_MASS, wld_pos, status="M"))
        # stop the function, since it will throw an error with an unpopulated world.bodies
        return

    last_obj = world.bodies[-1] # the last Body appended to world.bodies

    # create a new body if there isn't one being created and add it to the world
    if event.type == pg.MOUSEBUTTONDOWN and last_obj.status in ["O", "F"] and event.button not in [4, 5]:
        wld_pos = window.window_to_world(Vector(*event.pos))
        world.add_body(Body(STARTING_MASS, wld_pos, status="M"))
        return

    # changes the mass and radius of an object being added in by changing
    # it with respect to the distance between the Body and the cursor in the window
    elif event.type == pg.MOUSEMOTION and last_obj.status == "M":
        dist = Vector(*event.pos) - window.world_to_window(last_obj.pos)
        # needed cause mouse can be exactly at the position of body, resulting in a distance of 0
        if dist.magnitude == 0:
            last_obj.mass = STARTING_MASS
        else:
            last_obj.mass = dist.magnitude * MASS_CONST
        last_obj.update_surf(window.zoom_amt)
        return

    # If the last obj is an Body that was setting its mass and left click is released,
    # change its status to setting velocity
    elif event.type == pg.MOUSEBUTTONUP and last_obj.status == "M" and event.button not in [4, 5]:
        last_obj.status = "V"
        return

    # set the last_obj's velocity with respect to the distance between the mouse and the cursor
    # if the last_obj's mode was setting velocity. Also change the Body's status to operational
    elif event.type == pg.MOUSEBUTTONDOWN and last_obj.status == "V" and event.button not in [4, 5]:
        dist = Vector(*event.pos) - window.world_to_window(last_obj.pos)
        last_obj.velocity = dist * VELOCITY_CONST
        last_obj.status = "O"
        return

def manage_keyboard_input():
    '''
    used to check for key presses;
    cant put this stuff in on event bc pygame only sends one event when
    a key is pressed and held
    '''
    keys = pg.key.get_pressed()

    # pan window with wasd
    if keys[pg.K_w]:
        window.pan(Vector(0, -PAN_INCREMENT/window.zoom_amt))
    if keys[pg.K_a]:
        window.pan(Vector(-PAN_INCREMENT/window.zoom_amt, 0))
    if keys[pg.K_s]:
        window.pan(Vector(0, PAN_INCREMENT/window.zoom_amt))
    if keys[pg.K_d]:
        window.pan(Vector(PAN_INCREMENT/window.zoom_amt, 0))

def simulate():
    '''
    actually simulates the motion of the Objs, manages keyboard and mouse input
    and displays everything
    '''
    while running:
        # delta_time is time passed between last and current frame in seconds
        # clock.tick() also limits the frames per second the simulation runs at
        delta_time = clock.tick(FPS) / 1000

        # responds to events that occur during the simulation
        for event in pg.event.get():
            on_event(event)

        # TODO: move this somewhere better
        manage_keyboard_input()

        # calculate motion of the Objs
        world.step(delta_time)

        # and then display them on the screen
        world.display(screen, background, window, disp_vects)

    # quit pygame when the simulation is no longer running
    pg.quit()

# TODO: mabye move this to some diff module, mabye called goofy gimmicks idk 
def create_obj_circle(num:int, radius:int, center:tuple, mass:int=200, spd:float=0, state:str="F"):
    '''
    adds a circle with a certain radius of num objects with a certan mass, with a velocity
    perpendicular to the radius of the circle
    '''
    for i in range(num):
        angle = i * 2 * pi / num # angle of the object in radians
        pos = Vector(center[0] + (radius * cos(angle)), center[1] + (radius * sin(angle)))
        vel = Vector(spd * -sin(angle), spd * cos(angle))
        world.bodies.append(Body(mass, pos, vel, state))

if __name__ == "__main__":

    # sets up pygame
    pg.init()

    # sets up the window that will render everything
    screen = pg.display.set_mode(SCREEN_SIZE)
    pg.display.set_caption(WINDOW_TITLE)
    background = pg.image.load(BACKGROUND_IMG)
    background = pg.transform.scale(background, SCREEN_SIZE)

    world = World() # creates a world of Objs that can be used to simulate gravity
    window = Window() # create window to manage zoom, panning, and coordinate conversion

    clock = pg.time.Clock() # sets up the clock so time can be used for calculations

    disp_vects = False # bool for togglning the display of accel and velocity vectors
    running = True # setting running to True allows for the simulation to start

    simulate() # start yay