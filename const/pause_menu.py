from enum import Enum, auto


class PauseMenuState(Enum):
    CLOSED = auto()
    MAIN_MENU = auto()
    CREDIT_BOARD = auto()


class PauseMainMenuOption(Enum):
    RESUME_GAME = auto()
    OPEN_CREDIT_BOARD = auto()
    QUIT_GAME = auto()


CREDIT_CONTENT = 'credit.json'
