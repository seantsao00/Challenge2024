from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
import const.team
from event_manager import (EventCharacterDied, EventCreateTower, EventEveryTick, EventHumanInput,
                           EventSelectCharacter, EventSpawnCharacter, EventTeamGainTower,
                           EventTeamLoseTower, EventCharacterMove)
from instances_manager import get_event_manager
from model.building import Tower
from model.character import Character, Ranger
from model.timer import Timer
from util import log_info

if TYPE_CHECKING:
    from model.entity import Entity, LivingEntity

class Team_Vision_Grid:
    def __init__(self):
        self.N = int(const.ARENA_SIZE[0] / const.VISION_BLOCK_SIZE)
        self.M = int(const.ARENA_SIZE[1] / const.VISION_BLOCK_SIZE)
        self.mask: pg.Surface = pg.Surface((self.N, self.M), pg.SRCALPHA)
        self.mask.fill([0, 0, 0])
        self.mask.set_alpha(192)
        self.bool_mask: list[list[bool]] = [[False for _ in range(self.M)] for __ in range(self.N)]
        self.vision_not_open: list[list[int]] = [[0 for _ in range(int(self.M // const.TEAM_VISION_BLOCK) + 1)]
                                                 for __ in range(int(self.N // const.TEAM_VISION_BLOCK) + 1)]
        for x in range(self.N):
            for y in range(self.M):
                self.vision_not_open[x // const.TEAM_VISION_BLOCK][y //
                                                                   const.TEAM_VISION_BLOCK] += 1

    def transfer_to_pixel(self, position: pg.Vector2):
        return pg.Vector2(int(position.x / const.VISION_BLOCK_SIZE), int(position.y / const.VISION_BLOCK_SIZE))

    def transfer_to_heuristic(self, position: pg.Vector2):
        return pg.Vector2(int(position.x / const.VISION_BLOCK_SIZE / const.TEAM_VISION_BLOCK), int(position.y / const.VISION_BLOCK_SIZE / const.TEAM_VISION_BLOCK))

    def position_inside_vision(self, position: pg.Vector2) -> bool:
        pixel = self.transfer_to_pixel(position)
        if 0 <= pixel.x < self.N and 0 <= pixel.y < self.M:
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

    def brute_modify(self, position: pg.Vector2, radius: float):
        real_position = self.transfer_to_pixel(position)
        real_radius = radius / const.VISION_BLOCK_SIZE
        for x in range(max(0, int(real_position.x - real_radius)),
                       min(self.N, int(position.x + real_radius + 1))):
            for y in range(max(0, int(real_position.y - real_radius)),
                           min(self.M, int(position.y + real_radius + 1))):
                if position.distance_to(pg.Vector2(const.VISION_BLOCK_SIZE * (x + 0.5), const.VISION_BLOCK_SIZE * (y + 0.5))) <= radius:
                    a = self.mask.get_at((x, y))
                    if a[3] != 0:
                        a[3] = 0
                        self.vision_not_open[x
                                             // const.TEAM_VISION_BLOCK][y // const.TEAM_VISION_BLOCK] -= 1
                        self.bool_mask[x][y] = True
                        self.mask.set_at((x, y), a)

    def special_modify(self, set: set[tuple[int, int, int]]):
        if len(set) == 0:
            return
        def count_radius(vision: float, distance: float):
            if distance > vision:
                return -1
            return (vision ** 2 - distance ** 2) ** 0.5
        
        res = [[0 for _ in range(self.M + 1)] for __ in range(self.N + 1)]
        small_vision = [i for i in set if i[2] == const.RANGER_ATTRIBUTE.vision]
        big_vision = [i for i in set if i[2] == const.MELEE_ATTRIBUTE.vision]
        small_vision.sort()
        big_vision.sort()
        i = 0
        j = 0
        for x in range(self.N):
            for y in range(self.M):
                up_radius = -1
                if len(small_vision) > 0:
                    while i < len(small_vision) and small_vision[i] < (x, y, 0):
                        i = i + 1
                    if i > 0 and small_vision[i - 1][0] == x:
                        up_radius = max(up_radius, count_radius(small_vision[i - 1][2] / const.VISION_BLOCK_SIZE, y - small_vision[i - 1][1]))
                    if i < len(small_vision) and small_vision[i][0] == x:
                        up_radius = max(up_radius, count_radius(small_vision[i][2] / const.VISION_BLOCK_SIZE, small_vision[i][1] - y))
                if len(big_vision) > 0:
                    while j < len(big_vision) and big_vision[j] < (x, y, 0):
                        j = j + 1
                    if j > 0 and big_vision[j - 1][0] == x:
                        up_radius = max(up_radius, count_radius(big_vision[j - 1][2] / const.VISION_BLOCK_SIZE, y - big_vision[j - 1][1]))
                    if j < len(big_vision) and big_vision[j][0] == x:
                        up_radius = max(up_radius, count_radius(big_vision[j][2] / const.VISION_BLOCK_SIZE, big_vision[j][1] - y))
                if up_radius > -0.5:
                    res[max(0, int(x - up_radius))][y] += 1
                    res[min(self.N, int(x + up_radius + 1))][y] -= 1
        
        for x in range(1, self.N):
            for y in range(1, self.M):
                res[x][y] += res[x - 1][y]
                if res[x][y] > 0 and self.bool_mask[x][y] is False:
                    a = self.mask.get_at((x, y))
                    a[3] = 0
                    self.vision_not_open[x // const.TEAM_VISION_BLOCK][y // const.TEAM_VISION_BLOCK] -= 1
                    self.bool_mask[x][y] = True
                    self.mask.set_at((x, y), a)


                


    def update_vision(self, entity: LivingEntity):
        # if entity.alive is False or self.heuristic_test(entity.position) is False:
        #     return
        self.brute_modify(entity.position, entity.attribute.vision)


class Team_Vision(Team_Vision_Grid):
    def __init__(self, team):
        super().__init__()
        self.team = team
        self.set: set[tuple[int, int, int]] = set()
        self.timer = Timer(0.05, self.modify_vision, once=False)
        self.visit = [[ False for _ in range(self.M)] for __ in range(self.N)]

    def handle_character_move(self, event: EventCharacterMove):
        x, y = int(event.character.position.x / const.VISION_BLOCK_SIZE), int(event.character.position.y / const.VISION_BLOCK_SIZE)
        if self.visit[x][y] is True or \
           event.original_pos.distance_to(event.character.position) < 0.1 or\
           self.heuristic_test(event.character.position) is False or\
           event.character.alive is False:
            return
        self.set.add((x, y, event.character.attribute.vision))
        self.visit[x][y] = True

    def modify_vision(self):
        if len(self.set) == 0:
            return
        print(self.team, self.set)
        if len(self.set) >= 150:
            print("special modify")
            self.special_modify(self.set)
        else:
            print("brute modify")
            for st in self.set:
                self.brute_modify(pg.Vector2(st[0], st[1]), st[2])
        self.set.clear()
        print("OK")


