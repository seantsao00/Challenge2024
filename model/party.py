import sys

import pygame as pg

import const
from event_manager import EventSelectParty
from instances_manager import get_event_manager


class PartySelection:

    def __init__(self):
        self.selected_parties = [const.PartyTypes(0) for _ in range(4)]
        get_event_manager().register_listener(EventSelectParty, self.handle_select_party)

    def handle_select_party(self, event: EventSelectParty):
        """
        Handle EventChooseParty to update the selected party.
        """
        if event.increase:
            self.selected_parties[event.index] = (
                self.selected_parties[event.index] + 1) % len(const.PartyTypes)
        else:
            self.selected_parties[event.index] = (
                self.selected_parties[event.index] + len(const.PartyTypes) - 1) % len(const.PartyTypes)
