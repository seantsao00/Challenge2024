import threading
import traceback
import os
import signal

import pygame as pg

from api.api import API
from const import PlayerIds, FPS
from instances_manager import get_model


class Internal(API):
    def __init__(self, player_id: int):
        self.player_id = player_id

    def get_time():
        return pg.time.get_ticks() * 1000


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


helpers = [Internal(i) for i in PlayerIds]
ai = [None] * len(helpers)
timer = Timer()


def init_ai(files):
    raise NotImplementedError


def call_ai(player_id):
    model = get_model()
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
