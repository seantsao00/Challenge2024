"""
This module defines constants associated with entities.
"""

ENTITY_IMAGE_PATH = "entity/"

ENTITY_STATES = {
    "default": ["default"],
    "team1": ["default", "melee", "ranger", "sniper"],
    "team2": ["default", "melee", "ranger", "sniper"],
    "tower": ["default", "temporary_blue_nexus", "team1", "team2"]
}

ENTITY_RADIUS: float = 20
