"""
This module defines constants associated with entities.
"""

from const.window import ARENA_SIZE

ENTITY_IMAGE_PATH = "entity/"

ENTITY_STATES = {
    "default": ["default"],
    "fountain": ["temporary_blue_nexus"]
}

ENTITY_RADIUS: float = ARENA_SIZE[0]/10
