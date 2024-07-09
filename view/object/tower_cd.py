from __future__ import annotations

from math import pi
from typing import TYPE_CHECKING

import pygame as pg

import const
from view.object.entity_object import EntityObject

if TYPE_CHECKING:
    from model import Tower


class TowerCDView(EntityObject):
    images = {}
    image_initialized = False

    def __init__(self, canvas: pg.Vector2, entity: Tower):
        super().__init__(canvas, entity)
        self.entity: Tower
        if not self.image_initialized:
            self.init_convert()
        self.melee_weapon = self.images[const.CharacterType.MELEE]
        self.ranger_weapon = self.images[const.CharacterType.RANGER]
        self.sniper_weapon = self.images[const.CharacterType.SNIPER]

    @classmethod
    def init_convert(cls):
        for character_type, path in const.WEAPON_IMAGE.items():
            img = pg.image.load(path)
            cls.images[character_type] = img.convert_alpha()
        cls.image_initialized = True

    def draw(self):
        entity = self.entity
        if entity.spawn_timer is None:
            return

        entity_size = const.ENTITY_SIZE[entity.entity_type][entity.state]
        radius = entity_size / 1.5 * self.resize_ratio
        position = self.resize_ratio * (entity.position + pg.Vector2(entity_size, entity_size))
        pg.draw.circle(self.canvas, 'black', position, radius, width=int(3 * self.resize_ratio))
        inner_radius = radius - int(3 * self.resize_ratio)
        pg.draw.circle(self.canvas, 'white', position, inner_radius, 0)
        if entity.character_type == const.CharacterType.MELEE:
            weapon_image = self.melee_weapon
        elif entity.character_type == const.CharacterType.RANGER:
            weapon_image = self.ranger_weapon
        elif entity.character_type == const.CharacterType.SNIPER:
            weapon_image = self.sniper_weapon
        else:
            weapon_image = None
        if weapon_image:
            weapon_image = pg.transform.scale(
                weapon_image, (int(inner_radius * 2 / 2 ** 0.5), int(inner_radius * 2 / 2 ** 0.5)))
            self.canvas.blit(
                weapon_image, (position[0] - inner_radius / 2 ** 0.5, position[1] - inner_radius / 2 ** 0.5))
        cd_remaining = (entity.spawn_timer.interval -
                        entity.spawn_timer.get_remaining_time()) / entity.spawn_timer.interval
        pg.draw.arc(self.canvas, const.CD_BAR_COLOR, pg.Rect((self.resize_ratio*entity.position + pg.Vector2(self.resize_ratio*entity_size - radius,
                    self.resize_ratio*entity_size - radius)), pg.Vector2(radius*2, radius*2)), pi / 2, pi / 2 - pi * 2 * cd_remaining, width=int(3*self.resize_ratio))
