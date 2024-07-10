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

    def __handle_change_party(self, event: EventChangeParty):
        """
        Handle EventChangeParty to update the selected party.
        """
        ev_manager = get_event_manager()
        operation, change = event.select_input
        if operation is const.PartySelectInput.CONFIRM:
            if None in self.__selected_party_indices:
                return
            ev_manager.post(EventStartGame)
        elif operation is const.PartySelectInput.CHANGE:
            team_index, change_direction = change
            if self.__selected_party_indices[team_index] is None:
                if change_direction == 1:
                    self.__selected_party_indices[team_index] = 0
                else:
                    self.__selected_party_indices[team_index] = 4
            else:
                self.__selected_party_indices[team_index] = (self.__selected_party_indices[team_index] + change_direction) % 5

    def selected_parties(self) -> list[const.PartyType]:
        return [self.__party_list[index] for index in self.__selected_party_indices]
