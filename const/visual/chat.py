from enum import Enum, auto


class ChatMessageType(Enum):
    CHAT_COMMENT = auto()
    CHAT_BULLET = auto()


# rect: (x, y, width, height)
CHAT_POSITION = (353, 3)
CHAT_SIZE = (94, 244)
CHAT_FONT_SIZE = 6
AVATAR_WIDTH = 10
SPACING = (3, 3)
