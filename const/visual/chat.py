from enum import Enum, auto


class ChatMessageType(Enum):
    CHAT_COMMENT = auto()
    CHAT_BULLET = auto()


CHAT_POSITION = (363, 13)
CHAT_SIZE = (75, 204)
CHAT_FONT_SIZE = 6
AVATAR_WIDTH = 10
SPACING = (3, 3)
