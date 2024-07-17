"""
Controls how the chat messages are sent.
e.g. doing some checks before the message is actually sent
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from const import ChatMessageType, PartyType
from event_manager.events import EventSendChat
from instances_manager import get_event_manager

if TYPE_CHECKING:
    from model.team import Team


class Chat:
    def __init__(self) -> None:
        self.__comment_history: list[tuple[int, str]] = []
        
    def __send_chat(self, message_type: ChatMessageType, team: Team | None, text: str):
        get_event_manager().post(EventSendChat(type=message_type, team=team, text=text))

    def send_comment(self, team: Team, text: str):
        self.__comment_history.append((team.team_id, text))
        self.__send_chat(ChatMessageType.CHAT_COMMENT, team, text)

    def send_system(self, text: str):
        self.__send_chat(ChatMessageType.CHAT_SYSTEM, None, text)
        
    def get_comment_history(self, num: int) -> list[tuple[int, str]]:
        return self.__comment_history[-num:].copy()


chat = Chat()
