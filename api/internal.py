import os
import signal
import threading
import traceback

import pygame as pg

import api.api as api
import model
from const import PlayerIds, FPS, MAX_TEAMS
from instances_manager import get_model

__model = get_model()


class Internal(api.API):
    def __init__(self, player_id: int):
        self.player_id = player_id

    def __team(self):
        return __model.teams[self.player_id - 1]

    def get_time():
        return __model.clock.tick() * 1000

    def get_characters(self) -> list[api.Character]:
        raise NotImplementedError

    def get_towers(self) -> list[api.Tower]:
        raise NotImplementedError

    def get_team_id(self) -> int:
        # Cast to prevent modification
        return self.__team().id

    def get_score(self, index=0) -> int:
        if not isinstance(index, int):
            raise TypeError("Team index must be type int.")
        if index == 0:
            index = self.player_id
        if index < 1 or MAX_TEAMS:
            raise IndexError
        team = __model.teams[index - 1]
        # Should be correct, if model implementation changes this should fail
        assert team.id == index
        return team.points


class Timer():
    def __init__(self):
        if os.name == 'nt':
            self.is_windows = True
        elif os.name == 'posix':
            self.is_windows = False
        else:  # os.name == 'java' or unknown
            raise OSError

        if not self.is_windows:
            def handler(sig, frame):
                raise TimeoutError()

            signal.signal(signal.SIGALRM, handler)
        self.timer = None
        self.for_player_id = None

    def set_timer(self, interval: float, player_id: int):
        if not self.is_windows:
            signal.setitimer(signal.ITIMER_REAL, interval)
        else:
            def timeout_alarm(player_id: int):
                print(f"The AI of player {player_id} time out!")

            self.timer = threading.Timer(interval=interval, function=timeout_alarm,
                                         args=[player_id])
            self.timer.start()

    def cancel_timer(self):
        try:
            if not self.is_windows:
                signal.setitimer(signal.ITIMER_REAL, 0)
            else:
                self.timer.cancel()
        except:
            print("Perhaps some very slightly timeout.")


helpers = [Internal(i) for i in range(MAX_TEAMS)]
ai = [None] * len(helpers)
timer = Timer()


def init_ai(files):
    raise NotImplementedError


def call_ai(player_id):
    if ai[player_id] is None:
        return

    try:
        timer.set_timer(1 / (4 * FPS), player_id)
        ai[player_id].player_tick()
    except Exception as e:
        print(f"Caught exception in AI of {player_id}:")
        print(traceback.format_exc())
        return
    finally:
        timer.cancel_timer()
