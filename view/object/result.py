from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from instances_manager import get_model
from util import crop_image, transform_coordinate
from view.object.object_base import ObjectBase
from view.screen_info import ScreenInfo

if TYPE_CHECKING:
    from model import Result


class ResultView(ObjectBase):
    background_image: pg.Surface
    bottom_image: pg.Surface
    out_image: pg.Surface
    gold_circle_image: pg.Surface
    crown_image: pg.Surface
    party_images_nomal: dict[const.PartyType, pg.Surface] = {}
    party_images_gray: dict[const.PartyType, pg.Surface] = {}
    ratio: float

    def __init__(self, canvas: pg.Surface, result: Result):
        self.image_initialized = True
        super().__init__(canvas, [const.PRIORITY_RESULT])
        self.__result = result
        self.__scope_destination = const.RESULT_TEAM_POSITION
        self.__font = pg.font.Font(const.REGULAR_FONT, int(12 * ScreenInfo.resize_ratio))
        self.__team_out: list[bool] = [False, False, False, False]
        self.__team_rank: list[int] = [10, 10, 10, 10]
        self.__team_index: int = 0
        self.__number_of_teams: int = self.__result.number_of_teams()

    @classmethod
    def init_convert(cls):
        cls.ratio = ScreenInfo.screen_size[1] / 900

        img = pg.image.load(const.RESULT_BOTTOM)
        cls.bottom_image = crop_image(
            img, 348, ScreenInfo.screen_size[1], True).convert_alpha()

        img = pg.image.load(const.RESULT_BACKGROUND)
        cls.background_image = crop_image(
            img, 1260 * cls.ratio, ScreenInfo.screen_size[1], True).convert_alpha()

        img = pg.image.load(const.RESULT_SCOPE)
        cls.scope_image = crop_image(
            img, 360 * cls.ratio, 360 * cls.ratio, True).convert_alpha()

        img = pg.image.load(const.RESULT_OUT)
        cls.out_image = crop_image(
            img, 376 * cls.ratio, 360 * cls.ratio).convert_alpha()

        img = pg.image.load(const.RESULT_GOLDCIRCLE)
        cls.gold_circle_image = crop_image(
            img, 587 * cls.ratio, 512 * cls.ratio).convert_alpha()

        img = pg.image.load(const.RESULT_CROWN)
        cls.crown_image = crop_image(
            img, 101 * cls.ratio, 88 * cls.ratio).convert_alpha()

        for key, path in const.RESULT_IMAGE_NOMAL.items():
            img = pg.image.load(path)
            cls.party_images_nomal[key] = crop_image(
                img, 376 * cls.ratio, 360 * cls.ratio).convert_alpha()

        for key, path in const.RESULT_IMAGE_GRAY.items():
            img = pg.image.load(path)
            cls.party_images_gray[key] = crop_image(
                img, 376 * cls.ratio, 360 * cls.ratio).convert_alpha()

        cls.image_initialized = True

    def draw(self):
        model = get_model()
        img = self.bottom_image
        self.canvas.blit(img, (0, 0))

        team_icon_position: list = [(284, 100), (33, 420), (851, 100), (600, 420)]
        for team in model.teams:
            if self.__result.scope_position == self.__scope_destination[team.team_id] and self.__team_out[team.team_id] == False:
                self.__team_out[team.team_id] = True
                self.__team_index += 1
                self.__team_rank[team.team_id] = self.__team_index

            if self.__team_out[team.team_id] == True and self.__team_rank[team.team_id] < self.__number_of_teams:
                img = self.party_images_gray[team.party]
            else:
                img = self.party_images_nomal[team.party]
            self.canvas.blit(img, transform_coordinate(
                team_icon_position[team.team_id], self.ratio))

        img = self.background_image
        self.canvas.blit(img, (0, 0))

        for team in model.teams:
            if team.team_id < 2:
                draw_text(self.canvas, (team_icon_position[team.team_id][0] + 362 / 2) * self.ratio,
                          (team_icon_position[team.team_id][1]) * self.ratio, f"{team.team_name}", 'white', self.__font)
            else:
                draw_text(self.canvas, (team_icon_position[team.team_id][0] + 380 / 2) * self.ratio,
                          (team_icon_position[team.team_id][1]) * self.ratio, f"{team.team_name}", 'white', self.__font)

            if self.__team_out[team.team_id] == True:
                draw_text(self.canvas, (team_icon_position[team.team_id][0] + 370 / 2) * self.ratio, (
                    team_icon_position[team.team_id][1] + 305) * self.ratio, f"{team.points:.0f}", 'white', self.__font)

                if self.__team_rank[team.team_id] < self.__number_of_teams:
                    img = self.out_image
                    self.canvas.blit(img, transform_coordinate(
                        (team_icon_position[team.team_id][0], team_icon_position[team.team_id][1] + 120), self.ratio))
                elif self.__team_rank[team.team_id] == self.__number_of_teams:
                    img = self.gold_circle_image
                    self.canvas.blit(img, transform_coordinate(
                        (team_icon_position[team.team_id][0] - 102, team_icon_position[team.team_id][1] - 64), self.ratio))
                    img = self.crown_image
                    self.canvas.blit(img, transform_coordinate(
                        (team_icon_position[team.team_id][0] + 200, team_icon_position[team.team_id][1] + 25), self.ratio))

        img = self.scope_image
        self.canvas.blit(img, transform_coordinate(self.__result.scope_position, self.ratio))

        # if self.__party_selector.is_ready():
        #     draw_text(self.canvas, ScreenInfo.screen_size[0] / 2, ScreenInfo.screen_size[1] -
        #               40, 'Press ENTER to continue', 'white', self.__font)


def draw_text(surf: pg.Surface, x: float, y: float, text: str, color, font: pg.Font, underline: bool = False):
    underline_color = 'darkblue'
    underline_thickness = 3
    underline_offset = 3

    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))

    if underline:
        underline_start = (text_rect.left, text_rect.bottom + underline_offset)
        underline_end = (text_rect.right, text_rect.bottom + underline_offset)
        pg.draw.line(surf, underline_color, underline_start, underline_end, underline_thickness)

    surf.blit(text_surface, text_rect.topleft)
