import const
from event_manager import EventQuit, EventResumeModel
from instances_manager import get_event_manager


class PauseMenu:
    def __init__(self):
        self.state: const.PauseMenuState = const.PauseMenuState.CLOSED
        self.main_menu_options: list[const.PauseMainMenuOption] = list(const.PauseMainMenuOption)
        self.cursor_index = 0

    def move_cursor(self, move: int):
        if self.state is const.PauseMenuState.MAIN_MENU:
            self.cursor_index = (self.cursor_index + move +
                                 len(self.main_menu_options)) % len(self.main_menu_options)

    def execute(self):
        ev_manager = get_event_manager()
        option = self.main_menu_options[self.cursor_index]
        if option is const.PauseMainMenuOption.RESUME_GAME:
            ev_manager.post(EventResumeModel())
        elif option is const.PauseMainMenuOption.QUIT_GAME:
            ev_manager.post(EventQuit())

    def enable_menu(self):
        self.state = const.PauseMenuState.MAIN_MENU

    def disable_menu(self):
        self.state = const.PauseMenuState.CLOSED
