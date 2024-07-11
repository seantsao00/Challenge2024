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
    def __init__(self, canvas: pg.Surface, resize_ratio, position: tuple[int, int], team: Team):
        self.__canvas = canvas
        self.__resize_ratio = resize_ratio
        self.__position = position
        self.__team = team
        self.__team_score: int
        self.__team_name_surface = font_loader.get_font(
            size=16).render(str(team.team_name), False, 'black')
        self.__team_avatar = components.createTeamAvatar(
            self.__team, int(self.translate(scorebox.SCOREBOX_AVATAR_SIZE)))
        self.update()

    def translate(self, x: float, y: float | None = None):
        if y is None:
            return x * self.__resize_ratio
        return (
            (x + self.__position[0]) * self.__resize_ratio,
            (y + self.__position[1]) * self.__resize_ratio,
        )

    def draw(self):
        self.__canvas.blit(
            self.__team_name_surface,
            self.__team_name_surface.get_rect(midleft=self.translate(27, 12.5))
        )
        score_surface = font_loader.get_font(size=16).render(
            f"{self.__team_score:.2f}", False, 'black')
        self.__canvas.blit(
            score_surface,
            score_surface.get_rect(center=self.translate(35, 40))
        )
        self.__canvas.blit(self.__team_avatar, self.translate(0, 0))

    def update(self):
        self.__team_score = self.__team.points


class ScoreboxesView(ObjectBase):
    def __init__(self, canvas: pg.Surface):
        super().__init__(canvas, [8])
        self.__initialized = False
        self.__boxes: list[Scorebox] = []

    def initialize(self):
        for i, p in enumerate(scorebox.SCOREBOX_ANCHORS):
            if i < len(get_model().teams):
                self.__boxes.append(
                    Scorebox(self.canvas, ScreenInfo.resize_ratio, p, get_model().teams[i]))

    def draw(self):
        if not self.__initialized:
            self.initialize()
            self.__initialized = True
        for box in self.__boxes:
            box.draw()

    def update(self):
        for box in self.__boxes:
            box.update()
