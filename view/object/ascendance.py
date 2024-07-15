from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from util import load_image
from view.object.entity_object import EntityObject
from view.screen_info import ScreenInfo

if TYPE_CHECKING:
    from model import Character


class AscendanceView(EntityObject):
    __images: dict[tuple[const.PartyType, const.AscendanceType], pg.Surface] = {}
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
        cls.image_initialized = True

    def draw(self):
        pass
        # TODO: add its priority

    def update(self):
        if not self.exist:
            return False
        self.priority[1] = int(self.entity.position[1])
        self.priority[2] = int(self.entity.position[0])
        return True
