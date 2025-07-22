import math

def split_vector(magnitude:float, angle:float) -> tuple:
    '''
    returns a vector as a x and y component when inputted
    its direction and magnitude
    '''
    return (magnitude * math.cos(angle), magnitude * math.sin(angle))