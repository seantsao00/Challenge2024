"""
This module defines constants associated with entities.
"""

from const.window import ARENA_SIZE

ENTITY_IMAGE_PATH = "entity/"

ENTITY_STATES = {
    "default": ["default"],
    "tower": ["default", "temporary_blue_nexus", "team1"]
}

ENTITY_RADIUS: float = 20
