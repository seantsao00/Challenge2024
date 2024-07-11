from __future__ import annotations

import pygame as pg

from const.visual import scorebox
from instances_manager import get_model
from model.team import Team
from view.object import components
from view.object.object_base import ObjectBase
from view.screen_info import ScreenInfo
from view.textutil import font_loader


class Scorebox:
    def __init__(self, canvas: pg.Surface, team: Team):
        self.__canvas = canvas
        self.__team = team
        self.__team_score: int
        self.__team_name_surface = font_loader.get_font(
            size=16).render(str(team.team_name), False, 'black')
        self.__team_avatar = components.createTeamAvatar(
            self.__team, int(ScreenInfo.scale(scorebox.SCOREBOX_AVATAR_SIZE)))
        self.update()

    def draw(self, position: tuple[int, int]):
        self.__canvas.blit(
            self.__team_name_surface,
            self.__team_name_surface.get_rect(midleft=ScreenInfo.translate((27, 12.5), position))
        )
        score_surface = font_loader.get_font(size=16).render(
            f"{self.__team_score:.2f}", False, 'black')
        self.__canvas.blit(
            score_surface,
            score_surface.get_rect(center=ScreenInfo.translate((35, 40), position))
        )
        self.__canvas.blit(self.__team_avatar, ScreenInfo.translate((0, 0), position))

    def update(self):
        self.__team_score = self.__team.points


class ScoreboxesView(ObjectBase):
    def __init__(self, canvas: pg.Surface):
        super().__init__(canvas, [8])
        self.__initialized = False
        self.__boxes: list[Scorebox] = []

    def initialize(self):
        for team in get_model().teams:
            self.__boxes.append(Scorebox(self.canvas, team))

    def draw(self):
        if not self.__initialized:
            self.initialize()
            self.__initialized = True
        for i, box in enumerate(self.__boxes):
            box.draw(scorebox.SCOREBOX_ANCHORS[i])

    def update(self):
        for box in self.__boxes:
            box.update()
