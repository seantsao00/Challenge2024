"""
This module defines constants associated with entities.
"""

ENTITY_IMAGE_PATH = "entity/"

ENTITY_STATES = {
    "default": ["default"],
    "team0": ["default", "melee", "ranger", "sniper"],
    "team1": ["default", "melee", "ranger", "sniper"],
    "team2": ["melee", "ranger", "sniper"],
    "tower": ["default", "temporary_blue_nexus", "team0", "team1"]
}

ENTITY_RADIUS: float = 6.25
