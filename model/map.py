import csv
import heapq
import json
import os
import random
from dataclasses import dataclass

import pygame as pg

import const
import util


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
            random.randint(r, const.ARENA_SIZE[0] - r),
            random.randint(r, const.ARENA_SIZE[1] - r),
        )
        while not self.is_position_passable(ret):
            ret = pg.Vector2(
                random.randint(r, const.ARENA_SIZE[0] - r),
                random.randint(r, const.ARENA_SIZE[1] - r),
            )
        return ret

    def find_path(self, position_begin: pg.Vector2, position_end: pg.Vector2) -> list[pg.Vector2] | None:
        """
        Find a path from position_begin to position_end with A star algorithm.
        Positions take values in range [0, const.ARENA_SIZE).
        Returns a list of positions describing the path, or None if the algorithm
        did not find a path.
        """
        if (not self.is_position_passable(position_begin)
                or not self.is_position_passable(position_end)):
            return None

        max_x, max_y = self.size
        cell_begin = self.position_to_cell(position_begin)
        cell_end = self.position_to_cell(position_end)

        dist: list[list[float]] = [[8] * max_y for _ in range(max_x)]
        src: list[list[None | tuple[int, int]]] = [[None] * max_y for _ in range(max_x)]
        visited: list[list[bool]] = [[False] * max_y for _ in range(max_x)]

        # priority queue for A star containing (heuristic, distance, (x, y))
        pq: list[tuple[float, float, tuple[int, int]]] = []

        # helper functions
        def heuristic_dist_to_target(cell: tuple[int, int]) -> float:
            dx = abs(cell[0] - cell_end[0])
            dy = abs(cell[1] - cell_end[1])
            return dx + dy - (2 - 2 ** 0.5) * min(dx, dy)
            # this should be faster but I didn't see significant difference
            # return (dx ** 2 + dy ** 2) ** 0.5 + dist[cell[0]][cell[1]]

        def push_cell(cell: tuple[int, int], new_dist: float, cell_source: tuple[int, int]) -> None:
            cx, cy = cell
            if visited[cx][cy]:
                return
            if src[cx][cy] is not None and dist[cx][cy] <= new_dist:
                return
            dist[cx][cy] = new_dist
            src[cx][cy] = cell_source
            new_heur = heuristic_dist_to_target(cell)
            # A star: look for the vertix with lowest f(n) = g(n) + h(n),
            # g(n): actual distance travelled
            # h(n): heuristic function that estimates distance to target
            heapq.heappush(pq, (new_heur + new_dist, new_dist, cell))

        def get_neighbors(cur_cell: tuple[int, int], cur_dist):
            diff = [
                (-1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0), (1, 0, 1.0),
                (-1, -1, 1.4142135623730951), (-1, 1, 1.4142135623730951),
                (1, -1, 1.4142135623730951), (1, 1, 1.4142135623730951),
            ]
            for dx, dy, dd in diff:
                nx, ny = cur_cell[0] + dx, cur_cell[1] + dy
                nd = cur_dist + dd / (const.PUDDLE_SPEED_RATIO if self.get_cell_type(cur_cell) == const.MAP_PUDDLE else 1)
                if self.is_cell_passable((nx, ny)):
                    yield (nx, ny, nd)

        # find single source shortest path
        push_cell(cell_begin, 0, cell_begin)
        iters = 0
        while len(pq) > 0:
            iters += 1
            _, cur_dist, cur_cell = heapq.heappop(pq)
            cx, cy = cur_cell
            if visited[cx][cy]:
                continue
            visited[cx][cy] = True
            if cur_cell == cell_end:
                break  # path found
            for nx, ny, nd in get_neighbors(cur_cell, cur_dist):
                push_cell((nx, ny), nd, cur_cell)
        if not visited[cell_end[0]][cell_end[1]]:
            return None

        # path found
        path: list[pg.Vector2] = []
        cur_cell = cell_end
        while cur_cell != cell_begin:
            assert cur_cell is not None
            path.append(self.cell_to_position(cur_cell))
            cur_cell = src[cur_cell[0]][cur_cell[1]]
        return path[::-1]


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
    return Map(
        name, size, map_list, backgrounds, objects, fountains, neutral_towers, map_dir
    )
