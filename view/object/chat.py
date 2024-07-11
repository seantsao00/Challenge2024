"""
Controls how the chat messages are displayed.
e.g. storing all the comments currently being displayed, drawing them on the screen, etc.
"""

from __future__ import annotations

import pygame as pg

from const import ChatMessageType
from const.visual import chat as CHAT
from event_manager import EventSendChat
from instances_manager import get_event_manager, get_model
from model.team import Team
from view.object import components
from view.object.object_base import ObjectBase
from view.screen_info import ScreenInfo
from view.textutil import font_loader


class _RescaledConstants:
    def __init__(self):
        self.CHAT_POSITION = ScreenInfo.scale(CHAT.CHAT_POSITION)
        self.CHAT_SIZE = ScreenInfo.scale(CHAT.CHAT_SIZE)
        self.AVATAR_WIDTH = int(ScreenInfo.scale(CHAT.AVATAR_WIDTH))
        self.SPACING = ScreenInfo.scale(CHAT.SPACING)


consts: _RescaledConstants | None = None


class CommentBox:
    def __init__(self, text: str, user_avatar: pg.Surface, width: float):
        font = font_loader.get_font(size=CHAT.CHAT_FONT_SIZE)
        avatar_size = user_avatar.get_size()
        text_surf = components.createTextBox(
            text, 'black', font, width - consts.SPACING[0] * 3 - avatar_size[0])
        text_size = text_surf.get_size()

        height = max(avatar_size[1], text_size[1]) + consts.SPACING[1] * 2
        self.__size = (width, height)
        self.__surf = pg.Surface((width, height), pg.SRCALPHA)
        pg.draw.rect(self.__surf, pg.Color(255, 255, 255, 127), (0, 0, width, height))
        self.__surf.blit(user_avatar, (consts.SPACING[0], consts.SPACING[1]))
        self.__surf.blit(text_surf, (consts.SPACING[0] * 2 + avatar_size[0], consts.SPACING[1]))

    def get_size(self) -> tuple[int, int]:
        return self.__size

    def draw(self, canvas: pg.Surface, position: tuple[int, int]):
        canvas.blit(self.__surf, position)

    def update(self):
        pass


class ChatView(ObjectBase):
    def __init__(self, canvas: pg.Surface):
        super().__init__(canvas, [8])
        global consts
        consts = _RescaledConstants()
        self.__initialized = False
        self.__canvas = canvas
        self.__chat_surface = pg.Surface(consts.CHAT_SIZE, pg.SRCALPHA)
        self.__comments: list[CommentBox] = []
        self.__frame_count = 0
        get_event_manager().register_listener(EventSendChat, self.handle_new_chat)

    def initialize(self):
        for idx, team in enumerate(get_model().teams):
            self.add_comment(team, f"Comment from Team {idx + 1} =^-w-^= zzzzz")

    def draw(self):
        if not self.__initialized:
            self.initialize()
            self.__initialized = True
        self.__chat_surface.fill(pg.Color(0, 0, 0, 0))
        cur_pos = [0, consts.CHAT_SIZE[1]]
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

    def update(self):
        # import random
        # self.__frame_count += 1
        # if self.__frame_count % 60 == 0:
        #     teamid = random.randint(0, 3)
        #     team = get_model().teams[teamid]
        #     if random.randint(0, 1) > 0:
        #         self.add_comment(
        #             team, f"random comment #{random.randint(1, 10 ** 8)} (intentionally made taller for demo)")
        #     else:
        #         teamid2 = random.randint(0, 3)
        #         team, self.add_comment(f"Team {teamid}'s Ranger was slain by Team {teamid2}!")
        pass

    def handle_new_chat(self, e: EventSendChat):
        if e.type == ChatMessageType.CHAT_COMMENT:
            self.add_comment(e.team, e.text)
        elif e.type == ChatMessageType.CHAT_BULLET:
            # TODO
            print("Bullet messages are not supported yet!")

    def add_comment(self, team: Team, text: str):
        avatar = components.createTeamAvatar(team, consts.AVATAR_WIDTH)
        self.__comments.append(CommentBox(text, avatar, consts.CHAT_SIZE[0]))
