from vector import Vector
from settings import SETTINGS

SCREEN_SIZE = SETTINGS["window"]["SCREEN_SIZE"]
MIN_ZOOM = SETTINGS["window"]["MIN_ZOOM"]
MAX_ZOOM = SETTINGS["window"]["MAX_ZOOM"]

SIM_WIDTH = SETTINGS["physics"]["SIM_WIDTH"]
SIM_HEIGHT = SETTINGS["physics"]["SIM_HEIGHT"]
MIN_POS_X = -SIM_WIDTH / 2
MAX_POS_X = MIN_POS_X + SIM_WIDTH
MIN_POS_Y = -SIM_HEIGHT / 2
MAX_POS_Y = MIN_POS_Y + SIM_HEIGHT

class Window:
    '''
    used for zoom and panning control and to facilitate coordinate conversion
    between pygame window coordinates and world coordinates
    '''
    def __init__(self):
        self.size = Vector(*SCREEN_SIZE) # size of pygame window as a Vector
        self._zoom = 1
        self._pan = Vector(0, 0)

    @property
    def zoom_amt(self):
        return self._zoom

    @property
    def pan_amt(self):
        return self._pan

    def pan(self, disp:Vector):
        '''
        changes pan amount by a certain vector
        
        clamps when it reaches the world bounds if necessary
        '''
        self._pan += disp

        # bounds of window in the world if panned
        # using the vertical axis is positive bc lowk still works out
        left_bound, bottom_bound = (-self.size/self.zoom_amt/2 + self.pan_amt).components()
        right_bound, top_bound = (self.size/self.zoom_amt/2 + self.pan_amt).components()

        # pan to in bounds if the current window displays stuff out of simulation bounds
        if left_bound < MIN_POS_X:
            self._pan += Vector(MIN_POS_X - left_bound, 0)
        if bottom_bound < MIN_POS_Y:
            self._pan += Vector(0, MIN_POS_Y - bottom_bound)
        if right_bound > MAX_POS_X:
            self._pan += Vector(MAX_POS_X - right_bound, 0)
        if top_bound > MAX_POS_Y:
            self._pan += Vector(0, MAX_POS_Y - top_bound)

    def zoom(self, amt:float, world:"World"): # type: ignore
        '''
        adjusts zoom value
        '''
        # clamp zoom
        self._zoom = max(MIN_ZOOM, min(MAX_ZOOM, self._zoom + amt))

        # change size of surfaces of bodies in world depending on zoom
        for body in world.bodies:
            body.update_surf(self.zoom_amt)

        # panning by zero still runs the clamping thing and correctly pans the
        # view to make sure the zoom didn't show anything out of simulation bounds
        self.pan(Vector(0, 0))

    def window_to_world(self, coords:Vector) -> Vector:
        '''returns coordinates in the simulation world given coordinates in the pygame window'''
        return (coords - self.size/2) / self._zoom + self.pan_amt

    def world_to_window(self, coords:Vector) -> Vector:
        '''returns coordinates in the simulation world given coordinates in the pygame window'''
        return (coords - self.pan_amt) * self._zoom + self.size/2
