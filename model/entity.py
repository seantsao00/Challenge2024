"""
The module defines Entity class.
"""

import pygame as pg
from event_manager.events import EventCreateEntity
from instances_manager import get_event_manager

class Entity:
    """
    Class for entity (object) in the game, including NPCs.
    Each entity has the following property:
     - id: unique ID for each entity.
     - position: 
     - type: entity type, used for determine the image type
     - imgstate: used for different image for the same type
     - hidden: the entity will not render if it is True.
    """

    entity_id = 0

    def __init__(self, position):
        Entity.entity_id += 1
        self.id = Entity.entity_id
        self.position = position
        self.type = 'default'
        self.imgstate = 'default'
        self.hidden = False
        get_event_manager().post(EventCreateEntity(self))

