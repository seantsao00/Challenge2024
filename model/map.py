import csv
import json
import os
import random

import pygame as pg

import const
import const.map
import util


class Map:
    def __init__(
        self,
        name: str,
        size: tuple[int, int],
        map_list: list[list[int]],
        images: dict[str, int],
        fountains: list[tuple[int, int]],
        tower_spawns: list[tuple[int, int]],
        map_dir,
    ):
        self.name = name
        self.size = size
        self.map = map_list
        self.images = images
        self.fountains = fountains
        self.tower_spawns = tower_spawns
        self.map_dir = map_dir

    def convert_coordinate(self, position: tuple | pg.Vector2) -> tuple:
        """
        Return the coordinate based on self.size of position.
        position is a coordinate based on const.ARENA_SIZE.
        """
        x = util.clamp(
            int(position[0] * self.size[0] / const.ARENA_SIZE[0]), 0, self.size[0] - 1
        )
        y = util.clamp(
            int(position[1] * self.size[1] / const.ARENA_SIZE[1]), 0, self.size[1] - 1
        )
        return x, y

    def convert_cell(self, position: tuple | pg.Vector2) -> pg.Vector2:
        """
        Given an entity at a certain position in the map, return which cell it's in
        """
        x = util.clamp(
            position[0] * const.ARENA_SIZE[0] / self.size[0], 0, const.ARENA_SIZE[0] - 1
        )
        y = util.clamp(
            position[1] * const.ARENA_SIZE[1] / self.size[1], 0, const.ARENA_SIZE[1] - 1
        )
        return pg.Vector2(x, y)

    def get_type(self, position: tuple | pg.Vector2) -> int:
        """
        Return the type of terrain at a certain position in the map
        value 1 denotes road, 2 denotes puddle, and 3 denotes obstacle
        """
        x, y = self.convert_coordinate(position)
        return self.map[x][y]

    def get_random_pos(self, r: int) -> pg.Vector2:
        """
        Return a random position in map that is not of type "obstacle"
        """
        ret = pg.Vector2(
            random.randint(r, const.ARENA_SIZE[0] - r),
            random.randint(r, const.ARENA_SIZE[1] - r),
        )
        while self.get_type(ret) == const.MAP_OBSTACLE:
            ret = pg.Vector2(
                random.randint(r, const.ARENA_SIZE[0] - r),
                random.randint(r, const.ARENA_SIZE[1] - r),
            )
        return ret


def load_map(map_dir):
    json_file = os.path.join(map_dir, "map.json")
    map_file = os.path.join(map_dir, "map.csv")

    json_file = os.path.abspath(json_file)
    map_file = os.path.abspath(map_file)
    with open(json_file, encoding='utf-8') as f:
        data = json.load(f)
    images = data["images"]

    name = os.path.basename(os.path.dirname(json_file))
    size = (data["width"], data["height"])

    fountains = [tuple(i) for i in data["fountains"]]
    tower_spawns = [tuple(i) for i in data["tower_spawns"]]
    i = 0
    with open(map_file, encoding='utf-8') as f:
        rows = list(csv.reader(f))
        map_list = [[0] * size[1] for _ in range(0, size[0])]
        for y, row in enumerate(rows):
            for x, block in enumerate(row):
                map_list[x][y] = int(row[x])
    return Map(
        name, size, map_list, images, fountains, tower_spawns, map_dir
    )
