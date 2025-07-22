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

# physics related constants
GRAV_CONST = 1000 # gravitational constant determines how strong gravity is
SIZE_CONST = 2 # how much mass affects radius of object
MASS_CONST = 10 # 4.5 # how much user input affects an added Obj's mass
STARTING_MASS = 20 # mass of an Obj when it is just added in by mouse input
VELOCITY_CONST = 0.9 # 0.6 # how much user input affects an added Obj's velocity
COLLISION_CONST = 100000 # affects magnitude of force per pixel of distance that 2 objs are inside each other

# visual constants
FPS = 60 # frames per second to simulate at; set to 0 to have unlimited framerate
SCREEN_SIZE = (1600, 900) # width and height of pygame window
WINDOW_TITLE = "Gravity Simulator"
BACKGROUND_IMG = "stars.png" # filename of the background

# obj display attribute settings
FONT_FILE = "SpaceMono-Regular.ttf" # filename of the font
FONT_SIZE = 16
FONT_COLOR = (255,255,255) # rgb triplet of font color
TEXT_OFFSET = 14 # how much pixels the center of text appears below the bottom of an Obj

# color of the line that shows the direction of an added Obj's velocity
VELOCITY_LINE_COLOR = (255,255,255)
VELOCITY_LINE_THICKNESS = 2 # thickness of the line shown while setting an Obj's velocity

# Center of mass settings
COM_CIRCLE_RADIUS = 10 # radius of circle that displays center of mass
COM_CIRCLE_WIDTH = 3 # width of circle that displays center of mass
COM_COLOR = (200, 200, 200) # color of circle that displays center of mass

# Trail settings
TRAIL_LEN = 25 # len of trail in number of points
TRAIL_COLOR = (255, 255, 255)
TRAIL_START_WIDTH = 6
TRAIL_END_WIDTH = 1

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

