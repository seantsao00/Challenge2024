from __future__ import annotations

import heapq
from typing import TYPE_CHECKING

import pygame as pg

import const

if TYPE_CHECKING:
    from model.map import Map


class PathFinder:
    """
    A path finder for a map that implements A star algorithm.
    This finder is NOT thread safe for optimization purposes. Different threads
    should be using different instances of path finder.
    """
    INFINITY: int = 10 ** 10

    def __init__(self, game_map: Map):
        max_x, max_y = game_map.size

        self.__map = game_map
        self.__is_obstacle = [[game_map.get_cell_type(
            (x, y)) == const.MAP_OBSTACLE for y in range(max_y)] for x in range(max_x)]
        self.__is_puddle = [[game_map.get_cell_type(
            (x, y)) == const.MAP_PUDDLE for y in range(max_y)] for x in range(max_x)]
        self.__neighbors = [[list(self.__get_neighbors((x, y)))
                             for y in range(max_y)] for x in range(max_x)]
        # init A star
        self.__astar_run_id = 0
        # initial values of `dist`, `src` do not matter
        # initial values of `in_queue`, `visited` must be smaller than `astar_runid`
        self.__astar_dist: list[list[float]] = [[-1] * max_y for _ in range(max_x)]
        self.__astar_in_queue: list[list[int]] = [[-1] * max_y for _ in range(max_x)]
        self.__astar_src: list[list[tuple[int, int]]] = [
            [(-1, -1) for __ in range(max_y)] for _ in range(max_x)]
        self.__astar_visited: list[list[int]] = [[-1] * max_y for _ in range(max_x)]
        self.__dist_hint = PathFinder.INFINITY

    def __is_cell_passable(self, cell: tuple[int, int]) -> bool:
        """
        unlike Map.is_cell_passable, this functions uses pre-computed results
        """
        return (0 <= cell[0] < self.__map.size[0] and 0 <= cell[1] < self.__map.size[1]
                and not self.__is_obstacle[cell[0]][cell[1]])

    def __heuristic_dist_to_target(self, cell: tuple[int, int], cell_end: tuple[int, int]) -> float:
        dx = abs(cell[0] - cell_end[0])
        dy = abs(cell[1] - cell_end[1])
        return dx + dy - (2 - 2 ** 0.5) * min(dx, dy)
        # this should be slower (due to sqrt) but I didn't see significant difference
        # return (dx ** 2 + dy ** 2) ** 0.5 + dist[cell[0]][cell[1]]

    def __get_neighbors(self, cur_cell: tuple[int, int]):
        diff = (
            (-2, 0, 2.0), (0, -2, 2.0), (0, 2, 2.0), (2, 0, 2.0),
            (-1, -1, 1.4142135623730951), (-1, 1, 1.4142135623730951),
            (1, -1, 1.4142135623730951), (1, 1, 1.4142135623730951),
        )
        speed_ratio = (
            const.PUDDLE_SPEED_RATIO if self.__is_puddle[cur_cell[0]][cur_cell[1]] else 1)
        for dx, dy, dd in diff:
            nx, ny = cur_cell[0] + dx, cur_cell[1] + dy
            if self.__is_cell_passable((nx, ny)):
                nd = dd / speed_ratio
                yield (nx, ny, nd)

    def __find_path(self, position_begin: pg.Vector2, position_end: pg.Vector2) -> list[pg.Vector2] | None:
        """
        Find a path from position_begin to position_end with A star algorithm.
        Positions take values in range [0, const.ARENA_SIZE).
        Returns a list of positions describing the path, or None if the algorithm
        did not find a path.
        """
        if (not self.__map.is_position_passable(position_begin)
                or not self.__map.is_position_passable(position_end)):
            return None

        # swap `begin` and `end` so that `begin` remains the same in batched runs
        # and it becomes a single source shortest path problem
        position_begin, position_end = position_end, position_begin

        cell_begin = self.__map.position_to_cell(position_begin)
        cell_end = self.__map.position_to_cell(position_end)

        if (cell_begin[0] + cell_begin[1]) % 2 != (cell_end[0] + cell_end[1]) % 2:
            for new_end in [
                    (cell_end[0] + 1, cell_end[1]),
                    (cell_end[0] - 1, cell_end[1]),
                    (cell_end[0], cell_end[1] + 1),
                    (cell_end[0], cell_end[1] - 1) ]:
                if self.__is_cell_passable(new_end):
                    cell_end = new_end
                    break

        run_id = self.__astar_run_id
        self.__astar_run_id += 1
        dist = self.__astar_dist
        in_queue = self.__astar_in_queue
        src = self.__astar_src
        visited = self.__astar_visited
        dist_hint = self.__dist_hint

        # priority queue for A star containing (heuristic, distance, (x, y))
        pq: list[tuple[float, float, tuple[int, int]]] = []

        def push_cell(cell: tuple[int, int], new_dist: float, cell_source: tuple[int, int]) -> None:
            cx, cy = cell
            if visited[cx][cy] == run_id:
                return
            if in_queue[cx][cy] == run_id and dist[cx][cy] <= new_dist:
                return
            if visited[cx][cy] >= dist_hint:
                # this cell has been discovered in the same batch before
                # no need to relax it anymore
                new_dist = dist[cx][cy]
                cell_source = src[cx][cy]
            else:
                dist[cx][cy] = new_dist
                src[cx][cy] = cell_source
            in_queue[cx][cy] = run_id
            new_heur = self.__heuristic_dist_to_target(cell, cell_end)
            # A star: look for the vertix with lowest f(n) = g(n) + h(n),
            # g(n): actual distance travelled
            # h(n): heuristic function that estimates distance to target
            heapq.heappush(pq, (new_heur + new_dist, new_dist, cell))

        # find single source shortest path
        push_cell(cell_begin, 0, cell_begin)

        while len(pq) > 0:
            _, cur_dist, cur_cell = heapq.heappop(pq)
            cx, cy = cur_cell
            if visited[cx][cy] == run_id:
                continue
            visited[cx][cy] = run_id
            if cur_cell == cell_end:
                break  # path found
            for nx, ny, dd in self.__neighbors[cur_cell[0]][cur_cell[1]]:
                push_cell((nx, ny), cur_dist + dd, cur_cell)
        if visited[cell_end[0]][cell_end[1]] != run_id:
            return None

        def restore_path():
            path: list[pg.Vector2] = []
            cur_cell = cell_end
            while cur_cell != cell_begin:
                if visited[cur_cell[0]][cur_cell[1]] != run_id:
                    return None
                assert visited[cur_cell[0]][cur_cell[1]] == run_id
                path.append(self.__map.cell_to_position(cur_cell))
                cur_cell = src[cur_cell[0]][cur_cell[1]]
            return path
        # no need to reverse the path since begin and end have already been swapped
        return restore_path()

    def batch_begin(self):
        self.__dist_hint = self.__astar_run_id + 1

    def batch_end(self):
        self.__dist_hint = PathFinder.INFINITY

    def find_path(self, position_begin: pg.Vector2, position_end: pg.Vector2) -> list[pg.Vector2] | None:
        return self.__find_path(position_begin, position_end)

    def find_path_batched(self, position_begin_list: list[pg.Vector2], position_end: pg.Vector2) -> list[list[pg.Vector2] | None]:
        self.batch_begin()
        res = []
        for position_begin in position_begin_list:
            res.append(self.__find_path(position_begin, position_end))
        self.batch_end()
        return res
