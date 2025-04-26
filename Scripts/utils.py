from math import sin, cos, pi
from pygame import Vector2
from typing import Any

from .constants import *

def screen_border_check(position: Vector2, mask_size: tuple):
    mask_size_halved = Vector2(mask_size) / 2
    return [
        position.x - mask_size_halved.x < 0,
        position.x + mask_size_halved.x > GAME_SURFACE_SIZE[0],
        position.y - mask_size_halved.y < 0,
        position.y + mask_size_halved.y > GAME_SURFACE_SIZE[1]
    ]

def angle_to_vector(degrees: float):
    radians = degrees * pi / 180
    return Vector2(cos(radians), -sin(radians))

def lerp(start_value: Any, end_value: Any, progress: float):
    if type(start_value) is Vector2:
        return start_value.lerp(end_value, progress)

    distance = end_value - start_value
    return start_value + distance * progress