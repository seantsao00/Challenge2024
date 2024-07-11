from __future__ import annotations

from typing import TYPE_CHECKING

from const import ChatMessageType
from event_manager.events import EventSendChat
from instances_manager import get_event_manager

if TYPE_CHECKING:
    from model.team import Team


class Chat:
    def __send_chat(self, type: ChatMessageType, team: Team, text: str):
        get_event_manager().post(EventSendChat(type=type, team=team, text=text))

    def send_comment(self, team: Team, text: str):
        self.__send_chat(ChatMessageType.CHAT_COMMENT, team, text)

    def send_bullet(self, team: Team, text: str):
        self.__send_chat(ChatMessageType.CHAT_BULLET, team, text)


chat = Chat()
