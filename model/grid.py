import math

import pygame as pg

from event_manager import EventCreateEntity, EventCharactermove, EventCharacterDied
from instances_manager import get_event_manager, get_model
from model.character import Character
from model.entity import Entity
from model.team import Team

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
        new_character_list = []
        for candidate in self.characters:
            if not candidate is character:
                new_character_list.append(candidate)
        self.characters = new_character_list

    def get_enemy(self, team: Team):
        return [character for character in self.characters if not character.team is team]


class Grid:
    """
    Class for Grid (object) in the game.
    Each Grid has the following property:
     - width: The width of the grid.
     - height: The height of the grid.
     - cells: The height * width cells of the grid.
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.cells = [[Cell((i, j)) for i in range(width)] for j in range(height)]
        get_event_manager().register_listener(EventCreateEntity, self.event_add_entity)
        get_event_manager().register_listener(EventCharactermove, self.update_location)
        get_event_manager().register_listener(EventCharacterDied, self.remove_character)

    def get_cell(self, position: pg.Vector2):
        return self.cells[int(position.y)][int(position.x)]

    def add_to_grid(self, entity: Entity):
        self.get_cell(entity.position).add(entity)

    def delete_from_grid(self, character: Character, position: pg.Vector2):
        self.get_cell(position).remove_character(character)

    def remove_character(self, event: EventCharacterDied):
        self.delete_from_grid(event.character, event.character.position)

    def event_add_entity(self, event: EventCreateEntity):
        self.add_to_grid(event.entity)

    def get_closet_enemy(self, position: pg.Vector2, team: Team, radius: int, size: int = 1) -> list[Character]:
        character_at_radius = [[] for _ in range(radius + 1)]
        for i in range(int(max(position.x - radius, 0)), int(min(position.x + radius, self.height))):
            for j in range(int(max(position.y - radius, 0)), int(min(position.y + radius, self.width))):
                dis = (position - pg.Vector2(i, j)).length()
                if dis <= radius:
                    character_at_radius[math.floor(dis)].extend(self.cells[j][i].get_enemy(team))

        enemies = []
        for character_sublist in character_at_radius:
            enemies.extend(character_sublist)
        return enemies[:size]


    def get_closest_enemy_tower(self, team: Team, radius: int):
        for r in range(0, radius + 1):
            radius_cells = self.iterate_radius_cells(self.position, r)
            for position in radius_cells:
                tower = self.get_cell(position).tower
                if not tower.team is team:
                    return tower
        return None

    def get_closest_neutral_tower(self, team: Team, radius: int):
        for r in range(0, radius + 1):
            radius_cells = self.iterate_radius_cells(self.position, r)
            for position in radius_cells:
                tower = self.get_cell(position).tower
                if tower.team == None:
                    return tower
        return None

    def get_closest_team_tower(self, team: Team, radius: int):
        for r in range(0, radius + 1):
            radius_cells = self.iterate_radius_cells(self.position, r)
            for position in radius_cells:
                tower = self.get_cell(position).tower
                if tower.team is team:
                    return tower
        return None

    def update_location(self, event: EventCharactermove):
        self.delete_from_grid(event.character, event.original_pos)
        self.add_to_grid(event.character)

    def iterate_radius_cells(self, position: pg.Vector2, radius: int) -> list[tuple]:
        all_cells = []
        for y_dis in range(-radius, radius + 1):
            if position.y + y_dis < 0 or position.y + y_dis >= self.height:
                continue
            x_dis = int(math.sqrt(radius * radius - y_dis * y_dis))
            if position.x + x_dis < self.width:
                all_cells.append(pg.Vector2(position.x + x_dis, position.y + y_dis))
            if position.x - x_dis >= 0:
                all_cells.append(pg.Vector2(position.x - x_dis, position.y + y_dis))
        return all_cells
    


        
