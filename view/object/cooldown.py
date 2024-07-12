from __future__ import annotations

from math import pi
from typing import TYPE_CHECKING

import pygame as pg

import const
from const.visual.priority import PRIORITY_CD
from instances_manager import get_model
from view.object.entity_object import EntityObject
from view.screen_info import ScreenInfo

if TYPE_CHECKING:
    from model import Character, Tower


class BarCDView(EntityObject):
    """View of cooldown indicators, such as bar or circle."""

    def __init__(self, canvas: pg.Surface, entity: Character):
        super().__init__(canvas, entity)
        self.priority = [PRIORITY_CD, entity.position[1], entity.position[0]]
        self.entity: Character
        self.register_listeners()


class AbilitiesCDView(BarCDView):
    def __init__(self, canvas: pg.Surface, entity: Character):
        super().__init__(canvas, entity)
        self.entity: Character
        self.register_listeners()

    def draw(self):
        entity = self.entity
        entity_size = const.ENTITY_SIZE[entity.entity_type][entity.state]
        cd_width = min(get_model().get_time() - entity.abilities_time, entity.attribute.ability_cd) / \
            entity.attribute.ability_cd * entity_size * 2 * ScreenInfo.resize_ratio
        top = (self.entity.position.x - entity_size) * ScreenInfo.resize_ratio
        left = (self.entity.position.y - entity_size -
                const.CD_BAR_UPPER) * ScreenInfo.resize_ratio
        pg.draw.rect(self.canvas, (0, 0, 0),
                     (top, left, entity_size * 2 * ScreenInfo.resize_ratio, 2 * ScreenInfo.resize_ratio))
        pg.draw.rect(self.canvas, (0, 0, 255),
                     (top, left, cd_width, 2 * ScreenInfo.resize_ratio))


class TowerCDView(BarCDView):
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
        if entity.last_generate < 0:
            return

        entity_size = const.ENTITY_SIZE[entity.entity_type][entity.state]
        radius = entity_size / 1.5 * ScreenInfo.resize_ratio
        position = ScreenInfo.resize_ratio * \
            (entity.position + pg.Vector2(entity_size, entity_size) + const.DRAW_DISPLACEMENT)
        pg.draw.circle(self.canvas, 'black', position, radius,
                       width=int(3 * ScreenInfo.resize_ratio))
        inner_radius = radius - int(3 * ScreenInfo.resize_ratio)
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
        cd_remaining = (get_model().get_time() - entity.last_generate) / entity.period
        pg.draw.arc(self.canvas, const.CD_BAR_COLOR, pg.Rect((ScreenInfo.resize_ratio*(entity.position+const.DRAW_DISPLACEMENT) + pg.Vector2(ScreenInfo.resize_ratio*entity_size - radius,
                    ScreenInfo.resize_ratio*entity_size - radius)), pg.Vector2(radius*2, radius*2)), pi / 2 - pi * 2 * cd_remaining, pi / 2, width=int(3*ScreenInfo.resize_ratio))
