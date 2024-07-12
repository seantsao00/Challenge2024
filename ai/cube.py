import math
import random

import pygame as pg

import api.prototype


class Strategy:
    EPS = 1e-6
    ATTACK_RANGE_ESCAPE_FACTOR = 1.5
    TOWER_SIEGE_FACTOR = 1.2
    VISION_SIZE = 5
    VISION_TRIES = 8
    MELEE_TANK = 4
    RANGER_SIZE = 6

    def __init__(self):
        self.initialized = False
        self.api: api.prototype.API | None = None
        self.W: float | None = None
        self.fountain: api.prototype.Tower = []
        self.old_target_tower: api.prototype.Tower | None = None
        self.target_tower: api.prototype.Tower | None = None
        self.attackable_towers: list[api.prototype.Tower] = []
        self.squad_vision: list[api.prototype.Character] = []
        self.squad_attack_melee: list[api.prototype.Character] = []
        self.squad_attack_ranger: list[api.prototype.Character] = []
        self.spare_unit: list[api.prototype.Character] = []
        self.ready = False

    def initialize(self):
        self.W = self.api.get_grid_size()
        self.initialized = True

    def update_unit_info(self):
        # Update new tower instance
        owned_towers = self.api.get_owned_towers()
        visible_towers = self.api.get_visible_towers()
        self.fountain = [tower for tower in owned_towers if tower.is_fountain][0]
        new_towers = {tower.id: tower for tower in visible_towers}
        self.attackable_towers = [tower for tower in visible_towers if not tower.is_fountain]
        if self.target_tower is not None:
            self.old_target_tower = self.target_tower
            self.target_tower = new_towers[self.target_tower.id]

        # Get new info. Dict stores [ref, #ref].
        new_units = {character.id: [character, 0] for character in self.api.get_owned_characters()}

        # Renew pre-existing info: they might be dead, at a new position, etc.
        def renew_unit_list(ls: list[api.prototype.Character]):
            ls = [new_units[unit.id][0] for unit in ls if unit.id in new_units]
            for unit in ls:
                new_units[unit.id][1] += 1
            return ls
        self.squad_vision = renew_unit_list(self.squad_vision)
        self.spare_unit = renew_unit_list(self.spare_unit)
        self.squad_attack_melee = renew_unit_list(self.squad_attack_melee)
        self.squad_attack_ranger = renew_unit_list(self.squad_attack_ranger)

        # For #ref is zero, we put it in spare unit
        not_tracked = [val[0] for (key, val) in new_units.items() if val[1] == 0]
        self.spare_unit.extend(not_tracked)

    def take_spare(self, condition):
        yes, no = [], []
        for e in self.spare_unit:
            (yes, no)[0 if condition(e) else 1].append(e)
        self.spare_unit = no
        return yes

    def melee_escape(self, melee: api.prototype.Character):
        visible = self.api.get_visible_characters() + self.api.get_visible_towers()
        escaping_vector = pg.Vector2(0, 0)
        for unit in visible:
            displacement = melee.position - unit.position
            if (unit.team_id != melee.team_id and
                displacement.length() > Strategy.EPS and
                    displacement.length() <= unit.attack_range * Strategy.ATTACK_RANGE_ESCAPE_FACTOR):
                escaping_vector += displacement.normalize()
        if escaping_vector.length() <= Strategy.EPS:
            return False
        self.api.action_cast_ability([melee])
        self.api.action_move_along([melee], escaping_vector.normalize())
        return True

    def melee_try_extend_vision(self, unit: api.prototype.Character):
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

    def attack_ready(self, unit: api.prototype.Character):
        if self.target_tower is not None:
            if ((unit.position - self.target_tower.position).length() <=
                    self.target_tower.attack_range * Strategy.TOWER_SIEGE_FACTOR):
                self.api.action_move_clear([unit])
                return True
            else:
                self.api.action_move_to([unit], self.target_tower.position)
                return False
        return True

    def attack_tower_siege(self):
        self.target_tower = self.api.refresh_tower(self.target_tower)
        if self.target_tower is None:
            assert False
        if self.target_tower.team_id != self.old_target_tower.team_id:
            # Either succeeded or failed, give up and give it another try
            self.ready = False
            self.target_tower = None
            return
        self.api.action_move_to(self.squad_attack_melee +
                                self.squad_attack_ranger, self.target_tower.position)
        self.api.action_cast_ability(self.squad_attack_melee)
        self.api.action_attack(self.squad_attack_melee +
                               self.squad_attack_ranger, self.target_tower)

    def run(self, interface: api.prototype.API):
        self.api = interface

        # Initialize and update unit info
        if not self.initialized:
            self.initialize()
        self.update_unit_info()

        # Update unit lists
        def is_melee(x): return x.type == api.prototype.CharacterClass.MELEE
        def is_ranger(x): return x.type == api.prototype.CharacterClass.RANGER

        self.squad_vision.extend(self.take_spare(is_melee))
        self.spare_unit.extend(self.squad_vision[Strategy.VISION_SIZE:])
        del self.squad_vision[Strategy.VISION_SIZE:]
        self.squad_attack_melee.extend(self.take_spare(is_melee))
        self.spare_unit.extend(self.squad_attack_melee[Strategy.MELEE_TANK:])
        del self.squad_attack_melee[Strategy.MELEE_TANK:]
        self.squad_attack_ranger.extend(self.take_spare(is_ranger))
        self.spare_unit.extend(self.squad_attack_ranger[Strategy.RANGER_SIZE:])
        del self.squad_attack_ranger[Strategy.RANGER_SIZE:]

        if len(self.squad_vision) < Strategy.VISION_SIZE:
            self.api.change_spawn_type(self.fountain, api.prototype.CharacterClass.MELEE)
        elif len(self.squad_attack_ranger) < Strategy.RANGER_SIZE:
            self.api.change_spawn_type(self.fountain, api.prototype.CharacterClass.RANGER)
        else:
            self.api.change_spawn_type(self.fountain, api.prototype.CharacterClass.MELEE)

        # execute every team's job
        for melee in self.squad_vision:
            # if not self.melee_escape(melee):
            self.melee_try_extend_vision(melee)
        squad_attack = self.squad_attack_melee + self.squad_attack_ranger
        if self.target_tower is None:
            if len(self.attackable_towers) > 0:
                self.target_tower = self.attackable_towers[0]

        if self.target_tower is not None:
            if not self.ready:
                ready_states = [self.attack_ready(unit) for unit in squad_attack]
                if all(ready_states):
                    self.ready = True
            if self.ready:
                self.attack_tower_siege()


strategy = Strategy()


def every_tick(interface: api.prototype.API):
    print(f"cube's team is {interface.get_team_id()}")
    strategy.run(interface)
