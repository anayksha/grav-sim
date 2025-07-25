from vector import Vector
from settings import SETTINGS

SCREEN_SIZE = SETTINGS["window"]["SCREEN_SIZE"]

MIN_ZOOM = SETTINGS["window"]["MIN_ZOOM"]
MAX_ZOOM = SETTINGS["window"]["MAX_ZOOM"]

SIM_WIDTH = SETTINGS["misc"]["SIM_WIDTH"]
SIM_HEIGHT = SETTINGS["misc"]["SIM_HEIGHT"]
MIN_POS_X = -SIM_WIDTH / 2
MAX_POS_X = MIN_POS_X + SIM_WIDTH
MIN_POS_Y = -SIM_HEIGHT / 2
MAX_POS_Y = MIN_POS_Y + SIM_HEIGHT

class Window:
    '''
    used to facilitate coordinate conversion between window coordinates
    and world coordinates
    '''
    def __init__(self):
        self.size = Vector(*SCREEN_SIZE)
        self._zoom = 1
        self._pan = Vector(0, 0)

    @property
    def zoom_amt(self):
        return self._zoom

    @property
    def pan_amt(self):
        return self._pan

    def pan(self, disp:Vector):
        # using the vertical axis is positive bc lowk prob still works out
        # bounds of window if panned
        self._pan += disp

        left_bound, bottom_bound = (-self.size/self.zoom_amt/2 + self.pan_amt).components()
        right_bound, top_bound = (self.size/self.zoom_amt/2 + self.pan_amt).components()

        # pan if zoom results in showing things out of sim bounds
        # using top of vertical axis as positive bc like i dont think it'll affect anything
        if left_bound < MIN_POS_X:
            self._pan += Vector(MIN_POS_X - left_bound, 0)
        if bottom_bound < MIN_POS_Y:
            self._pan += Vector(0, MIN_POS_Y - bottom_bound)
        if right_bound > MAX_POS_X:
            self._pan += Vector(MAX_POS_X - right_bound, 0)
        if top_bound > MAX_POS_Y:
            self._pan += Vector(0, MAX_POS_Y - top_bound)

    def zoom(self, amt:float, world:"World"): # type: ignore
        # calculate bounds and clamp zoom
        self._zoom = max(MIN_ZOOM, min(MAX_ZOOM, self._zoom + amt))

        for body in world.bodies:
            body.update_surf(self.zoom_amt)

        # panning by zero still runs the clamping thing and correctly pans the
        # view to make sure the zoom didn't show anything out of simulation bounds
        self.pan(Vector(0, 0))

    def window_to_world(self, coords:Vector) -> Vector:
        return (coords - self.size/2) / self._zoom + self.pan_amt

    def world_to_window(self, coords:Vector) -> Vector:
        return (coords - self.pan_amt) * self._zoom + self.size/2
