"""
This module defines constants associated with vehicle.
"""
import math
from enum import Enum, auto


class VehicleType(Enum):
    RED = auto()


class VehicleState(Enum):
    FRONT = auto()
    BACK = auto()
    LEFT = auto()
    RIGHT = auto()


VEHICLE_SPEED = 50
VEHICLE_WIDTH = 10
VEHICLE_DAMAGE = math.inf
