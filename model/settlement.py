import random

import pygame as pg

import const
from event_manager import EventChangeParty, EventStartGame
from instances_manager import get_event_manager, get_model
from model.team import Team


class Settlement:

    def __init__(self, number_of_teams: int):
        self.__number_of_teams: int = number_of_teams
        self.__rank_of_teams: list = [Team]
        self.__scope_position = const.SETTLEMENT_INITIAL_POSITION
        self.__scope_target_index: int = 0  # The index of target team
        self.__scope_target_position = pg.Vector2 | tuple[float, float]
        self.__team_position = const.SETTLEMENT_TEAM_POSITION
        self.__scope_speed: int = const.SCOPE_SPEED

    def ranking(self):
        model = get_model()
        self.__rank_of_teams = sorted(model.teams, key=lambda team: team.points)

    def update(self) -> bool:
        if self.__scope_target_index >= self.__number_of_teams:
            return True

        displacement = (self.set_target() - self.__scope_position).normalize()*self.__scope_speed
        self.__scope_position += displacement
        return True

    def set_target(self) -> pg.Vector2:
        target_team: Team = self.__rank_of_teams[self.__scope_target_index]

        if self.__scope_position == self.__team_position[target_team.team_id]:
            self.__scope_target_index += 1

        target_team = self.__rank_of_teams[self.__scope_target_index]
        return self.__team_position[target_team.team_id]

    @property
    def scope_position(self) -> pg.Vector2:
        return self.__scope_position
