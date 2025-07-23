import pygame as pg

from physics import Vector
from bodies import Body

from settings import SETTINGS

SCREEN_SIZE = SETTINGS["window"]["SCREEN_SIZE"]

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

    def resolve_collisions():
        pass

    def remove_far_bodies(self):
        to_remove = []

        for i in range(len(self.bodies)):
            body = self.bodies[i]
            if not (World.MIN_POS_X <= body.pos.x <= World.MAX_POS_X) or \
            not (World.MIN_POS_Y <= body.pos.y <= World.MAX_POS_Y):
                to_remove.append(i)
        
        for i in to_remove:
            del self.bodies[i]

    def step(self, delta_time:float):
        '''
        changes the position of each object by calculating the accel
        caused by every other object, summing the accels, and then
        calculating velocity and changing position
        '''
        # calculate gravitational acceleration between each pair of Bodies
        for i in range(len(self.bodies) - 1):
            for j in range(i + 1, len(self.bodies)):
                force = self.bodies[i].calc_grav_force(self.bodies[j])
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
