from event_manager import EventQuit, EventResumeModel
from instances_manager import get_event_manager


class PauseMenu:
    def __init__(self):
        self.enabled: bool = False
        self.options = ['Resume', 'Exit']
        self.selected = 0

    def change_selected(self, move):
        self.selected += move
        if self.selected == 2:
            self.selected = 0
        elif self.selected == -1:
            self.selected = 1

    def execute(self):
        ev_manager = get_event_manager()
        if self.selected == 0:
            ev_manager.post(EventResumeModel())
        elif self.selected == 1:
            ev_manager.post(EventQuit())

    def enable_menu(self):
        self.enabled = True

    def disable_menu(self):
        self.enabled = False