class Obj:
    '''
    A celestial object with mass that exerts gravitational force on other objects.

    An Obj can have one of 4 statuses, operational, setting mass, setting velocity, and
    fixed. An Obj with the operational status works as normal. An Obj has the setting mass status
    when it has been added in and the user is setting its mass. An Obj has the setting velocity
    status when it has been added in and the user is setting its velocity. An Obj that is fixed
    doesn't move, but it still exerts a gravitational force on other Objs. These statuses are 
    represented as strings, with "O", "M", "V", "F" for operational, changing mass, changing
    velocity, and fixed, respectively.
    '''
    def __init__(self, mass:float, pos:list, velocity:list=None, status:str="O"):
        '''
        Initializes an Obj with a bunch of properties responsible for calculating
        the position of an Obj over time as well as some visual properties

        velocity, accel, and pos are 2 item lists or tuples, with item at index
        0 being the x value and item at index 1 being the y value
        '''
        # necessary bc default arguments are shared by all instances of the class
        # so when we need to change it, it changes all instances
        if velocity is None:
            velocity = [0, 0]

        # assigns the Obj all of its properties that affect its behavior
        self.mass = mass
        self.pos = pos
        self.velocity = velocity
        self.accel = (0, 0)
        self.status = status

        # assumes each Obj is made from the same material at a specific density so that
        # each kg of mass corresponds to a certain amount of surface area of the Obj
        # Since radius and surface area are intertwined, the mass of the Obj affects its radius
        self.update_size()

        self.trail = Trail(TRAIL_LEN, TRAIL_COLOR, TRAIL_START_WIDTH, TRAIL_END_WIDTH)

    def calc_accel(self, other_obj:"Obj") -> tuple:
        '''
        Calculates the acceleration one object faces due to the gravitational force
        between itself and one other object (other_obj) and then returns that
        '''
        # if the Obj's status isn't operational, or other_obj is new and its status is
        # setting mass or setting velocity, the Obj shouldn't accelerate
        if self.status != "O" or other_obj.status in ["M", "V"]:
            return (0, 0)

        # calculates horizontal, vertical, and actual distance between the 2 Obj to calculate accel
        dist_x = other_obj.pos[0] - self.pos[0]
        dist_y = other_obj.pos[1] - self.pos[1]
        dist = math.hypot(dist_x, dist_y)

        # only force is contact force if the 2 objects are inside each other
        if dist < (self.size/2 + other_obj.size/2):
            # random aah formula for contact acceleration as a function of distance the objs are inside eachother
            accel_magnitude = -COLLISION_CONST * (self.size/2 + other_obj.size/2 - dist)**2 / self.mass
            return split_vector(accel_magnitude, math.atan2(dist_y, dist_x))

        # uses an expression created from gravitation formula and F = ma to determine acceleration
        return split_vector(GRAV_CONST * other_obj.mass / dist**2, math.atan2(dist_y, dist_x))

    def sum_accel(self, accelerations:list):
        '''Sums a list of acceleration lists and changes self.accel in place'''
        accel_x = sum(accel[0] for accel in accelerations)
        accel_y = sum(accel[1] for accel in accelerations)
        self.accel = (accel_x, accel_y)

    def change_velocity(self, delta_time:float):
        '''Changes self.velocity in place using self.accel and change in time'''
        self.velocity[0] += self.accel[0] * delta_time
        self.velocity[1] += self.accel[1] * delta_time

    def move(self, delta_time:float):
        '''
        Changes the position of the object using its velocity and change in time
        passed between last and current frame

        also updates its trail
        '''
        self.pos[0] += self.velocity[0] * delta_time
        self.pos[1] += self.velocity[1] * delta_time

        self.trail.update_trail(tuple(self.pos))

    def display_attribute(self, obj_attribute:str):
        '''
        meant to display an attribute below an Obj

        the attribute's value and units are inputted as a str
        '''
        font_surf = font.render(obj_attribute, True, FONT_COLOR) # a pygame surface of the text
        # calculates where the center of the text should be
        text_coords = (self.pos[0], self.pos[1] + self.size/2 + TEXT_OFFSET)
        screen.blit(font_surf, center_surf(font_surf, text_coords)) # blits the text onto the screen

    def update_size(self):
        '''
        updates the radius of the Obj based on its mass

        used when the user adds celestial objects with specific masses to the simulation
        '''
        self.image = pg.image.load("lebron.png")
        self.size = math.sqrt(self.mass) * SIZE_CONST
        self.image = pg.transform.scale(self.image, (self.size, self.size))

    def draw(self):
        '''
        draws the celestial object and it's trail onto the pygame display, as well as mass or
        initial velocity if the Obj is being added to the simulation
        '''
        self.trail.draw_trail(screen)

        # draws the Obj, regardless of its status
        screen.blit(self.image, center_surf(self.image, self.pos))

        # if the Obj's mass is being set
        if self.status == "M":
            mass = f"{self.mass:.1f} kg" # rounds mass and turns it to a string w/ units
            self.display_attribute(mass)

        # if the Obj's velocity is being set
        elif self.status == "V":
            # gets mouse pos for velocity calculations and drawing a line
            mouse_pos = pg.mouse.get_pos()

            # calculates velocity with the distance between the mouse and the Obj
            dist_x = mouse_pos[0] - self.pos[0]
            dist_y = mouse_pos[1] - self.pos[1]
            # rounds velocity and turns it to a string w/ units
            velocity = f"{math.hypot(dist_x, dist_y) * VELOCITY_CONST:.2f} m/s"
            self.display_attribute(velocity)

            # draws a line to display the direction of the velocity 
            pg.draw.line(screen, VELOCITY_LINE_COLOR, self.pos, mouse_pos, VELOCITY_LINE_THICKNESS)

def split_vector(magnitude:float, angle:float) -> tuple:
    '''
    returns a vector as a x and y component when inputted
    its direction and magnitude
    '''
    return (magnitude * math.cos(angle), magnitude * math.sin(angle))

# TODO: add vectorization function

