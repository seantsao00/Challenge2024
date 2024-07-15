import random

import numpy as np

import const
from event_manager import EventChangeParty, EventStartGame
from instances_manager import get_event_manager


class PartySelector:

    def __init__(self, number_of_teams: int):
        self.__number_of_teams: int = number_of_teams
        self.__party_list: list[const.PartyType] =\
            [party for party in const.PartyType if party is not const.PartyType.NEUTRAL]
        self.__selected_party_indices: tuple[None | int] = [None for _ in range(number_of_teams)]
        get_event_manager().register_listener(EventChangeParty, self.__handle_change_party)

    def select_random_party(self, unique: bool):
        self.__selected_party_indices = np.random.choice(
            5, self.__number_of_teams, not unique).tolist()

    def __handle_change_party(self, event: EventChangeParty):
        """
        Handle EventChangeParty to update the selected party.
        """
        ev_manager = get_event_manager()
        operation, change = event.select_input
        if operation is const.PartySelectorInputType.CONFIRM:
            if None in self.__selected_party_indices:
                return
            ev_manager.post(EventStartGame())
        elif operation is const.PartySelectorInputType.CHANGE:
            team_index, change_direction = change
            if team_index >= self.__number_of_teams:
                return
            if self.__selected_party_indices[team_index] is None:
                if change_direction == 1:
                    self.__selected_party_indices[team_index] = 0
                else:
                    self.__selected_party_indices[team_index] = 4
            else:
                self.__selected_party_indices[team_index] = (
                    self.__selected_party_indices[team_index] + change_direction) % 5

    def selected_parties(self) -> list[const.PartyType]:
        return [None if index is None else self.__party_list[index] for index in self.__selected_party_indices]

    def is_ready(self) -> bool:
        return all(x is not None for x in self.__selected_party_indices)

    @property
    def number_of_teams(self) -> int:
        return self.__number_of_teams
