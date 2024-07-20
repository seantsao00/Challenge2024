"""
This module defines constants associated with vehicle.
"""
import math
from enum import Enum, auto


class VehicleType(Enum):
    BLACK = auto()
    WHITE = auto()
    GRAY = auto()
    RED = auto()
    GREEN = auto()  # 06512E
    BLUE = auto()  # 0378AE #067BBE
    YELLOW = auto()  # CECE22
    OLIVE = auto()  # A2B861
    DARK_CYAN = auto()  # 0C575B
    ORANGE = auto()  # D26701
    PURPLE = auto()  # 8D1D8C
    GLITCH = auto()
    SCOOTER = auto()


VEHICLE_RARITY = {
    VehicleType.BLACK: 20,
    VehicleType.WHITE: 20,
    VehicleType.GRAY: 20,
    VehicleType.RED: 3,
    VehicleType.GREEN: 3,
    VehicleType.BLUE: 3,
    VehicleType.YELLOW: 3,
    VehicleType.OLIVE: 1,
    VehicleType.DARK_CYAN: 1,
    VehicleType.ORANGE: 1,
    VehicleType.PURPLE: 1,
    VehicleType.GLITCH: 0.01,
    VehicleType.SCOOTER: 3
}

VEHICLE_COLOR = {
    VehicleType.BLACK: (0x00, 0x00, 0x00, 0xFF),
    VehicleType.WHITE: (0xFF, 0xFF, 0xFF, 0xFF),
    VehicleType.GRAY: (0xC0, 0xC0, 0xC0, 0xFF),
    VehicleType.RED: (0xEB, 0x33, 0x24, 0xFF),
    VehicleType.GREEN: (0x06, 0x51, 0x2E, 0xFF),
    VehicleType.BLUE: (0x03, 0x78, 0xAE, 0xFF),
    VehicleType.YELLOW: (0xCE, 0xCE, 0x22, 0xFF),
    VehicleType.OLIVE: (0xA2, 0xB8, 0x61, 0xFF),
    VehicleType.DARK_CYAN: (0x0C, 0x57, 0x5B, 0xFF),
    VehicleType.ORANGE: (0xD2, 0x67, 0x01, 0xFF),
    VehicleType.PURPLE: (0x8D, 0x1D, 0x8C, 0xFF),
    VehicleType.GLITCH: (0xFF, 0xFF, 0xFF, 0x66),
    VehicleType.SCOOTER: (0xFF, 0xFF, 0xFF)
}


class VehicleState(Enum):
    FRONT = auto()
    BACK = auto()
    LEFT = auto()
    RIGHT = auto()
    SCOOTER_LEFT = auto()
    SCOOTER_RIGHT = auto()


VEHICLE_SPEED = 50
VEHICLE_WIDTH = 8
VEHICLE_DAMAGE = math.inf
