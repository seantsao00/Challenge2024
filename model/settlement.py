import random

import pygame as pg

import const
from event_manager import EventChangeParty, EventStartGame
from instances_manager import get_event_manager, get_model


class Settlement:

    def __init__(self, number_of_teams: int):
        self.__number_of_teams: int = number_of_teams
        self.__rank_of_teams: list = []
        self.__scope_position = pg.Vector2(-100, -100)
        self.__scope_target_index: int = 0

    def ranking(self):
        model = get_model()
        self.__rank_of_teams = sorted(model.teams, key=lambda team: team.points)

    def update(self) -> bool:
        team_position = const.SETTLEMENT_TEAM_POSITION
        if self.__scope_position == team_position[self.__rank_of_teams[self.__scope_target_index].team_id]:
            self.__scope_target_index += 1
        if self.__scope_target_index >= 3:
            return True

        displacement = (
            team_position[self.__rank_of_teams[self.__scope_target_index].team_id] - self.__scope_position).normalize()
        self.__scope_position += displacement
        return True

    @property
    def scope_position(self) -> pg.Vector2:
        return self.__scope_position
