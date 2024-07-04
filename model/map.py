import csv
import json
import os
import random
import heapq

import pygame as pg

import const
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

    def find_path(self, position_begin: pg.Vector2, position_end: pg.Vector2) -> list[pg.Vector2] | None:
        """
        Find a path from position_begin to position_end. Positions take values
        in range [0, const.ARENA_SIZE).
        Returns a list of positions describing the path, or None if the algorithm
        did not find a path.
        """
        max_x, max_y = self.size
        cell_begin = self.convert_coordinate(position_begin)
        cell_end = self.convert_coordinate(position_end)

        dist: list[list[float]]                 = [[8]     * max_y for _ in range(max_x)]
        src: list[list[None | tuple[int, int]]] = [[None]  * max_y for _ in range(max_x)]
        visited: list[list[bool]]               = [[False] * max_y for _ in range(max_x)]

        # priority queue for A star containing (heuristic, distance, (x, y))
        pq: list[tuple[float, float, tuple[int, int]]] = []

        # helper functions
        def heuristic(cell: tuple[int, int]) -> float:
            return (cell[0] - cell_end[0]) ** 2 + (cell[1] - cell_end[1]) ** 2
        def push_cell(cell: tuple[int, int], new_dist: float, cell_source: tuple[int, int]) -> None:
            cx, cy = cell
            if visited[cx][cy]:
                return
            if src[cx][cy] is not None and dist[cx][cy] <= new_dist:
                return
            dist[cx][cy] = new_dist
            src[cx][cy] = cell_source
            new_heur = heuristic(cell)
            heapq.heappush(pq, (new_heur, new_dist, cell))
        def get_neighbors(cur_cell: tuple[int, int], cur_dist):
            diff = [
                (-1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0), (1, 0, 1.0),
                (-1, -1, 1.4142135623730951), (-1, 1, 1.4142135623730951),
                (1, -1, 1.4142135623730951), (1, 1, 1.4142135623730951),
            ]
            for dx, dy, dd in diff:
                nx, ny, nd = cur_cell[0] + dx, cur_cell[1] + dy, cur_dist + dd
                if (0 <= nx < max_x and 0 <= ny < max_y
                    and self.map[nx][ny] != const.MAP_OBSTACLE):
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
            path.append(self.convert_cell(cur_cell))
            cur_cell = src[cur_cell[0]][cur_cell[1]]
        return path[::-1]


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
