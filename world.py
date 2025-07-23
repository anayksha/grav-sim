from math import sqrt
import pygame as pg

from physics import Vector
from bodies import Body

from settings import SETTINGS

SCREEN_SIZE = SETTINGS["window"]["SCREEN_SIZE"]

GRAV_CONST = SETTINGS["physics"]["GRAV_CONST"]
COLLISION_CONST = SETTINGS["physics"]["COLLISION_CONST"]

class World:
    '''
    physics world for storing and simulating a set of bodies
    '''
    # TODO: put this stuff in settings
    WIDTH = 1600
    HEIGHT = 900
    MIN_POS_X = -(WIDTH - SCREEN_SIZE[0]) / 2
    MAX_POS_X = MIN_POS_X + WIDTH
    MIN_POS_Y = -(HEIGHT - SCREEN_SIZE[1]) / 2
    MAX_POS_Y = MIN_POS_Y + HEIGHT

    def __init__(self):
        self.bodies = []

    def add_body(self, body:Body):
        self.bodies.append(body)

    def check_collision(self, body1:Body, body2:Body):
        return (body2.pos - body1.pos).magnitude <= (body1.dia + body2.dia)/2

    def resolve_collisions(self, body1:Body, body2:Body):
        '''
        so this uses a really complicated and goofy formula to reposition bodies
        that are intersecting eachother
        '''
        vel_ba = body2.velocity - body1.velocity
        pos_ba = body2.pos - body1.pos

        a = vel_ba.dot(vel_ba)
        b = 2 * vel_ba.dot(pos_ba)
        c = pos_ba.dot(pos_ba) - ((body1.dia + body2.dia) / 2)**2

        # quadratic formula aah
        time = (-b - sqrt(b**2 - 4 * a * c)) / (2 * a)

        body1.pos += body1.velocity * time
        body2.pos += body2.velocity * time

    def remove_far_bodies(self):
        to_remove = []

        for i in range(len(self.bodies)):
            body = self.bodies[i]
            if not (World.MIN_POS_X <= body.pos.x <= World.MAX_POS_X) or \
            not (World.MIN_POS_Y <= body.pos.y <= World.MAX_POS_Y):
                to_remove.append(i)

        for i in to_remove:
            del self.bodies[i]

    def calc_grav_force(self, body1:Body, body2:Body) -> Vector:
        '''
        Calculates the acceleration one object faces due to the gravitational force
        between itself and one other object (other_obj) and then returns that
        
        TODO: revise bc this was originaly in Body class
        also might wanna move to somewhere else bc it isnt that fitting to have it here?
        '''
        # if the Body's status isn't operational, or other_obj is new and its status is
        # setting mass or setting velocity, the Body shouldn't accelerate
        if body1.status in ["M", "V"] or body2.status in ["M", "V"]:
            return Vector(0, 0)

        # calculates horizontal, vertical, and actual distance between the 2 Body to calculate accel
        dist = body2.pos - body1.pos

        # only force is contact force if the 2 objects are inside each other
        if dist.magnitude < (body1.dia/2 + body2.dia/2):
            # random aah formula for contact acceleration as a function of distance the objs are inside eachother
            accel_magnitude = -100000 * (body1.dia/2 + body2.dia/2 - dist.magnitude)**2
            return Vector(accel_magnitude, dist.angle, input_angle=True)

        # uses an expression created from gravitation formula and F = ma to determine acceleration
        return Vector(GRAV_CONST * body1.mass * body2.mass / dist.magnitude**2, dist.angle, input_angle=True)

    def step(self, delta_time:float):
        '''
        changes the position of each object by calculating the accel
        caused by every other object, summing the accels, and then
        calculating velocity and changing position
        '''
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
            obj.accel = Vector(0, 0)

    def display(self, screen:pg.surface.Surface, background:pg.surface.Surface, zoom=None, camera_pan=None):
        '''
        displays everything in the pygame window, including the motion
        of the Objs
        '''
        screen.blit(background, (0, 0)) # draws background every frame to reset screen

        # draws each Body in world.bodies
        for obj in self.bodies:
            obj.draw(screen)

        pg.display.flip() # display everything on the screen
