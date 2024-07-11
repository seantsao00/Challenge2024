import time

import pygame as pg

import api.prototype as api
from util import log_info

log_info("AI axis: test whether the transformed axis is working properly.")

st = None


def every_tick(api: api.API):
    global st
    owned = api.get_owned_characters()

    if len(owned) > 0 and st == None:
        st = time.time()

    if st is not None and time.time() - st > 2 and len(owned) > 2:
        api.action_move_along([owned[1]],
                              pg.Vector2(0, 1))
    elif len(owned) >= 1:
        api.action_move_along([owned[0]],
                              pg.Vector2(1, 0))
