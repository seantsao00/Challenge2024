"""
Controls how the chat messages are displayed.
e.g. storing all the comments currently being displayed, drawing them on the screen, etc.
"""

from __future__ import annotations

import pygame as pg

import const
import const.team
from event_manager import EventSendChat
from instances_manager import get_event_manager, get_model
from model.team import NeutralTeam, Team
from view.object import components
from view.object.animation import LinearAnimation, LinearAnimationEasings
from view.object.object_base import ObjectBase
from view.screen_info import ScreenInfo
from view.textutil import font_loader


class _RescaledConstants:
    def __init__(self):
        self.CHAT_POSITION = ScreenInfo.scale(const.CHAT_POSITION)
        self.CHAT_SIZE = ScreenInfo.scale(const.CHAT_SIZE)
        self.AVATAR_WIDTH = int(ScreenInfo.scale(const.AVATAR_WIDTH))
        self.SPACING = ScreenInfo.scale(const.SPACING)


consts: _RescaledConstants | None = None


class CommentBox:
    def __init__(self, text: str, user_avatar: pg.Surface | None, width: float, critical: bool = True):
        font = font_loader.get_font(size=const.CHAT_FONT_SIZE)
        avatar_size = user_avatar.get_size()
        if not critical:
            text_surf = components.create_text_box(
                text, 'black', font, width - consts.SPACING[0] * 3 - avatar_size[0])
        else:
            text_surf = components.create_text_box(
                text, (230, 0, 0), font, width - consts.SPACING[0] * 3 - avatar_size[0])

        text_size = text_surf.get_size()

        height = max(avatar_size[1], text_size[1]) + consts.SPACING[1] * 2
        self.__size = (width, height)
        self.__background_surf = pg.Surface((width, height), pg.SRCALPHA)
        self.__background_surf.set_alpha(128)
        self.__background_surf.fill((220, 220, 220))
        self.__surf = pg.Surface((width, height), pg.SRCALPHA)
        self.__surf.blit(user_avatar, (consts.SPACING[0], consts.SPACING[1]))
        self.__surf.blit(text_surf, (consts.SPACING[0] * 2 + avatar_size[0], consts.SPACING[1]))

    def get_size(self) -> tuple[int, int]:
        return self.__size

    def draw(self, canvas: pg.Surface, position: tuple[int, int]):
        canvas.blit(self.__background_surf, position)
        canvas.blit(self.__surf, position)

    def update(self):
        pass


class ChatView(ObjectBase):
    def __init__(self, canvas: pg.Surface):
        super().__init__(canvas, [8])
        global consts
        consts = _RescaledConstants()
        self.__canvas = canvas
        self.__chat_surface = pg.Surface(consts.CHAT_SIZE, pg.SRCALPHA)
        self.__comments: list[CommentBox] = []
        self.__scroll = LinearAnimation(0, 1, LinearAnimationEasings.easeOutCubic)
        self.__total_scroll = 0
        get_event_manager().register_listener(EventSendChat, self.handle_new_chat)

    def draw(self):
        self.__chat_surface.fill(pg.Color(0, 0, 0, 0))
        cur_pos = [0, consts.CHAT_SIZE[1] + self.__total_scroll - self.__scroll.value]
        iter = len(self.__comments) - 1
        while iter >= 0 and cur_pos[1] > 0:
            comment = self.__comments[iter]
            cur_pos[1] -= comment.get_size()[1]
            comment.draw(self.__chat_surface, cur_pos)
            cur_pos[1] -= consts.SPACING[1]
            iter -= 1
        if iter >= 0:
            del self.__comments[:(iter + 1)]
        self.__canvas.blit(self.__chat_surface, consts.CHAT_POSITION)

    def handle_new_chat(self, e: EventSendChat):
        if e.type == const.ChatMessageType.CHAT_COMMENT:
            self.add_comment(e.team, e.text)
        elif e.type == const.ChatMessageType.CHAT_SYSTEM:
            team = get_model().neutral_team
            self.add_comment(team, e.text)

    def add_comment(self, team: Team, text: str):
        avatar = components.create_team_avatar(team, consts.AVATAR_WIDTH)
        critical = (team.party is const.PartyType.NEUTRAL)
        comment_box = CommentBox(text, avatar, consts.CHAT_SIZE[0], critical)
        self.__comments.append(comment_box)
        self.__total_scroll += comment_box.get_size()[1] + consts.SPACING[1]
        self.__scroll.value = self.__total_scroll
