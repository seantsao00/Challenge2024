import pygame as pg

from view.object.object_base import ObjectBase
from instances_manager import get_event_manager, get_model
import const.const as const
import model.player
from util import crop_image


class Player(ObjectBase):
    images: dict[const.PlayerIds, dict[const.PlayerSpeeds, pg.Surface]] = {
        player: {
            state: None for state in const.PlayerSpeeds
        } for player in const.PlayerIds
    }
    """
    The static dict that stores player images.

    This dict is shared among all Player instances and 
    initialized only once in init_convert.
    """

    def __init__(self, player: model.player.Player):
        super().__init__()
        self.player = player
        self.position = self.player.position.copy()

    @classmethod
    def init_convert(cls):
        for player in const.PlayerIds:
            for state in const.PlayerSpeeds:
                path = (
                    const.IMAGE_PATH
                    + const.PLAYER_IMAGE_PATH[player]
                    + const.PLAYER_IMAGE_PATH[state]
                )
                img = pg.image.load(path)
                width = const.PLAYER_RADIUS * 2
                height = const.PLAYER_RADIUS * 2
                cls.images[player][state] = crop_image(
                    img, width, height
                ).convert_alpha()
                # print(f'{width}, {height}')
        cls.image_initialized = True

    def draw(self, screen: pg.Surface):
        player = self.player

        if player.running:
            img = self.images[player.id][const.PlayerSpeeds.RUN]
        else:
            img = self.images[player.id][const.PlayerSpeeds.WALK]
        screen.blit(img, img.get_rect(midbottom=(player.position)))
