from __future__ import annotations

import pygame as pg

from const.visual.priority import PRIORITY_CHAT
from instances_manager import get_model
from view.object import components
from view.object.object_base import ObjectBase
from view.textutil import font_loader

CHAT_WIDTH = 100 * 900 / 250
AVATAR_WIDTH = int(15 * 900 / 250)
SPACING_VERTICAL = 10
SPACING_HORIZONTAL = 10


class CommentBox:
    def __init__(self, canvas: pg.Surface, text: str, user_avatar: pg.Surface, width: float):
        self.__canvas = canvas

        font = font_loader.get_font(size=8)
        avatar_size = user_avatar.get_size()
        text_surf = components.createTextBox(text, 'black', font, width - SPACING_HORIZONTAL * 2)
        text_size = text_surf.get_size()

        height = avatar_size[1] + text_size[1] + SPACING_VERTICAL * 3
        self.__surf = pg.Surface((width, height), pg.SRCALPHA)
        pg.draw.rect(self.__surf, pg.Color(255, 255, 255, 127), (0, 0, width, height))
        self.__surf.blit(user_avatar, (SPACING_HORIZONTAL, SPACING_VERTICAL))
        self.__surf.blit(text_surf, (SPACING_HORIZONTAL, SPACING_VERTICAL * 2 + avatar_size[1]))

    def draw(self):
        self.__canvas.blit(self.__surf, (0, 0))

    def update(self):
        pass


class ChatView(ObjectBase):
    def __init__(self, canvas: pg.Surface):
        super().__init__(canvas, [PRIORITY_CHAT])
        self.__initialized = False
        self.__canvas = canvas

    def initialize(self):
        ava = components.createTeamAvatar(get_model().teams[0], AVATAR_WIDTH)
        self.__box = CommentBox(
            self.__canvas, "This is a \nSUSPICIOUS\nand loooooooooooooooooong demo text\nTeam 69's Ranger was slain by Team 8!", ava, CHAT_WIDTH)

    def draw(self):
        if not self.__initialized:
            self.initialize()
            self.__initialized = True
        self.__box.draw()

    def update(self):
        pass
