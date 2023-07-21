
from enum import Enum
import math
from typing import SupportsFloat
from typing_extensions import SupportsIndex
from typing import Union

import numpy as np
import marthabot.configurations.robot_config as config
from math import pi



def r2d(r):
    """Convert radians into degrees."""
    return math.degrees(r)


def d2r(d):
    """Convert degrees into radians."""
    return math.radians(d)




# https://gist.github.com/phn/1111712/cfac65be099fc1a62c10594749571e470c529cc4
def normalize_degrees(value, lower = config.MIN_ANGLE, upper = config.MAX_ANGLE):
    
    if lower >= upper:
        raise ValueError("Invalid lower and upper limits: (%s, %s)" %
                             (lower, upper))
    res = (np.array(value)
           .reshape((-1,1))
           .astype(float)
           )

    too_positive = res > upper or res == lower

    res = np.where(too_positive,
             lower + abs(res + upper) % (abs(lower) + abs(upper)),
             upper - abs(res - lower) % (abs(lower) + abs(upper)),)

    res *= 1.0
    return res[0,0] if type(value) == float else res

# https://gist.github.com/phn/1111712/cfac65be099fc1a62c10594749571e470c529cc4
def normalize_rad(value, lower = math.radians(config.MIN_ANGLE), upper = math.radians(config.MAX_ANGLE)):
    return normalize_degrees(value,lower,upper)

def diff_deg(a,b):
    diff = a - b
    return (diff + 180) % 360 - 180

def diff_rad(a,b):
    diff = a - b
    return (diff + pi/2) % pi - pi/2



# https://gist.github.com/phn/1111712/cfac65be099fc1a62c10594749571e470c529cc4
class Angle(float):
    
    def __new__(cls, ) :
        return super().__new__(__x)
    def __init__(self, __x: Union[SupportsFloat, SupportsIndex, str]) -> None:
        pass


    # Create a bunch of 

    binops = ['add', 'sub', 'mul', 'div', 'radd', 'rsub'] # etc
    unops = ['neg', 'abs', 'invert'] # etc

    binop_meth = """
def __%s__(self, other):
    return type(self)(int.__%s__(self, other))
    """
    unop_meth = """
def __%s__(self):
    return type(self)(int.__%s__(self))
    """
    for op in binops:
        exec(binop_meth % (op, op))
    
    for op in unops:
        exec(unop_meth % (op, op))
        
