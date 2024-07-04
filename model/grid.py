from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg
import const
from event_manager import EventCharacterDied, EventCharacterMove, EventCreateEntity
from instances_manager import get_event_manager
from model import Character, Tower

if TYPE_CHECKING:
    from model import Entity, Team


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
        self.tower: set[Tower] = set()
        self.characters: set[Character] = set()
        self.tower_occupied: set[Tower] = set()

    def add(self, entity: Entity):
        if isinstance(entity, Character):
            self.characters.add(entity)
        elif isinstance(entity, Tower):
            self.tower_occupied.add(entity)
            if pg.Vector2(int(entity.position.x), int(entity.position.y)) == self.position:
                self.tower.add(entity)
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
        self.radius = const.GRID_BLOCK_SIZE
        self.width = int(width / self.radius)
        self.height = int(height / self.radius)
        self.cells = [[Cell(pg.Vector2(i, j)) for i in range(width)] for j in range(height)]
        self.register_listeners()

    def transfer(self, position: pg.Vector2) -> pg.Vector2:
        return pg.Vector2(position.x / self.radius, position.y / self.radius)

    def get_cell(self, position: pg.Vector2) -> Cell:
        pos = self.transfer(position)
        return self.cells[int(pos.x)][int(pos.y)]

    def add_to_grid(self, entity: Entity):
        self.get_cell(entity.position).add(entity)
        if isinstance(entity, Tower):
            x1, x2 = (entity.position.x - const.TOWER_ATTACK_RANGE) / self.radius, (entity.position.x + const.TOWER_ATTACK_RANGE) / self.radius
            y1, y2 = (entity.position.y - const.TOWER_ATTACK_RANGE) / self.radius, (entity.position.y + const.TOWER_ATTACK_RANGE) / self.radius
            print(entity.type, entity.imgstate, x1, x2, y1, y2)
            for x in range(max(0, int(x1)), min(self.height, int(x2) + 1)):
                for y in range(max(0, int(y1)), min(self.width, int(y2) + 1)):
                    self.cells[x][y].tower_occupied.add(entity)

    def delete_from_grid(self, character: Character, position: pg.Vector2):
        self.get_cell(position).remove_character(character)

    def handle_character_died(self, event: EventCharacterDied):
        self.delete_from_grid(event.character, event.character.position)

    def handle_create_entity(self, event: EventCreateEntity):
        self.add_to_grid(event.entity)

    def get_attacker_tower(self, position: pg.Vector2) -> set[Tower]:
        return self.get_cell(position).tower_occupied

    def all_entity_in_range(self, position: pg.Vector2, radius: float) -> list[Character | Tower]:
        x, y = self.transfer(position)
        result = []
        for dx in range(max(0, int(x)), min(self.height, int(x + radius / self.radius + 1))):
            for dy in range(max(0, int(y)), min(self.width, int(y + radius / self.radius + 1))):
                cell = self.cells[dx][dy]
                result.extend([tower for tower in cell.tower if tower.position.distance_to(position) <= radius])
                result.extend([character for character in cell.characters if character.position.distance_to(position) <= radius])
        return result

    def iterate_radius_cells(self, position: pg.Vector2, radius: int) -> list[Cell]:
        cell_at_radius = [[] for _ in range(radius + 1)]
        all_cells = []
        for i in range(int(max(position.x - radius, 0)), int(min(position.x + radius, self.height))):
            for j in range(int(max(position.y - radius, 0)), int(min(position.y + radius, self.width))):
                dis = (position - pg.Vector2(i, j)).length()
                if dis <= radius:
                    cell_at_radius[int(dis)].append(self.cells[j][i])
        for cell_sublist in cell_at_radius:
            all_cells.extend(cell_sublist)
        return all_cells

    def get_closet_enemy(self, position: pg.Vector2, team: Team, radius: int, size: int = 1) -> list[Character]:
        cells = self.iterate_radius_cells(position, radius)
        enemies = []
        for cell in cells:
            enemies.extend(cell.get_enemy(team))
            if len(enemies) >= size:
                break
        return enemies[:size]

    def get_closest_enemy_tower(self, position: pg.Vector2, team: Team, radius: int):
        cells = self.iterate_radius_cells(position, radius)
        for cell in cells:
            if not cell.tower.team is team:
                return cell.tower
        return None

    def get_closest_neutral_tower(self, position: pg.Vector2, team: Team, radius: int):
        cells = self.iterate_radius_cells(position, radius)
        for cell in cells:
            if cell.tower.team is None:
                return cell.tower
        return None

    def get_closest_team_tower(self, position: pg.Vector2, team: Team, radius: int):
        cells = self.iterate_radius_cells(position, radius)
        for cell in cells:
            if cell.tower.team is team:
                return cell.tower
        return None

    def update_location(self, event: EventCharacterMove):
        self.delete_from_grid(event.character, event.original_pos)
        self.add_to_grid(event.character)

    def register_listeners(self):
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventCreateEntity, self.handle_create_entity)
        ev_manager.register_listener(EventCharacterMove, self.update_location)
        ev_manager.register_listener(EventCharacterDied, self.handle_character_died)
