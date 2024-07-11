import pygame as pg

import const
from const.character import CharacterType
from model.team import Team


def createTeamAvatar(team: Team, size: int):
    if not isinstance(size, int):
        raise ValueError("Avatar size must be a ineteger")

    party = team.party
    avatar_img = pg.image.load(const.ENTITY_IMAGE[party][CharacterType.RANGER][None])
    avatar = pg.Surface((size, size), pg.SRCALPHA)

    # resize and crop unwanted parts
    ratio = size / avatar_img.get_width()
    dim = avatar_img.get_size()
    dim = (dim[0] * ratio, dim[1] * ratio)
    avatar_img = pg.transform.scale(avatar_img, dim)
    avatar.blit(avatar_img, (0, 0))

    # create a round mask to make the avatar a circle
    rect_mask = pg.Surface((size, size), pg.SRCALPHA)
    pg.draw.rect(rect_mask, (255, 255, 255), (0, 0, size, size), border_radius=(size // 4))
    avatar = avatar.copy().convert_alpha()
    avatar.blit(rect_mask, (0, 0), None, pg.BLEND_RGBA_MIN)

    return avatar
