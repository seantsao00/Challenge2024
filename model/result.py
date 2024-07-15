from math import pi
from random import getrandbits

import pygame as pg

import const
import const.result
from event_manager.events import EventResultChamp, EventResultChoseCharacter, EventResultWandering
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
        self.__final_wandering_parameter: bool = const.is_final_wandering(number_of_teams)
        self.__champion_runnerup_position: pg.Vector2 = None
        self.__champion_runnerup_used: bool = False

    def ranking(self):
        model = get_model()
        self.__rank_of_teams = sorted(model.teams, key=lambda team: team.points)
        if self.__final_wandering_parameter:
            if bool(getrandbits(1)):
                target: Team = self.__rank_of_teams[self.__number_of_teams - 1]
            else:
                target: Team = self.__rank_of_teams[self.__number_of_teams - 2]
            self.__champion_runnerup_position = (self.__team_position[target.team_id]
                                                 + const.WANDERING_SHIFT)

    def arrived(self) -> bool:
        return (self.__scope_target_position - self.__scope_position).length() < const.POSITION_EPSILON

    def update(self):
        if self.__scope_status is const.ScopeStatus.FINISH:
            if self.arrived():
                return
        elif self.__scope_status is const.ScopeStatus.WANDERING:
            self.__scope_target_position = const.wandering_formula(self.__parameter_wandering)
            self.__parameter_wandering += 2 * pi * get_model().dt / const.WANDERING_PERIOD
        elif self.__scope_status is const.ScopeStatus.TOWARD_WANDERING:
            if self.arrived():
                self.__scope_status = const.ScopeStatus.WANDERING
                Timer(interval=const.interval_wandering(),
                      function=self.set_toward_target, once=True)
        elif self.__scope_status is const.ScopeStatus.WAITING:
            pass
        elif self.__scope_status is const.ScopeStatus.TOWARD_TARGET:
            if self.arrived():
                if self.__scope_target_index + 1 == self.__number_of_teams:
                    get_event_manager().post(EventResultChamp())
                else:
                    get_event_manager().post(EventResultChoseCharacter())
                self.__scope_status = const.ScopeStatus.WAITING
                self.__scope_target_index += 1
                Timer(interval=const.INTERVAL_WAITING,
                      function=self.set_toward_wandering, music=True, once=True)
        elif self.__scope_status is const.ScopeStatus.FINAL_WANDERING:
            if self.arrived():
                self.set_toward_wandering(False)

        displacement = self.__scope_target_position - self.__scope_position
        if displacement.length() > 0:
            self.__scope_position += displacement.clamp_magnitude(
                self.__scope_speed * get_model().dt)

    def set_toward_wandering(self, music: bool):
        if self.__scope_target_index >= self.__number_of_teams:
            self.__scope_status = const.ScopeStatus.FINISH
            self.__scope_target_position = const.RESULT_FINAL_POSITION
            return
        if self.__scope_target_index + 1 == self.__number_of_teams:
            self.__scope_status = const.ScopeStatus.TOWARD_TARGET
            target_team: Team = self.__rank_of_teams[self.__scope_target_index]
            self.__scope_target_position = self.__team_position[target_team.team_id]
            return
        if music:
            get_event_manager().post(EventResultWandering())
        self.__scope_status = const.ScopeStatus.TOWARD_WANDERING
        self.__parameter_wandering = 0
        self.__scope_target_position = const.wandering_formula(self.__parameter_wandering)

    def set_toward_target(self):
        if self.__scope_target_index + 2 == self.__number_of_teams and self.__final_wandering_parameter and not self.__champion_runnerup_used:
            self.__champion_runnerup_used = True
            self.__scope_status = const.ScopeStatus.FINAL_WANDERING
            self.__scope_target_position = self.__champion_runnerup_position
        else:
            self.__scope_status = const.ScopeStatus.TOWARD_TARGET
            target_team: Team = self.__rank_of_teams[self.__scope_target_index]
            self.__scope_target_position = self.__team_position[target_team.team_id]

    def handle_scopemoving_start(self):
        if self.__scope_status is const.ScopeStatus.WAITING_INPUT:
            self.set_toward_wandering(True)

    @property
    def scope_position(self) -> pg.Vector2:
        return self.__scope_position

    def number_of_teams(self) -> int:
        return self.__number_of_teams
