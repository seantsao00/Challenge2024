from __future__ import annotations

from typing import Callable

import pygame as pg

from const.visual import scorebox
from instances_manager import get_model
from model.team import Team
from view.object import components
from view.object.animation import LinearAnimation
from view.object.object_base import ObjectBase
from view.screen_info import ScreenInfo
from view.textutil import font_loader


class Scorebox:
    def __init__(self, canvas: pg.Surface, team: Team, initial_position: tuple[int, int]):
        self.__canvas = canvas
        self.__team = team
        self.__team_score = self.__team.points
        self.__team_name_surface = font_loader.get_font(
            size=scorebox.SCOREBOX_FONT_SIZE).render(f"Team {self.__team.team_id}", False, 'black')
        self.__team_avatar = components.createTeamAvatar(
            self.__team, int(ScreenInfo.scale(scorebox.SCOREBOX_AVATAR_SIZE)))
        self.__position_x = initial_position[0]
        self.__position_y = LinearAnimation(
            initial_position[1], scorebox.SCOREBOX_ANIMATION_DURATION)

    def draw(self):
        position = (self.__position_x, self.__position_y.value)
        pg.draw.rect(self.__canvas, pg.color.Color(255, 255, 255, 127),
                     (*ScreenInfo.translate((0, 0), position), ScreenInfo.scale(70), ScreenInfo.scale(40)))
        self.__canvas.blit(
            self.__team_name_surface,
            self.__team_name_surface.get_rect(midleft=ScreenInfo.translate((20, 10), position))
        )
        score_surface = font_loader.get_font(size=scorebox.SCOREBOX_FONT_SIZE).render(
            f"{self.__team_score:.2f}", False, 'black')
        self.__canvas.blit(
            score_surface,
            score_surface.get_rect(topright=ScreenInfo.translate((70, 18), position))
        )
        self.__canvas.blit(self.__team_avatar, ScreenInfo.translate((2, 2), position))

    def update(self, position_y: float):
        self.__team_score = self.__team.points
        self.__position_y.value = position_y

    def cur_score(self):
        return self.__team_score


class ScoreboxesView(ObjectBase):
    def __init__(self, canvas: pg.Surface):
        super().__init__(canvas, [8])
        self.__initialized = False
        self.__boxes: list[Scorebox] = []

    def initialize(self):
        cur_y = scorebox.SCOREBOX_POSITION[1]
        for team in get_model().teams:
            self.__boxes.append(
                Scorebox(self.canvas, team, (scorebox.SCOREBOX_POSITION[0], cur_y)))
            cur_y += scorebox.SCOREBOX_HEIGHT + scorebox.SCOREBOX_SPACING

    def draw(self):
        if not self.__initialized:
            self.initialize()
            self.__initialized = True
        for box in self.__boxes:
            box.draw()

    def update(self):
        self.__boxes.sort(key=lambda box: box.cur_score(), reverse=True)
        cur_y = scorebox.SCOREBOX_POSITION[1]
        for box in self.__boxes:
            box.update(cur_y)
            cur_y += scorebox.SCOREBOX_HEIGHT + scorebox.SCOREBOX_SPACING
