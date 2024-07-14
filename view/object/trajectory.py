from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from const.visual.priority import PRIORITY_ARROW
from view.object.entity_object import EntityObject
from view.screen_info import ScreenInfo

if TYPE_CHECKING:
    from model import Character


class TrajectoryView(EntityObject):
    def __init__(self, canvas: pg.Surface, entity: Character, team_id: int):
        super().__init__(canvas, entity)
        self.priority[0] = PRIORITY_ARROW
        self.entity: Character
        self.team_id = team_id

    def draw(self):
        entity = self.entity
        entity_path = entity.move_path
        if entity_path is not None and len(entity_path) > 1:
            entity_path = [[x * ScreenInfo.resize_ratio for x in p] for p in entity_path]
            pg.draw.lines(self.canvas, const.HEALTH_BAR_COLOR[entity.team.team_id],
                          False, entity_path, const.TRAJECTORY_WIDTH)
            pg.draw.lines(self.canvas, (0, 0, 0),
                          False, entity_path, 2)
            pg.draw.circle(self.canvas, const.HEALTH_BAR_COLOR[entity.team.team_id],
                           entity_path[-1], const.DESTINATION_RADIUS, const.DESTINATION_RADIUS)
            pg.draw.lines(self.canvas, 'red',
                          False, entity_path[:10], const.TRAJECTORY_WIDTH)
            pg.draw.circle(self.canvas, 'red',
                           entity_path[min(len(entity_path)-1, 10)], const.TRAJECTORY_WIDTH, const.TRAJECTORY_WIDTH)
