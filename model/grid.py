import math

import pygame as pg

from event_manager import EventCreateEntity
from instances_manager import get_event_manager, get_model
from model.building import Tower
from model.character import Character
from model.entity import Entity
from model.timer import Timer


class Cell:
    """
    Class for Cell (object) in the game.
    Each Cell has the following property:
     - position: The position of the grid.
     - tower: The tower on the grid.
     - characters: The characters on the grid. 
    """

    def __init__(self, position: pg.Vector2):
        self.position = position
        self.fountain = None
        self.tower = None
        self.characters = []

    def add(self, entity: Entity):
        if isinstance(entity, Character):
            self.characters.append(entity)
        else:
            self.tower = entity

    def remove_character(self, character: Character):
        self.characters.remove(character)

    def get_characters(self):
        return list(self.characters)


class Grid:
    """
    Class for Grid (object) in the game.
    Each Grid has the following property:
     - width: The width of the grid.
     - height: The height of the grid.
     - cells: The height * width cells of the grid.
     - character_update_timer: The timer to update the location of all characters per 1/4 second.
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.character_update_timer = Timer(250, self.characters_replace)
        self.cells = [[Cell((i, j)) for i in range(width)] for j in range(height)]
        get_event_manager().register_listener(EventCreateEntity, self.event_add_entity)

    def add_to_grid(self, entity: Entity):
        fixed_position_y, fixed_position_x = round(entity.position.y), round(entity.position.x)
        self.cells[fixed_position_y][fixed_position_x].add(entity)

    def event_add_entity(self, event: EventCreateEntity):
        self.add_to_grid(event.entity)

    def add_entity(self, entity: Entity):
        self.add_to_grid(entity)

    def get_nearest_characters(self, position: pg.Vector2, radius: float):
        character_at_radius = [[] for _ in range(radius + 1)]
        for i in range(int(max(position.x - radius, 0)), int(min(position.x + radius, self.height))):
            for j in range(int(max(position.y - radius, 0)), int(min(position.y + radius, self.width))):
                dis = (position - pg.Vector2(i, j)).length()
                if dis <= radius:
                    character_at_radius[math.floor(dis)].extend(self.cells[j][i].characters)

        character_list = []
        for character_sublist in character_at_radius:
            character_list.extend(character_sublist)
        return character_list

    def characters_replace(self):
        characters_list = get_model().characters
        for col in self.cells:
            for cell in col:
                cell.characters = []
        for character in characters_list:
            self.add_entity(character)
