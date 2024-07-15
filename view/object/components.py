"""
Different components on scoreboard and chat.
Moved here for reusability & keep scorebox/chat modules clean.
"""

import pygame as pg

import const.character
import const.team
import const.tower
from model.team import Team
from view.textutil import draw_text, split_text

_cache_avatar_img: dict[const.team.PartyType, pg.Surface] = {}
_cache_avatar: dict[tuple[int, int], pg.Surface] = {}


def _getAvatarImage(party: const.team.PartyType):
    if party in _cache_avatar_img:
        return _cache_avatar_img[party]

    if (party is const.team.PartyType.JUNIOR) or (party is const.team.PartyType.FBI):
        avatar_img = pg.image.load(
            const.ENTITY_IMAGE[party][const.character.CharacterType.SNIPER][const.CharacterState.LEFT])
    elif party is const.team.PartyType.POLICE:
        avatar_img = pg.image.load(
            const.ENTITY_IMAGE[party][const.character.CharacterType.MELEE][const.CharacterState.LEFT])
    else:
        avatar_img = pg.image.load(
            const.ENTITY_IMAGE[party][const.character.CharacterType.RANGER][const.CharacterState.LEFT])

    _cache_avatar_img[party] = avatar_img
    return avatar_img


def _getTeamAvatar(team: Team, size: int):
    if (team, size) in _cache_avatar:
        return _cache_avatar[(team, size)]

    avatar_img = _getAvatarImage(team.party)
    avatar = pg.Surface((size, size), pg.SRCALPHA)

    # resize and crop unwanted parts
    ratio = size / avatar_img.get_width()
    dim = avatar_img.get_size()
    # if party is JUNIOR, zoom in slightly
    if team.party == const.PartyType.JUNIOR:
        dim = (dim[0] * ratio, dim[1] * ratio - 2.5)
    else:
        dim = (dim[0] * ratio, dim[1] * ratio)
    avatar_img = pg.transform.scale(avatar_img, dim)
    avatar.blit(avatar_img, (0, 0))

    # create a round mask to make the avatar a circle
    rect_mask = pg.Surface((size, size), pg.SRCALPHA)
    pg.draw.rect(rect_mask, (255, 255, 255), (0, 0, size, size), border_radius=(size // 4))
    avatar = avatar.copy().convert_alpha()
    avatar.blit(rect_mask, (0, 0), None, pg.BLEND_RGBA_MIN)

    _cache_avatar[(team, size)] = avatar
    return avatar


def createTeamAvatar(team: Team, size: int) -> pg.Surface:
    if not isinstance(size, int):
        raise ValueError("Avatar size must be a ineteger")
    return _getTeamAvatar(team, size)


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


_cache_icon_img: dict[str, pg.Surface] = {}
_cache_icon: dict[tuple[str, float], pg.Surface] = {}


def _getIconImage(file_path: str):
    if file_path in _cache_icon_img:
        return _cache_icon_img[file_path]
    img = pg.image.load(file_path)
    _cache_icon_img[file_path] = img
    return img


def _getIcon(file_path: str, icon_height: float):
    if (file_path, icon_height) in _cache_icon:
        return _cache_icon[(file_path, icon_height)]
    img = _getIconImage(file_path)
    w, h = img.get_size()
    ratio = icon_height / h
    icon = pg.transform.scale(img, (w * ratio, h * ratio))
    _cache_icon[(file_path, icon_height)] = icon
    return icon


def createIcon(file_path: str, icon_height: float) -> pg.Surface:
    """
    Load and scale an icon to specified height
    """
    return _getIcon(file_path, icon_height)
