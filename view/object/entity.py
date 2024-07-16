from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from model import Bullet, Character
from util import load_image
from view.object.entity_object import EntityObject
from view.screen_info import ScreenInfo

if TYPE_CHECKING:
    from model import Entity


class EntityView(EntityObject):
    __images: dict[tuple[const.PartyType, const.EntityType, const.EntityState],
                   tuple[pg.Surface, pg.Vector2]] = {}
    """
    structure: __images[(party, entity, state)]

    The static dict that stores entity images.

    This dict is shared among all Entity instances,
    built from const, and initialized only once in init_convert.
    """
    __ascendance_character_images: dict[tuple[const.PartyType, const.EntityType, const.EntityState, frozenset[const.AscendanceType]],
                                        tuple[pg.Surface, pg.Vector2]] = {}
    """
    structure: __ascendance_images[(party, entity, state, frozenset(ascendance))]
    """

    def __init__(self, canvas: pg.Surface, entity: Entity):
        self.entity: Entity = entity
        super().__init__(canvas, entity, self.entity.position[1])
        self.register_listeners()

    @classmethod
    def init_convert(cls):
        for party, entity_dict in const.ENTITY_IMAGE.items():
            for entity, state_dict in entity_dict.items():
                for state, path in state_dict.items():
                    w, h = pg.Vector2(const.ENTITY_SIZE[entity][state]) * ScreenInfo.resize_ratio
                    w, h = int(w), int(h)
                    cls.__images[(party, entity, state)] = load_image(path, w, h)
        cls.image_initialized = True

    @classmethod
    def __stack_ascendant_character(cls, party: const.PartyType, character_type: const.CharacterType, state: const.EntityState, ascendance_set: frozenset):
        w, h = pg.Vector2(const.ENTITY_SIZE[character_type][state]) * ScreenInfo.resize_ratio
        w, h = int(w), int(h)
        surface = pg.Surface((w, h), pg.SRCALPHA)
        img, displacement = load_image(const.ENTITY_IMAGE[party][character_type][state], w, h)
        surface.blit(img, displacement)
        for ascendance in ascendance_set:
            print(party, character_type, state, ascendance, w, h)
            img, displacement = load_image(
                const.ASCENDANCE_IMAGE[party][character_type][state][ascendance], w, h)
            surface.blit(img, displacement)
        cls.__ascendance_character_images[(
            party, character_type, state, ascendance_set)] = surface, pg.Vector2(0, 0)

    def draw(self):
        entity = self.entity
        img, displacement = self.__images[(entity.team.party, entity.entity_type, entity.state)]
        party, entity_type, state = entity.team.party, entity.entity_type, entity.state
        w, h = pg.Vector2(const.ENTITY_SIZE[entity_type][state]) * ScreenInfo.resize_ratio
        w, h = int(w), int(h)
        if isinstance(entity, Character):
            index = (party, entity_type, state, frozenset(entity.ascendance))
            if index not in self.__ascendance_character_images:
                self.__stack_ascendant_character(*index)
            img, displacement = self.__ascendance_character_images[index]
            self.canvas.blit(img, ScreenInfo.resize_ratio * (entity.position) -
                             pg.Vector2(w/2, h) + displacement)
        elif isinstance(entity, Bullet):
            img = pg.transform.rotate(img, entity.view_rotate)
            self.canvas.blit(img, img.get_rect(center=ScreenInfo.resize_ratio *
                                               (entity.position + const.DRAW_DISPLACEMENT)))
        else:
            index = (party, entity_type, state)
            img, displacement = self.__images[index]
            self.canvas.blit(img, ScreenInfo.resize_ratio * (entity.position) -
                             pg.Vector2(w/2, h) + displacement)

    def update(self):
        if not self.exist:
            return False
        self.priority[1] = int(self.entity.position[1])
        self.priority[2] = int(self.entity.position[0])
        return True
