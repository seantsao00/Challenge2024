from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
import const.team
from event_manager import EventCharacterMove
from model.timer import Timer

if TYPE_CHECKING:
    from model.entity import Entity, LivingEntity


class TeamVisionGrid:
    def __init__(self):
        self.n = int(const.ARENA_SIZE[0] / const.VISION_BLOCK_SIZE)
        self.m = int(const.ARENA_SIZE[1] / const.VISION_BLOCK_SIZE)
        self.mask: pg.Surface = pg.Surface((self.n, self.m), pg.SRCALPHA)
        self.mask.fill([0, 0, 0])
        self.mask.set_alpha(192)
        self.bool_mask: list[list[bool]] = [[False for _ in range(self.m)] for _ in range(self.n)]
        self.vision_not_open: list[list[int]] = [[0 for _ in range(int(self.m // const.TEAM_VISION_BLOCK) + 1)]
                                                 for _ in range(int(self.n // const.TEAM_VISION_BLOCK) + 1)]
        self.visit = [[False for _ in range(self.m)] for _ in range(self.n)]
        for x in range(self.n):
            for y in range(self.m):
                self.vision_not_open[x // const.TEAM_VISION_BLOCK][y //
                                                                   const.TEAM_VISION_BLOCK] += 1

    def transfer_to_pixel(self, position: pg.Vector2):
        return pg.Vector2(int(position.x / const.VISION_BLOCK_SIZE), int(position.y / const.VISION_BLOCK_SIZE))

    def transfer_to_heuristic(self, position: pg.Vector2):
        return pg.Vector2(int(position.x / const.VISION_BLOCK_SIZE / const.TEAM_VISION_BLOCK),
                          int(position.y / const.VISION_BLOCK_SIZE / const.TEAM_VISION_BLOCK))

    def position_inside_vision(self, position: pg.Vector2) -> bool:
        pixel = self.transfer_to_pixel(position)
        if 0 <= pixel.x < self.n and 0 <= pixel.y < self.m:
            return self.bool_mask[int(pixel.x)][int(pixel.y)]
        return False

    def entity_inside_vision(self, entity: Entity):
        return self.position_inside_vision(entity.position)

    def get_mask(self):
        return self.mask

    def heuristic_test(self, position: pg.Vector2):
        bx, by = self.transfer_to_heuristic(position)
        bx, by = int(bx), int(by)
        for x in range(max(0, bx - 1), min(len(self.vision_not_open), bx + 2)):
            for y in range(max(0, by - 1), min(len(self.vision_not_open[0]), by + 2)):
                if self.vision_not_open[x][y] > 0:
                    return True
                if self.vision_not_open[x][y] < 0:
                    raise NotImplementedError
        return False

    def brute_modify(self, position: pg.Vector2, real_radius: float):
        real_position = pg.Vector2(position.x * const.VISION_BLOCK_SIZE,
                                   position.y * const.VISION_BLOCK_SIZE)
        real_position = pg.Vector2(position.x * const.VISION_BLOCK_SIZE,
                                   position.y * const.VISION_BLOCK_SIZE)
        radius = real_radius / const.VISION_BLOCK_SIZE
        for x in range(max(0, int(position.x - radius)),
                       min(self.n, int(position.x + radius + 1))):
            for y in range(max(0, int(position.y - radius)),
                           min(self.m, int(position.y + radius + 1))):
                if real_position.distance_to(pg.Vector2(const.VISION_BLOCK_SIZE * (x + 0.5), const.VISION_BLOCK_SIZE * (y + 0.5))) <= real_radius:
                    a = self.mask.get_at((x, y))
                    if a[3] != 0:
                        a[3] = 0
                        self.vision_not_open[x
                                             // const.TEAM_VISION_BLOCK][y // const.TEAM_VISION_BLOCK] -= 1
                        self.bool_mask[x][y] = True
                        self.mask.set_at((x, y), a)

    def special_modify(self, points: set[tuple[int, int, int]]):
        if len(points) == 0:
            return

        def count_radius(vision: float, distance: float):
            if distance > vision:
                return -1
            return (vision ** 2 - distance ** 2) ** 0.5

        res = [[0 for _ in range(self.m + 1)] for _ in range(self.n + 1)]
        small_vision = [i for i in points if i[2] == const.RANGER_ATTRIBUTE.vision]
        big_vision = [i for i in points if i[2] == const.MELEE_ATTRIBUTE.vision]
        small_vision.sort()
        big_vision.sort()
        i = 0
        j = 0
        for x in range(self.n):
            for y in range(self.m):
                up_radius = -1
                if len(small_vision) > 0:
                    while i < len(small_vision) and small_vision[i] < (x, y, 0):
                        i = i + 1
                    if i > 0 and small_vision[i - 1][0] == x:
                        up_radius = max(up_radius, count_radius(
                            small_vision[i - 1][2] / const.VISION_BLOCK_SIZE, y - small_vision[i - 1][1]))
                        up_radius = max(up_radius, count_radius(
                            small_vision[i - 1][2] / const.VISION_BLOCK_SIZE, y - small_vision[i - 1][1]))
                    if i < len(small_vision) and small_vision[i][0] == x:
                        up_radius = max(up_radius, count_radius(
                            small_vision[i][2] / const.VISION_BLOCK_SIZE, small_vision[i][1] - y))
                        up_radius = max(up_radius, count_radius(
                            small_vision[i][2] / const.VISION_BLOCK_SIZE, small_vision[i][1] - y))
                if len(big_vision) > 0:
                    while j < len(big_vision) and big_vision[j] < (x, y, 0):
                        j = j + 1
                    if j > 0 and big_vision[j - 1][0] == x:
                        up_radius = max(up_radius, count_radius(
                            big_vision[j - 1][2] / const.VISION_BLOCK_SIZE, y - big_vision[j - 1][1]))
                        up_radius = max(up_radius, count_radius(
                            big_vision[j - 1][2] / const.VISION_BLOCK_SIZE, y - big_vision[j - 1][1]))
                    if j < len(big_vision) and big_vision[j][0] == x:
                        up_radius = max(up_radius, count_radius(
                            big_vision[j][2] / const.VISION_BLOCK_SIZE, big_vision[j][1] - y))
                        up_radius = max(up_radius, count_radius(
                            big_vision[j][2] / const.VISION_BLOCK_SIZE, big_vision[j][1] - y))
                if up_radius > -0.5:
                    res[max(0, int(x - up_radius))][y] += 1
                    res[min(self.n, int(x + up_radius + 1))][y] -= 1

        for x in range(1, self.n):
            for y in range(1, self.m):
                res[x][y] += res[x - 1][y]
                if res[x][y] > 0 and self.bool_mask[x][y] is False:
                    a = self.mask.get_at((x, y))
                    a[3] = 0
                    self.vision_not_open[x // const.TEAM_VISION_BLOCK][y //
                                                                       const.TEAM_VISION_BLOCK] -= 1
                    self.vision_not_open[x // const.TEAM_VISION_BLOCK][y //
                                                                       const.TEAM_VISION_BLOCK] -= 1
                    self.bool_mask[x][y] = True
                    self.mask.set_at((x, y), a)

    def update_vision(self, entity: LivingEntity):
        x, y = int(entity.position.x /
                   const.VISION_BLOCK_SIZE), int(entity.position.y / const.VISION_BLOCK_SIZE)
        x, y = int(entity.position.x /
                   const.VISION_BLOCK_SIZE), int(entity.position.y / const.VISION_BLOCK_SIZE)
        if entity.alive is False or self.visit[x][y] is True or self.heuristic_test(entity.position) is False:
            return
        self.brute_modify(pg.Vector2(x, y), entity.attribute.vision)


class TeamVision(TeamVisionGrid):
    def __init__(self, team):
        super().__init__()
        self.team = team
        self.set: set[tuple[int, int, int]] = set()
        self.timer = Timer(0.05, self.modify_vision, once=False)

    def handle_character_move(self, event: EventCharacterMove):
        x, y = int(event.character.position.x
                   / const.VISION_BLOCK_SIZE), int(event.character.position.y / const.VISION_BLOCK_SIZE)
        if (self.visit[x][y] is True
            or event.original_pos.distance_to(event.character.position) < 0.1
            or self.heuristic_test(event.character.position) is False
                or event.character.alive is False):
            return
        self.set.add((x, y, event.character.attribute.vision))
        self.visit[x][y] = True
        # self.modify_vision()

    def modify_vision(self):
        if len(self.set) == 0:
            return
        if len(self.set) >= 35:
            self.special_modify(self.set)
        else:
            for st in self.set:
                self.brute_modify(pg.Vector2(st[0], st[1]), st[2])
        self.set.clear()
