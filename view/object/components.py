import pygame as pg

import const.character
import const.team
import const.tower
from model.team import Team
from view.textutil import draw_text, split_text


def createTeamAvatar(team: Team, size: int) -> pg.Surface:
    if not isinstance(size, int):
        raise ValueError("Avatar size must be a ineteger")

    party = team.party
    if const.character.CharacterType.RANGER in const.ENTITY_IMAGE[party]:
        avatar_img = pg.image.load(
            const.ENTITY_IMAGE[party][const.character.CharacterType.RANGER][None])
    else:
        avatar_img = pg.image.load(
            const.ENTITY_IMAGE[const.team.PartyType.NEUTRAL][const.tower.TowerType.PYLON][None])
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


def createTextBox(text: str, color: pg.Color, font: pg.font.Font, width: float) -> pg.Surface:
    line_height = font.get_linesize()
    lines = split_text(text, font, width)
    height = line_height * len(lines)
    textbox = pg.Surface((width, height), pg.SRCALPHA)
    cur_y = line_height / 2
    for ln in lines:
        draw_text(textbox, 0, cur_y, ln, color, font, align_text='midleft')
        cur_y += line_height
    return textbox
