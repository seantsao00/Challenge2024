from __future__ import annotations

from math import pi
from typing import TYPE_CHECKING

import pygame as pg

import const
from const.visual.priority import PRIORITY_CD
from instances_manager import get_model
from util import crop_image
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
        w, h = pg.Vector2(const.ENTITY_SIZE[entity.entity_type]
                          [entity.state]) * ScreenInfo.resize_ratio
        w, h = int(w), int(h)
        cd_width = min(get_model().get_time() - entity.abilities_time, entity.attribute.ability_cd) / \
            entity.attribute.ability_cd * w
        top_left = (self.entity.position + const.CD_BAR_UPPER) * \
            ScreenInfo.resize_ratio - pg.Vector2(w/2, h)
        pg.draw.rect(self.canvas, (0, 0, 0), (*top_left, w, 1 * ScreenInfo.resize_ratio))
        pg.draw.rect(self.canvas, (0, 0, 255), (*top_left, cd_width, 1 * ScreenInfo.resize_ratio))


class TowerCDView(BarCDView):
    images: dict[const.CharacterType, pg.Surface] = {}
    """(Surface, position)"""

    def __init__(self, canvas: pg.Vector2, entity: Tower):
        super().__init__(canvas, entity)
        self.entity: Tower

    @classmethod
    def init_convert(cls):
        length = int(const.TOWER_CD_RADIUS[1] * ScreenInfo.resize_ratio * 2 * 0.7)
        for character_type, path in const.WEAPON_IMAGE.items():
            img = pg.image.load(path)
            cls.images[character_type] = crop_image(img, length, length)
        cls.image_initialized = True

    def draw(self):
        entity = self.entity
        if entity.last_generate < 0:
            return

        w, h = pg.Vector2(const.ENTITY_SIZE[entity.entity_type]
                          [entity.state]) * ScreenInfo.resize_ratio
        w, h = int(w), int(h)
        radius, inner_radius = pg.Vector2(const.TOWER_CD_RADIUS) * ScreenInfo.resize_ratio
        width = const.TOWER_CD_RADIUS[0] - const.TOWER_CD_RADIUS[1]
        position = ScreenInfo.resize_ratio * entity.position + pg.Vector2(w/2, h/2)
        pg.draw.circle(self.canvas, const.TOWER_CD_COLOR[0], position, radius, int(
            width * ScreenInfo.resize_ratio))
        pg.draw.circle(self.canvas, const.TOWER_CD_COLOR[2], position, inner_radius, 0)
        img = self.images[entity.character_type]
        self.canvas.blit(img, img.get_rect(center=position))
        cd_remaining = (get_model().get_time() - entity.last_generate) / entity.period
        pg.draw.arc(self.canvas, const.CD_BAR_COLOR,
                    pg.Rect((position + pg.Vector2(-radius, -radius)),
                            pg.Vector2(radius*2, radius*2)), pi / 2 - pi * 2 * cd_remaining, pi / 2, int(width*ScreenInfo.resize_ratio))
