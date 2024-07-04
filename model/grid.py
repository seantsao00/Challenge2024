import pygame as pg

from event_manager import EventCharacterDied, EventCharacterMove, EventCreateEntity
from instances_manager import get_event_manager
from model import Bullet, Character, Entity, Team, Tower


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
        self.fountain = None
        self.tower = None
        self.bullet = None
        self.characters: set[Character] = set()

    def add(self, entity: Entity):
        if isinstance(entity, Character):
            self.characters.add(entity)
        elif isinstance(entity, Tower):
            self.tower = entity
        elif isinstance(entity, Bullet):
            self.bullet = entity
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
        self.width = width
        self.height = height
        self.cells = [[Cell(pg.Vector2(i, j)) for i in range(width)] for j in range(height)]
        self.register_listeners()

    def get_cell(self, position: pg.Vector2) -> Cell:
        return self.cells[int(position.y)][int(position.x)]

    def add_to_grid(self, entity: Entity):
        self.get_cell(entity.position).add(entity)

    def delete_from_grid(self, character: Character, position: pg.Vector2):
        self.get_cell(position).remove_character(character)

    def handle_character_died(self, event: EventCharacterDied):
        self.delete_from_grid(event.character, event.character.position)

    def handle_create_entity(self, event: EventCreateEntity):
        self.add_to_grid(event.entity)

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
