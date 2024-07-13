import random
from math import cos, pi, sin

import pygame as pg

import const
from event_manager import EventChangeParty, EventStartGame
from instances_manager import get_event_manager, get_model
from model.team import Team
from model.timer import Timer


class Settlement:

    def __init__(self, number_of_teams: int):
        self.__number_of_teams: int = number_of_teams
        self.__rank_of_teams: list = [Team]
        self.__scope_position = const.SETTLEMENT_INITIAL_POSITION
        self.__scope_target_index: int = -1  # The index of target team
        self.__scope_target_position: pg.Vector2 | tuple[float,
                                                         float] = const.SETTLEMENT_INITIAL_POSITION
        self.__team_position = const.SETTLEMENT_TEAM_POSITION
        self.__scope_speed: int = const.SCOPE_SPEED
        self.__scope_status: const.ScopeStatus = const.ScopeStatus.TOWARD_WANDERING
        self.__parameter_wandering: float = 0

    def ranking(self):
        model = get_model()
        self.__rank_of_teams = sorted(model.teams, key=lambda team: team.points)

    def vector_equal(self, vectorA: pg.Vector2, vectorB: pg.Vector2):
        return (vectorA-vectorB).length() < const.POSITION_EPSILON

    def update(self) -> bool:

        if self.__scope_target_index >= self.__number_of_teams:
            return

        if self.__scope_waiting:
            pass
        elif self.__scope_wandering:
            pass
        elif self.vector_equal(self.__scope_target_position, self.__scope_position):
            Timer(interval=const.INVERVAL_WAITING, function=self.set_wandering, once=True)

        self.set_target()
        displacement = (self.__scope_target_position - self.__scope_position).normalize()*self.__scope_speed if (self.__scope_target_position -
                                                                                                                 self.__scope_position).length() > self.__scope_speed else (self.__scope_target_position - self.__scope_position)
        self.__scope_position += displacement

    def set_target(self):

        if not self.__scope_wandering:
            target_team: Team = self.__rank_of_teams[self.__scope_target_index]
            self.__scope_target_position = self.__team_position[target_team.team_id]

        else:
            if not self.__scope_waiting:
                self.__parameter_wandering += 2*pi*get_model().dt/const.WANDERING_PERIOD
                self.__scope_target_position = pg.Vector2(
                    100*sin(self.__parameter_wandering)+125, 100*cos(2*self.__parameter_wandering)+125)

    def set_wandering(self):
        self.__scope_wandering = True
        self.__scope_waiting = True
        self.__scope_target_index += 1
        self.__parameter_wandering = 0
        Timer(interval=const.INVERVAL_WANDERING, function=self.set_not_wandering, once=True)

    def set_not_wandering(self):
        self.__scope_wandering = False

    @property
    def scope_position(self) -> pg.Vector2:
        return self.__scope_position
