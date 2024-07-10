import time

from api.prototype import *
from util import log_info


def every_tick(api: API):
    print("lets sleep...")
    time.sleep(1)
