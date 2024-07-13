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
        self.__scope_target_index: int = 0  # The index of target team
        self.__scope_target_position = pg.Vector2 | tuple[float, float]
        self.__team_position = const.SETTLEMENT_TEAM_POSITION
        self.__scope_speed: int = const.SCOPE_SPEED
        self.__scope_wandering: bool = False  # if the scope is wandering
        self.__scope_waiting: bool = False  # if the scope is waiting for timer to make it wandering
        self.__parameter_wandering: float = 0
        self.scope_state: const.Settlement_Scope_State = const.Settlement_Scope_State.WAITING_INPUT

    def ranking(self):
        model = get_model()
        self.__rank_of_teams = sorted(model.teams, key=lambda team: team.points)

    def update(self) -> bool:
        if self.scope_state is const.Settlement_Scope_State.WAITING_INPUT:
            pass
        elif self.__scope_position == self.__scope_target_position and self.__scope_target_index >= self.__number_of_teams:
            pass
        elif self.__scope_position == self.__scope_target_position and not self.__scope_waiting:
            self.__scope_target_index += 1
            self.__scope_waiting = True
            Timer(interval=const.INVERVAL_WAITING, function=self.set_wandering, once=True)
        elif self.__scope_position == self.__scope_target_position:
            pass
        else:
            self.set_target()
            displacement = (self.__scope_target_position - self.__scope_position).normalize()*self.__scope_speed if (self.__scope_target_position -
                                                                                                                     self.__scope_position).length() > self.__scope_speed else (self.__scope_target_position - self.__scope_position)
            self.__scope_position += displacement
        return

    def set_target(self):

        if self.__scope_target_index >= self.__number_of_teams:
            self.__scope_target_position = self.__scope_position

        elif not self.__scope_wandering:
            target_team: Team = self.__rank_of_teams[self.__scope_target_index]
            self.__scope_target_position = self.__team_position[target_team.team_id]

        else:
            self.__scope_target_position = pg.Vector2(
                100*sin(self.__parameter_wandering)+100, 100*cos(2*self.__parameter_wandering)+100)
            self.__parameter_wandering += 2*pi*get_model().dt/const.WANDERING_PERIOD

    def set_wandering(self):
        self.__scope_wandering = True
        self.__scope_waiting = False
        self.__parameter_wandering = 0
        self.set_target()
        Timer(interval=const.INVERVAL_WANDERING, function=self.set_not_wandering, once=True)

    def set_not_wandering(self):
        self.__scope_wandering = False

    def handel_scopemoving_start(self):
        self.scope_state = const.Settlement_Scope_State.MOVING

    @property
    def scope_position(self) -> pg.Vector2:
        return self.__scope_position
