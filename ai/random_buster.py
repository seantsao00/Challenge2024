"""
This AI does nothing but keep resetting seeds.
A thing that is more observable is chat keeps showing the same message (as `random.choice` is begin manipulated.) 
"""

import time
import random

import api.prototype as api

def every_tick(api: api.API):
    t = time.time()
    cnt = 0
    try:
        while time.time() - t < 0.8:
            random.seed(0)
            cnt += 1
    finally:
        print(f"Attempted to reset seed {cnt} time(s).")
