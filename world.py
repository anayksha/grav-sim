class World:
    '''
    physics world for storing and simulating a set of bodies
    '''
    # TODO: put this stuff in settings
    WIDTH = None
    HEIGHT = None

    def __init__(self):
        self.bodies = []

    def add_body(self):
        pass

    def resolve_collisions():
        pass

    def remove_far_bodies(self):
        pass

    def step(self, delta_time):
        pass

    def display(self, screen, zoom, camera_pan):
        pass
