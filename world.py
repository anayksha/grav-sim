from math import sqrt
import pygame as pg

from vector import Vector
from bodies import Body

from settings import SETTINGS

SCREEN_SIZE = SETTINGS["window"]["SCREEN_SIZE"]

GRAV_CONST = SETTINGS["physics"]["GRAV_CONST"]
RESTITUTION_COEFF = SETTINGS["physics"]["RESTITUTION_COEFF"]
GRAV_THRESHOLD = SETTINGS["physics"]["GRAV_THRESHOLD"]
SIM_WIDTH = SETTINGS["physics"]["SIM_WIDTH"]
SIM_HEIGHT = SETTINGS["physics"]["SIM_HEIGHT"]
MIN_POS_X = -SIM_WIDTH / 2
MAX_POS_X = MIN_POS_X + SIM_WIDTH
MIN_POS_Y = -SIM_HEIGHT / 2
MAX_POS_Y = MIN_POS_Y + SIM_HEIGHT

class World:
    '''
    physics world for storing and simulating a set of bodies
    '''
    def __init__(self):
        self.bodies = []

    def add_body(self, body:Body):
        '''adds a Body to self.bodies'''
        self.bodies.append(body)

    def check_collision(self, body1:Body, body2:Body):
        '''returns if there is a collision between 2 active Bodies'''
        return body1.status not in ["M", "V"] and body2.status not in ["M", "V"] and \
        (body2.pos - body1.pos).magnitude <= (body1.dia + body2.dia)/2

    def resolve_collisions(self, body1:Body, body2:Body, delta_time):
        '''
        so this uses a really complicated and goofy formula to reposition bodies
        that are intersecting eachother

        its called continuous collission detection, and basically finds the point in time where the 2
        bodies would have been touching by assuming that they were both travelling in a straight line
        between the last frame and current frame. It was some really complicated vector algebra that I
        couldn't solve but JoelBiswas did.

        The collision reaction mechanism uses some formula to calculate the impulse betweeen 2 colliding
        Bodies by Chris Hecker bc I honestly didn't know how 2D collisions between 2 bodies worked. Its derived
        from momentum and conservation of energy formulas though.

        Also as of right now, i don't think collisions between a non-fixed body and a fixed body properly works rn

        TODO: mabye implement more basic collision resolution method if cross product of velocities is small
        bc its still selling when restitution is not 1 or when more than 2 things collide
        '''
        # only check for collisions between active Bodies
        if body1.status in ["M", "V"] or body2.status in ["M", "V"]:
            return

        # delete the trail point that was created when the 2 bodies intersected one another
        del body1.trail.trail_points[0]
        del body2.trail.trail_points[0]

        # math and physics begin
        vel_diff = body2.velocity - body1.velocity
        pos_diff = body2.pos - body1.pos

        a = vel_diff.dot(vel_diff)
        b = 2 * vel_diff.dot(pos_diff)
        c = pos_diff.dot(pos_diff) - ((body1.dia + body2.dia) / 2)**2

        # quadratic formula aah
        # time when collission should have occured relative to current time so is a negative value
        time = (-b - sqrt(b**2 - 4 * a * c)) / (2 * a)

        # repositions Bodies so they're barely touching
        body1.pos += body1.velocity * time
        body2.pos += body2.velocity * time

        # actually using momentum to find new velocities now
        rel_vel = body1.velocity - body2.velocity # relative velocity
        normal = Vector(1, (body2.pos-body1.pos).angle, input_angle=True)

        impulse = (rel_vel * -(1 + RESTITUTION_COEFF)).dot(normal)
        impulse /= (1 / body1.mass) + (1 / body2.mass)

        # changed accel instead of directly changing velocity with impulse bc I wanted to display
        # the acceleration vector during collisions too
        body1.accel += normal * (impulse / delta_time / body1.mass)
        body2.accel -= normal * (impulse / delta_time / body2.mass)

        body1.change_velocity(delta_time)
        body2.change_velocity(delta_time)

        # because the collison occured between frames, uses the time remaning after collision
        # to reposition bodies with the new velocity
        body1.move(delta_time + time)
        body2.move(delta_time + time)

    def remove_far_bodies(self):
        '''deletes bodies out of bounds from world.bodies'''
        to_remove = []

        for i in range(len(self.bodies)):
            body = self.bodies[i]
            if not (MIN_POS_X <= body.pos.x <= MAX_POS_X) or \
            not (MIN_POS_Y <= body.pos.y <= MAX_POS_Y):
                to_remove.append(i)

        for i in to_remove:
            del self.bodies[i]

    def calc_grav_force(self, body1:Body, body2:Body) -> Vector:
        '''
        Calculates the gravitational force beween 2 Bodies using newton's formula
        '''
        # return 0 force if body1 or body2 is an inactive Body or if the bodies are really close together
        # beyond the threshold
        if body1.status in ["M", "V"] or body2.status in ["M", "V"] or \
        (body1.pos - body2.pos).magnitude <= (body1.dia + body2.dia) / 2 + GRAV_THRESHOLD: 
            return Vector(0, 0)

        # calculates distance vector between the 2 Body to calculate accel
        dist = body2.pos - body1.pos

        return Vector(GRAV_CONST * body1.mass * body2.mass / dist.magnitude**2, dist.angle, input_angle=True)

    def step(self, delta_time:float):
        '''
        changes the position of each object by calculating the accel
        caused by every other object, summing the accels, and then
        calculating velocity and changing position.

        also checks for and manages collisions after that, and then removes Bodies
        that went out of bounds
        '''
        for obj in self.bodies:
            obj.accel = Vector(0, 0)

        # calculate gravitational acceleration between each pair of Bodies
        for i in range(len(self.bodies) - 1):
            for j in range(i + 1, len(self.bodies)):
                force = self.calc_grav_force(self.bodies[i], self.bodies[j])
                self.bodies[i].accel += force / self.bodies[i].mass
                self.bodies[j].accel += -force / self.bodies[j].mass

        # once the accels for all Objs are calculated, move them all
        # this is separated from the main loop because moving the objects
        # as calculating the motions of the other objects would change the calculations
        for obj in self.bodies:
            obj.change_velocity(delta_time)
            obj.move(delta_time)
        
        # check for collisions even after some are resolved bc of overlap and stuff
        checking_for_collisions = True
        while checking_for_collisions:
            # assuming there are no collisions until one is found
            checking_for_collisions = False

            for i in range(len(self.bodies) - 1):
                for j in range(i + 1, len(self.bodies)):
                    if self.check_collision(self.bodies[i], self.bodies[j]):
                        checking_for_collisions = True
                        self.resolve_collisions(self.bodies[i], self.bodies[j], delta_time)
        
        self.remove_far_bodies()

    def display(self, screen:pg.surface.Surface, background:pg.surface.Surface, window:"Window", disp_vects:bool): # type: ignore
        '''
        displays everything in the pygame window, including the motion
        of the Objs
        '''
        # scales the background based on zoom, and then blits a bunch of them accross the world onto the window
        scaled_bg = pg.transform.scale(background, [window.zoom_amt * val for val in background.get_size()])
        for x in range(int(MIN_POS_X), int(MAX_POS_X), background.get_width()):
            for y in range(int(MIN_POS_Y), int(MAX_POS_Y), background.get_height()):
                # draws background every frame to reset screen
                screen.blit(scaled_bg, window.world_to_window(Vector(x, y)).components())

        # draws each Body in world.bodies
        for obj in self.bodies:
            obj.draw(screen, window, disp_vects)

        pg.display.flip() # display everything on the screen
