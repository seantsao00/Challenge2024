import os 
import csv
import json
from queue import Queue
import random

import pygame as pg

import const 
import util

class Map:
    def __init__(
        self,
        name: str,
        size: tuple[int, int],
        map_list: list[list[int]],
        portals: list[tuple[int, int, int]],
        images: dict[str, int],
        spawn: list[tuple[int]],
        solider_spawn_point,
        map_dir,
        portkey_map,
    ):
        self.name = name
        self.size = size
        self.map = map_list
        self.images = images
        self.portals = portals
        self.spawn = spawn
        self.solider_spawn_point = solider_spawn_point
        self.map_dir = map_dir
        self.connected_component = dict()
        self.closest_cell = dict()
        self.number_of_connected_components = dict()
        self.portkey_map = portkey_map

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

def load_map(map_dir):
    json_file = os.path.join(map_dir, "map.json")
    map_file = os.path.join(map_dir, "map.csv")

    with open(json_file) as f:
        data = json.load(f)
    images = data["images"]

    name = os.path.basename(os.path.dirname(json_file))
    size = (data["width"], data["height"])
    spawn = [tuple(i) for i in data["spawn"]]
    portals = []
    ghost_spawn = tuple(data["tower_spawn"])
    portkey_cells = [[] for i in range(len(data["portals"]))]

    with open(map_file) as f:
        rows = csv.reader(f)

        map_list = [[0] * size[1] for _ in range(0, size[0])]
        portkey_map = [[-1] * size[1] for _ in range(0, size[0])]

        y = 0
        for row in rows:
            for x in range(0, size[0]):
                map_list[x][y] = int(row[x])
                if map_list[x][y] >= const.MAP_PORTKEY_MIN:
                    portkey_map[x][y] = int(row[x]) - const.MAP_PORTKEY_MIN
                    portkey_cells[portkey_map[x][y]].append((x, y))
            y += 1

    for i in range(len(data["portals"])):
        sx = 0
        sy = 0
        for x, y in portkey_cells[i]:
            sx += x
            sy += y
        sx /= len(data["portals"])
        sy /= len(data["portals"])
        ax = -1
        ay = -1

        def dis(a, b):
            dx = a[0] - b[0]
            dy = a[1] - b[1]
            return dx * dx + dy * dy

        for x, y in portkey_cells[i]:
            if ax == -1 or dis((ax, ay), (sx, sy)) > dis((x, y), (sx, sy)):
                ax, ay = x, y
        portals.append(((ax, ay), (data["portals"][i][0], data["portals"][i][1])))

    return Map(
        name, size, map_list, portals, images, spawn, ghost_spawn, map_dir, portkey_map
    )