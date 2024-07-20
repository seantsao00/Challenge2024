import csv
import json
import os
import random
from dataclasses import dataclass
from typing import Any

import pygame as pg

import const
import util
from model.map.station import SpecialMapStation


@dataclass
class Map:
    name: str
    size: tuple[int, int]
    map_list: list[list[int]]
    backgrounds: list[str]
    objects: dict[str, int]
    fountains: list[tuple[int, int]]
    neutral_towers: list[tuple[tuple[int, int], const.TowerType]]
    map_dir: str
    special_handler: Any | None

    def __post_init__(self):
        self.__rng = random.Random()
        """Random number generator. This is used to patch potential RNG manipulation."""

    def position_to_cell(self, position: pg.Vector2) -> tuple[int, int]:
        """
        Return the coordinate based on self.size of position.
        position is a coordinate based on const.ARENA_SIZE.
        """
        x = util.clamp(int(position[0] * self.size[0] / const.ARENA_SIZE[0]), 0, self.size[0] - 1)
        y = util.clamp(
            int(position[1] * self.size[1] / const.ARENA_SIZE[1]), 0, self.size[1] - 1
        )
        return x, y

    def cell_to_position(self, cell: tuple[int, int]) -> pg.Vector2:
        """
        Given an entity at a certain position in the map, return which cell it's in
        """
        x = util.clamp(
            cell[0] * const.ARENA_SIZE[0] / self.size[0], 0, const.ARENA_SIZE[0] - 1
        )
        y = util.clamp(
            cell[1] * const.ARENA_SIZE[1] / self.size[1], 0, const.ARENA_SIZE[1] - 1
        )
        return pg.Vector2(x + 0.5, y + 0.5)

    def get_cell_type(self, cell: tuple[int, int]) -> int:
        """
        Get the type of terrain at a certain cell on the map
        Cell takes in *integer* coordinates in range [0, Map.size)
        Types of terrain are defined in const/map.py
        """
        x, y = cell
        return self.map_list[x][y]

    def get_position_type(self, position: pg.Vector2) -> int:
        """
        Get the type of terrain at a certain position on the map
        Position takes in *real-valued* coordinates in range [0, const.ARENA_SIZE)
        Types of terrain are defined in const/map.py
        """
        return self.get_cell_type(self.position_to_cell(position))

    def is_cell_passable(self, cell: tuple[int, int]) -> bool:
        """
        Checks if a cell is open for characters to pass through
        Cell takes in *integer* coordinates in range [0, Map.size)
        """
        return (0 <= cell[0] < self.size[0] and 0 <= cell[1] < self.size[1]
                and self.get_cell_type(cell) != const.MAP_OBSTACLE)

    def is_position_passable(self, position: pg.Vector2) -> bool:
        """
        Checks if a cell is open for characters to pass through
        Position takes in *real-valued* coordinates in range [0, const.ARENA_SIZE)
        """
        return self.is_cell_passable(self.position_to_cell(position))

    def is_cell_puddle(self, cell: tuple[int, int]) -> bool:
        """
        Checks if a cell is a puddle and will cause the character to slow down
        Cell takes in *integer* coordinates in range [0, Map.size)
        """
        return (0 <= cell[0] < self.size[0] and 0 <= cell[1] < self.size[1]
                and self.get_cell_type(cell) == const.MAP_PUDDLE)

    def is_position_puddle(self, position: pg.Vector2) -> bool:
        """
        Checks if a cell is a puddle and will cause the character to slow down
        Position takes in *real-valued* coordinates in range [0, const.ARENA_SIZE)
        """
        return self.is_cell_puddle(self.position_to_cell(position))

    def get_random_pos(self, r: int) -> pg.Vector2:
        """
        Return a random position in map that is not of type "obstacle"
        """
        ret = pg.Vector2(
            self.__rng.randint(r, const.ARENA_SIZE[0] - r),
            self.__rng.randint(r, const.ARENA_SIZE[1] - r),
        )
        while not self.is_position_passable(ret):
            ret = pg.Vector2(
                self.__rng.randint(r, const.ARENA_SIZE[0] - r),
                self.__rng.randint(r, const.ARENA_SIZE[1] - r),
            )
        return ret


def load_map(map_dir):
    json_file = os.path.join(map_dir, 'topography.json')
    map_file = os.path.join(map_dir, 'topography.csv')

    json_file = os.path.abspath(json_file)
    map_file = os.path.abspath(map_file)
    with open(json_file, encoding='utf-8') as f:
        data = json.load(f)
    backgrounds = data['images']['backgrounds']
    objects = data['images']['objects']

    name = os.path.basename(os.path.dirname(json_file))
    size = (data['width'], data['height'])

    fountains = [tuple(i) for i in data['fountains']]
    neutral_towers: list[tuple[tuple[int, int], const.TowerType]] = []
    for i in data['neutral_towers']:
        if i[-1] == "ferris_wheel":
            tower_type = const.TowerType.FERRIS_WHEEL
        elif i[-1] == "hotel":
            tower_type = const.TowerType.HOTEL
        elif i[-1] == "pylon":
            tower_type = const.TowerType.PYLON
        else:
            raise TypeError(f"neutral tower type '{i[-1]}' is unknown")
        neutral_towers.append((tuple(i[:2]), tower_type))

    with open(map_file, encoding='utf-8') as f:
        rows = list(csv.reader(f))
        map_list = [[0] * size[1] for _ in range(0, size[0])]
        for y, row in enumerate(rows):
            for x, _ in enumerate(row):
                map_list[x][y] = int(row[x])

    special_handler = None
    if name == 'station':
        special_handler = SpecialMapStation()

    return Map(
        name, size, map_list, backgrounds, objects, fountains, neutral_towers, map_dir, special_handler
    )
