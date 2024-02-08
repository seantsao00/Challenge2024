from const.model import FPS
from enum import Enum, IntEnum, auto

PLAYER_RADIUS = 30


class PlayerIds(IntEnum):
    def __str__(self):
        return f"{self.name}"

    PLAYER0 = 0


class PlayerSpeeds(IntEnum):
    WALK = 80 / FPS
    RUN = 120 / FPS


# image path

PLAYER_IMAGE_PATH = {
    PlayerIds.PLAYER0: "player/player0/",
    PlayerSpeeds.WALK: "walk.png",
    PlayerSpeeds.RUN: "run.png",
}
