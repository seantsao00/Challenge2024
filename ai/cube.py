import math
import random

import pygame as pg

import api.prototype


class Strategy:
    VISION_SIZE = 5
    VISION_TRIES = 8

    def __init__(self):
        self.initialized = False
        self.api: api.prototype.API | None = None
        self.W: float | None = None
        self.fountain: api.prototype.Tower = []
        self.vision_squad: list[api.prototype.Character] = []
        self.spare_unit: list[api.prototype.Character] = []

    def initialize(self):
        self.W = self.api.get_grid_size()
        self.initialized = True

    def update_unit_info(self):
        # update new fountain instance
        self.fountain = [tower for tower in self.api.get_owned_towers() if tower.is_fountain][0]

        # Get new info. Dict stores [ref, #ref].
        new_units = {character.id: [character, 0] for character in self.api.get_owned_characters()}

        # Renew pre-existing info: they might be dead, at a new position, etc.
        def renew_unit_list(ls: list[api.prototype.Character]):
            ls = [new_units[unit.id][0] for unit in ls if unit.id in new_units]
            for unit in ls:
                new_units[unit.id][1] += 1
            return ls
        self.vision_squad = renew_unit_list(self.vision_squad)
        self.spare_unit = renew_unit_list(self.spare_unit)

        # For #ref is zero, we put it in spare unit
        not_tracked = [val[0] for (key, val) in new_units.items() if val[1] == 0]
        self.spare_unit.extend(not_tracked)

    def take_spare(self, condition):
        yes, no = [], []
        for e in self.spare_unit:
            (yes, no)[0 if condition(e) else 1].append(e)
        self.spare_unit = no
        return yes

    def try_extend_vision(self, unit: api.prototype.Character):
        if self.api.get_movement(unit).status is api.prototype.MovementStatusClass.TO_POSITION:
            return
        for _ in range(Strategy.VISION_TRIES):
            position = pg.Vector2(random.uniform(0, self.W), random.uniform(0, self.W))
            if (self.api.is_visible(position) or
                    self.api.get_terrain(position) == api.prototype.MapTerrain.OBSTACLE):
                continue
            self.api.action_move_to([unit], position)
            break
        else:
            self.api.action_move_to([unit], self.fountain.position)

    def run(self, interface: api.prototype.API):
        self.api = interface
        # initialize if not
        if not self.initialized:
            self.initialize()
        # update unit info
        self.update_unit_info()
        # update unit list
        self.vision_squad.extend(self.take_spare(
            lambda x: x.type == api.prototype.CharacterClass.MELEE))
        self.spare_unit.extend(self.vision_squad[Strategy.VISION_SIZE:])
        del self.vision_squad[Strategy.VISION_SIZE:]
        if len(self.vision_squad) < Strategy.VISION_SIZE:
            self.api.change_spawn_type(self.fountain, api.prototype.CharacterClass.MELEE)
        else:
            self.api.change_spawn_type(self.fountain, api.prototype.CharacterClass.RANGER)
        # execute every team's job
        self.try_extend_vision()


strategy = Strategy()


def every_tick(interface: api.prototype.API):
    strategy.run(interface)