def center_surf(surface:pg.surface.Surface, coords:tuple) -> tuple:
    '''
    given the coordinates that the center of a pygame surface should be placed,
    this returns the coordinates that the top left corner of the surface should be placed
    (pygame uses the coordinates of the top left corner to blit surfaces)
    '''
    return (surface.get_width() / -2 + coords[0], surface.get_height() / -2 + coords[1])

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
        # add an Obj if there isn't one in celestial_objs and a mouse click is detected
        if event.type == pg.MOUSEBUTTONDOWN:
            celestial_objs.append(Obj(STARTING_MASS, list(event.pos), [0, 0], "M"))
        # stop the function, since it will throw an error with an unpopulated celestial_objs
        return

    last_obj = celestial_objs[-1] # the last Obj appended to celestial_objs

    # create a new object if there isn't one being created and add it to celestial_objs
    if event.type == pg.MOUSEBUTTONDOWN and last_obj.status in ["O", "F"]:
        celestial_objs.append(Obj(STARTING_MASS, list(event.pos), [0, 0], "M"))

    # changes the mass and radius of an object being added in by changing
    # it with respect to the distance between the Obj and the cursor
    elif event.type == pg.MOUSEMOTION and last_obj.status == "M":
        dist_x = event.pos[0] - last_obj.pos[0]
        dist_y = event.pos[1] - last_obj.pos[1]
        last_obj.mass = math.hypot(dist_x, dist_y) * MASS_CONST
        last_obj.update_size()

    # If the last obj is an Obj that was setting its mass and left click is released,
    # change its status to setting velocity
    elif event.type == pg.MOUSEBUTTONUP and last_obj.status == "M":
        last_obj.status = "V"

    # set the last_obj's velocity with respect to the distance between the mouse and the cursor
    # if the last_obj's mode was setting velocity. Also change the Obj's status to operational
    elif event.type == pg.MOUSEBUTTONDOWN and last_obj.status == "V":
        dist_x = event.pos[0] - last_obj.pos[0]
        dist_y = event.pos[1] - last_obj.pos[1]
        last_obj.velocity = [dist_x * VELOCITY_CONST, dist_y * VELOCITY_CONST]
        last_obj.status = "O"

def calculate_mvt(delta_time:float):
    '''
    changes the position of each object by calculating the accel
    caused by every other object, summing the accels, and then
    calculating velocity and changing position
    '''
    # for each Obj in celestial_objs, calculate the accel caused by all other Objs
    for obj in celestial_objs:
        accels = []

        for other_obj in celestial_objs:
            # if obj and other_obj are not the same, calculate accel
            if other_obj is not obj:
                accels.append(obj.calc_accel(other_obj))

        # sum all of the accels calculated and change velocity
        obj.sum_accel(accels)
        obj.change_velocity(delta_time)

    # once the accels for all Objs are calculated, move them all
    # this is separated from the main loop because moving the objects
    # as calculating the motions of the other objects would change the calculations
    for obj in celestial_objs:
        obj.move(delta_time)

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

    # draws each Obj in celestial_objs
    for obj in celestial_objs:
        obj.draw()

    # if celestial_objs:
    #     display_com(celestial_objs, screen)

    pg.display.flip() # display everything on the screen

def simulate():
    '''
    actually simulates the motion of the Objs, by calculating accel,
    changing velocity, and moving each Obj
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
        celestial_objs.append(Obj(mass, pos, vel, state))

if __name__ == "__main__":
    # sets up pygame
    pg.init()

    # sets up the window that will render everything
    screen = pg.display.set_mode(SCREEN_SIZE)
    pg.display.set_caption(WINDOW_TITLE)
    background = pg.image.load(BACKGROUND_IMG)
    background = pg.transform.scale(background, SCREEN_SIZE)

    # loads the font used for displaying text
    font = pg.font.Font(FONT_FILE, FONT_SIZE)

    celestial_objs = [] # creates a list of Objs that can be iterated through to simulate gravity

    clock = pg.time.Clock() # sets up the clock so time can be used for calculations

    running = True # setting running to True allows for the simulation to start

    simulate()