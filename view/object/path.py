from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from const.visual.priority import PRIORITY_ARROW
from view.object.entity_object import EntityObject
from view.screen_info import ScreenInfo

if TYPE_CHECKING:
    from model import Character


class PathView(EntityObject):
    def __init__(self, canvas: pg.Surface, entity: Character, team_id: int):
        super().__init__(canvas, entity)
        self.priority[0] = PRIORITY_ARROW
        self.entity: Character
        self.team_id = team_id

    def draw(self):
        entity = self.entity
        entity_path = entity.move_path
        entity_path = [ScreenInfo.resize_ratio * p for p in entity_path]
        if len(entity_path) > 1:
            pg.draw.lines(self.canvas, const.HEALTH_BAR_COLOR[entity.team.team_id],
                          False, entity_path, const.PATH_WIDTH)
            pg.draw.lines(self.canvas, (0, 0, 0),
                          False, entity_path, 2)
            pg.draw.circle(self.canvas, const.HEALTH_BAR_COLOR[entity.team.team_id],
                           entity_path[-1], const.DESTINATION_RADIUS, const.DESTINATION_RADIUS)
            pg.draw.lines(self.canvas, 'red',
                          False, entity_path[:10], const.PATH_WIDTH)
            pg.draw.circle(self.canvas, 'red',
                           entity_path[min(len(entity_path)-1, 10)], const.PATH_WIDTH, const.PATH_WIDTH)
