import json
from dataclasses import dataclass

import const
from event_manager import EventQuit, EventResumeModel
from instances_manager import get_event_manager


@dataclass(kw_only=True)
class CreditContent:
    game_title: str
    title: str
    content: dict


class PauseMenu:
    def __init__(self):
        self.state: const.PauseMenuState = const.PauseMenuState.CLOSED
        self.main_menu_options: list[const.PauseMainMenuOption] = list(const.PauseMainMenuOption)
        self.cursor_index = 0
        with open(const.CREDIT_CONTENT, encoding='utf-8') as f:
            credit_content_data = json.load(f)
        self.credit_content: CreditContent = CreditContent(
            game_title=credit_content_data['game_title'],
            title=credit_content_data['title'],
            content=credit_content_data['content']
        )

    def move_cursor(self, move: int):
        if self.state is const.PauseMenuState.MAIN_MENU:
            self.cursor_index = (self.cursor_index + move +
                                 len(self.main_menu_options)) % len(self.main_menu_options)
        else:
            return

    def execute(self):
        ev_manager = get_event_manager()
        if self.state is const.PauseMenuState.MAIN_MENU:
            option = self.main_menu_options[self.cursor_index]
            if option is const.PauseMainMenuOption.RESUME_GAME:
                ev_manager.post(EventResumeModel())
            if option is const.PauseMainMenuOption.OPEN_CREDIT_BOARD:
                self.state = const.PauseMenuState.CREDIT_BOARD
            elif option is const.PauseMainMenuOption.QUIT_GAME:
                ev_manager.post(EventQuit())
        elif self.state is const.PauseMenuState.CREDIT_BOARD:
            self.state = const.PauseMenuState.MAIN_MENU

    def enable_menu(self):
        self.state = const.PauseMenuState.MAIN_MENU

    def disable_menu(self):
        self.state = const.PauseMenuState.CLOSED
