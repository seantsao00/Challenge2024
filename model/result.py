import random
from math import cos, pi, sin

import pygame as pg

import const
import const.result
from event_manager import EventChangeParty, EventStartGame
from instances_manager import get_event_manager, get_model
from model.team import Team
from model.timer import Timer


class Result:

    def __init__(self, number_of_teams: int):
        self.__number_of_teams: int = number_of_teams
        self.__rank_of_teams: list = [Team]
        self.__scope_position = const.RESULT_INITIAL_POSITION
        self.__scope_target_index: int = 0  # The index of target team
        self.__scope_target_position: pg.Vector2 = const.RESULT_INITIAL_POSITION
        self.__team_position: pg.Vector2 = const.RESULT_TEAM_POSITION
        self.__scope_speed: int = const.SCOPE_SPEED
        self.__scope_status: const.ScopeStatus = const.ScopeStatus.WAITING_INPUT
        self.__parameter_wandering: float = 0

    def ranking(self):
        model = get_model()
        self.__rank_of_teams = sorted(model.teams, key=lambda team: team.points)

    def arrived(self) -> bool:
        return (self.__scope_target_position - self.__scope_position).length() < const.POSITION_EPSILON

    def update(self):

        if self.__scope_status is const.ScopeStatus.FINISH:
            if self.arrived():
                return
        elif self.__scope_status is const.ScopeStatus.WANDERING:
            self.__scope_target_position = const.wandering_formula(self.__parameter_wandering)
            self.__parameter_wandering += 2*pi*get_model().dt/const.WANDERING_PERIOD
        elif self.__scope_status is const.ScopeStatus.TOWARD_WANDERING:
            if self.arrived():
                self.__scope_status = const.ScopeStatus.WANDERING
                Timer(interval=const.INVERVAL_WANDERING, function=self.set_toward_target, once=True)
        elif self.__scope_status is const.ScopeStatus.WAITING:
            pass
        elif self.__scope_status is const.ScopeStatus.TOWARD_TARGET:
            if self.arrived():
                self.__scope_status = const.ScopeStatus.WAITING
                self.__scope_target_index += 1
                Timer(interval=const.INVERVAL_WAITING, function=self.set_wandering, once=True)

        displacement = (self.__scope_target_position - self.__scope_position).normalize()*self.__scope_speed if (self.__scope_target_position -
                                                                                                                 self.__scope_position).length() > self.__scope_speed else (self.__scope_target_position - self.__scope_position)
        self.__scope_position += displacement

    def set_wandering(self):
        if self.__scope_target_index >= self.__number_of_teams:
            self.__scope_status = const.ScopeStatus.FINISH
            self.__scope_target_position = const.RESULT_FINAL_POSITION
            return
        self.__scope_status = const.ScopeStatus.WANDERING
        self.__parameter_wandering = 0
        Timer(interval=const.INVERVAL_WANDERING, function=self.set_toward_target, once=True)

    def set_toward_target(self):
        self.__scope_status = const.ScopeStatus.TOWARD_TARGET
        target_team: Team = self.__rank_of_teams[self.__scope_target_index]
        self.__scope_target_position = self.__team_position[target_team.team_id]

    def handle_scopemoving_start(self):
        if self.__scope_status is const.ScopeStatus.WAITING_INPUT:
            self.__scope_status = const.ScopeStatus.TOWARD_WANDERING

    @property
    def scope_position(self) -> pg.Vector2:
        return self.__scope_position
