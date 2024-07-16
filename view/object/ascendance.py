from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
import const.entity
from util import load_image
from view.object.entity_object import EntityObject
from view.screen_info import ScreenInfo

if TYPE_CHECKING:
    from model import Character


class AscendanceView(EntityObject):
    __images: dict[tuple[const.PartyType, const.AscendanceType],
                   tuple[pg.Surface, pg.Vector2]] = {}
    """
    structure: images[party][entity][state]

    The static dict that stores entity images.

    This dict is shared among all Entity instances,
    built from const, and initialized only once in init_convert.
    """

    def __init__(self, canvas: pg.Surface, entity: Character):
        self.entity: Character = entity
        super().__init__(canvas, entity, self.entity.position[1])
        self.register_listeners()

    @classmethod
    def init_convert(cls):
        # TODO: use util.load_image
        for party, ascendance_dict in const.ASCENDANCE_IMAGE.items():
            for ascendance, character_dict in ascendance_dict.items():
                for character, state_dict in character_dict.items():
                    for state, path in state_dict.items():
                        print(path)
                        w = const.ENTITY_SIZE[character][state] * 2 * ScreenInfo.resize_ratio
                        h = const.ENTITY_SIZE[character][state] * 2 * ScreenInfo.resize_ratio
                        cls.__images[(party, ascendance, character, state)
                                     ] = load_image(path, int(w), int(h))
        cls.image_initialized = True

    def draw(self):
        # TODO: add its priority
        entity = self.entity
        self.ascendance = Character.ascendance
        print(self.ascendance)
        for ascendance in self.ascendance:
            img = self.__images[(entity.team.party, ascendance, entity.entity_type, entity.state)]
            self.canvas.blit(img[0], img.get_rect(center=ScreenInfo.resize_ratio *
                                                  (entity.position + const.DRAW_DISPLACEMENT)+img[1]))

    def update(self):
        if not self.exist:
            return False
        self.priority[1] = int(self.entity.position[1])
        self.priority[2] = int(self.entity.position[0])
        return True
