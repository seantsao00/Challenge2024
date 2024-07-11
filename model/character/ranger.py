from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from event_manager import EventBulletCreate, EventUseRangerAbility
from instances_manager import get_event_manager, get_model
from model.bullet import BulletCommon, BulletRanger
from model.character import Character
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
        super().__init__(position, team, const.RANGER_ATTRIBUTE, const.CharacterType.RANGER, None)
        get_event_manager().register_listener(EventUseRangerAbility, listener=self.use_ability)

    def attack(self, enemy: Entity):
        now_time = get_model().get_time()
        dist = self.position.distance_to(enemy.position)
        if (self.team != enemy.team
            and dist <= self.attribute.attack_range
                and (now_time - self._attack_time) * self.attribute.attack_speed >= 1):
            bullet = BulletCommon(position=self.position,
                                  victim=enemy,
                                  team=self.team,
                                  attacker=self,
                                  damage=const.RANGER_ATTRIBUTE.attack_damage,
                                  speed=const.BULLET_RANGER_SPEED)
            get_event_manager().post(EventBulletCreate(bullet=bullet))
            self._attack_time = now_time

    def cast_ability(self, *args, **kwargs):
        """This function is called after clicked Q, it wouldn't generate bullet"""

        log_info("Ranger ability is on")
        now_time = get_model().get_time()
        if now_time - self.abilities_time < self.attribute.ability_cd:
            return
        self.abilities_time = now_time
        get_model().RangerAbility = True

    def use_ability(self, event: EventUseRangerAbility):
        """This function is called after clicked Q and left button, it would generate bullet"""

        if self.position.distance_to(event.position) <= self.attribute.attack_range:
            get_model().RangerAbility = False
            log_info("Ranger cast ablility")
            bullet = BulletRanger(position=self.position,
                                  target=event.position,
                                  team=self.team,
                                  attacker=self)
            get_event_manager().post(EventBulletCreate(bullet=bullet))
