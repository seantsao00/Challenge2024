from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from event_manager import EventBulletCreate, EventUseRangerAbility
from instances_manager import get_event_manager, get_model
from model.bullet import BulletCommon, BulletRanger
from model.character.character import Character
from model.timer import Timer
from util import log_info

if TYPE_CHECKING:
    from model.entity import Entity
    from model.team import Team


class Ranger(Character):
    """
    Class for the ranger fighter
    Ranger fighter has the following unique moves:
     - area_attack: Attack a locations and damage all nearby foes.
    """

    def __init__(self, position: pg.Vector2 | tuple[float, float], team: Team):
        super().__init__(position, team, const.RANGER_ATTRIBUTE,
                         const.CharacterType.RANGER, const.CharacterState.LEFT)
        get_event_manager().register_listener(EventUseRangerAbility,
                                              listener=self.use_ability, channel_id=self.id)

    def attack(self, enemy: Entity):
        now_time = get_model().get_time()
        dist = self.position.distance_to(enemy.position)
        if (self.team != enemy.team
            and dist <= self.attribute.attack_range
                and (now_time - self._last_attack_time) * self.attribute.attack_speed >= 1):
            bullet = BulletCommon(position=self.position,
                                  victim=enemy,
                                  team=self.team,
                                  attacker=self,
                                  damage=const.RANGER_ATTRIBUTE.attack_damage,
                                  speed=const.BULLET_RANGER_SPEED)
            get_event_manager().post(EventBulletCreate(bullet=bullet))
            self._last_attack_time = now_time

    def cast_ability(self, *args, **kwargs):
        """`kwargs` should contain position (default to my position)"""
        target = kwargs.get('position', self.position)
        now_time = get_model().get_time()
        if now_time - self.abilities_time < self.attribute.ability_cd:
            print(f"[Ranger] {self} is casting ability too fast")
            return
        if not self.reachable(target):
            print(f"[Ranger] {self} is casting ability too far")
            return
        print(f"[Ranger] {self} casted ability")
        self.abilities_time = now_time
        get_event_manager().post(EventUseRangerAbility(position=target), channel_id=self.id)
        self.ascendance.add(const.AscendanceType.ARMOR)
        Timer(interval=self.attribute.armor_show_time,
              function=self.handler_lost_ascendance, once=True)

    def manual_cast_ability(self, *args, **kwargs):
        """
        This function is called after clicked Q, it wouldn't generate bullet.
        Actual call is handled inside model.
        """
        now_time = get_model().get_time()
        if now_time - self.abilities_time < self.attribute.ability_cd:
            return
        # This is moved to model preventing ability double spam
        # self.abilities_time = now_time
        get_model().ranger_ability = True
        get_model().ranger_controlling = self
        log_info(f"[Ranger] {self} Ability is on")

    def use_ability(self, event: EventUseRangerAbility):
        """This function is called after clicked Q and left button, it would generate bullet"""
        # Range determine is moved outside this function, as there might be lag
        # between of API and event manager (which casing the event fail is quite weird)

        # In case of API cast ability, this controlling will not be overritten,
        # to ensure API does not interrupt human control.
        log_info(f"[Ranger] {self} Cast ablility")
        bullet = BulletRanger(position=self.position,
                              target=event.position,
                              team=self.team,
                              attacker=self)
        get_event_manager().post(EventBulletCreate(bullet=bullet))

    def handler_lost_ascendance(self):
        if const.AscendanceType.ARMOR in self.ascendance:
            self.ascendance.remove(const.AscendanceType.ARMOR)
