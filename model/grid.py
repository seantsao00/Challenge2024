from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from event_manager import (EventCharacterDied, EventCharacterMove, EventCreateEntity,
                           EventCreateTower)
from instances_manager import get_event_manager
from model.building import Tower
from model.bullet import Bullet
from model.character import Character

if TYPE_CHECKING:
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
        self.position: pg.Vector2 = position
        self.towers: set[Tower] = set()
        self.characters: set[Character] = set()
        self.tower_occupied: set[Tower] = set()

    def add(self, entity: Entity):
        if isinstance(entity, Character):
            self.characters.add(entity)
        elif isinstance(entity, Tower):
            self.towers.add(entity)
        elif isinstance(entity, Bullet):
            pass
        else:
            raise NotImplementedError

    def remove_character(self, character: Character):
        if character in self.characters:
            self.characters.remove(character)

    def get_enemy(self, team: Team) -> list[Character]:
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
        self.__radius = const.GRID_BLOCK_SIZE
        self.__width = int(width / self.__radius)
        self.__height = int(height / self.__radius)
        self.__cells = [[Cell(pg.Vector2(i, j)) for i in range(height)] for j in range(width)]
        self.__register_listeners()

    def __transfer(self, position: pg.Vector2) -> pg.Vector2:
        return pg.Vector2(position.x / self.__radius, position.y / self.__radius)

    def __get_cell(self, position: pg.Vector2) -> Cell:
        pos = self.__transfer(position)
        return self.__cells[int(pos.x)][int(pos.y)]

    def __add_to_grid(self, entity: Entity):
        self.__get_cell(entity.position).add(entity)
        if isinstance(entity, Tower):
            x1, x2 = ((entity.position.x - entity.attribute.attack_range) / self.__radius,
                      (entity.position.x + entity.attribute.attack_range) / self.__radius)
            y1, y2 = ((entity.position.y - entity.attribute.attack_range) / self.__radius,
                      (entity.position.y + entity.attribute.attack_range) / self.__radius)
            for x in range(max(0, int(x1)), min(self.__height, int(x2) + 1)):
                for y in range(max(0, int(y1)), min(self.__width, int(y2) + 1)):
                    self.__cells[x][y].tower_occupied.add(entity)

    def __handle_character_died(self, event: EventCharacterDied):
        self.delete_from_grid(event.character, event.character.position)

    def __handle_create_entity(self, event: EventCreateEntity):
        self.__add_to_grid(event.entity)

    def __handle_create_tower(self, event: EventCreateTower):
        self.__add_to_grid(event.tower)

    def __iterate_radius_cells(self, position: pg.Vector2, radius: int) -> list[Cell]:
        cell_at_radius = [[] for _ in range(radius + 1)]
        all_cells = []
        for i in range(int(max(position.x - radius, 0)), int(min(position.x + radius, self.__height))):
            for j in range(int(max(position.y - radius, 0)), int(min(position.y + radius, self.__width))):
                dis = (position - pg.Vector2(i, j)).length()
                if dis <= radius:
                    cell_at_radius[int(dis)].append(self.__cells[j][i])
        for cell_sublist in cell_at_radius:
            all_cells.extend(cell_sublist)
        return all_cells

    def __update_location(self, event: EventCharacterMove):
        self.delete_from_grid(event.character, event.original_pos)
        self.__add_to_grid(event.character)

    def __register_listeners(self):
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventCreateEntity, self.__handle_create_entity)
        ev_manager.register_listener(EventCreateTower, self.__handle_create_tower)
        ev_manager.register_listener(EventCharacterMove, self.__update_location)
        ev_manager.register_listener(EventCharacterDied, self.__handle_character_died)

    def delete_from_grid(self, character: Character, position: pg.Vector2):
        self.__get_cell(position).remove_character(character)

    def get_closet_enemy(self, position: pg.Vector2, team: Team, radius: int, size: int = 1) -> list[Character]:
        cells = self.__iterate_radius_cells(position, radius)
        enemies = []
        for cell in cells:
            enemies.extend(cell.get_enemy(team))
            if len(enemies) >= size:
                break
        return enemies[:size]

    def get_closest_enemy_tower(self, position: pg.Vector2, team: Team, radius: int):
        cells = self.__iterate_radius_cells(position, radius)
        for cell in cells:
            if not cell.towers.team is team:
                return cell.towers
        return None

    def get_closest_neutral_tower(self, position: pg.Vector2, radius: int):
        cells = self.__iterate_radius_cells(position, radius)
        for cell in cells:
            if cell.towers.team is None:
                return cell.towers
        return None

    def get_closest_team_tower(self, position: pg.Vector2, team: Team, radius: int):
        cells = self.__iterate_radius_cells(position, radius)
        for cell in cells:
            if cell.towers.team is team:
                return cell.towers
        return None

    def get_attacker_tower(self, position: pg.Vector2) -> set[Tower]:
        return self.__get_cell(position).tower_occupied

    def all_entity_in_range(self, position: pg.Vector2, radius: float) -> list[Character | Tower]:
        x, y = self.__transfer(position)
        result = []
        for dx in range(max(0, int(x - radius / self.__radius)), min(self.__height, int(x + radius / self.__radius + 1))):
            for dy in range(max(0, int(y - radius / self.__radius)), min(self.__width, int(y + radius / self.__radius + 1))):
                cell = self.__cells[dx][dy]
                result.extend(
                    [tower for tower in cell.towers if tower.position.distance_to(position) <= radius])
                result.extend(
                    [character for character in cell.characters if character.position.distance_to(position) <= radius])
        return result
