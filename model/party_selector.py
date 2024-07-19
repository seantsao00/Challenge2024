import numpy as np

import const
from event_manager import EventChangeParty, EventStartGame
from instances_manager import get_event_manager


class PartySelector:

    def __init__(self, number_of_teams: int, team_names: list[int]):
        self.__number_of_teams: int = number_of_teams
        self.__party_list: list[const.PartyType] =\
            [party for party in const.PartyType if party is not const.PartyType.NEUTRAL]
        def get_index(party: const.PartyType):
            for i in range(len(const.PartyType)):
                if party is self.__party_list[i]:
                    return i
            raise ValueError
        def get_team_party(name: str):
            if name == "team1" or name == "team2":
                return get_index(const.PartyType.POLICE)
            elif name == "team3" or name == "team5":
                return get_index(const.PartyType.FBI)
            elif name == "team4" or name == "team7":
                return get_index(const.PartyType.BLACK)
            elif name == "team6" or name == "team8":
                return get_index(const.PartyType.JUNIOR)
            elif name == "team9" or name == "team10":
                return get_index(const.PartyType.MOURI)
            else:
                return None
        self.__selected_party_indices: tuple[None | int] = [get_team_party(team_names[i]) for i in range(number_of_teams)]
        get_event_manager().register_listener(EventChangeParty, self.__handle_change_party)

    def select_random_party(self, unique: bool):
        self.__selected_party_indices = np.random.choice(
            len(const.PartyType)-1, self.__number_of_teams, not unique).tolist()

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
                    self.__selected_party_indices[team_index] = len(const.PartyType) - 2
            else:
                self.__selected_party_indices[team_index] = (
                    self.__selected_party_indices[team_index] + change_direction) % (len(const.PartyType) - 1)

    def selected_parties(self) -> list[const.PartyType]:
        return [None if index is None else self.__party_list[index] for index in self.__selected_party_indices]

    def is_ready(self) -> bool:
        return all(x is not None for x in self.__selected_party_indices)

    @property
    def number_of_teams(self) -> int:
        return self.__number_of_teams
