import pygame as pg

from const.visual.scorebox import *
from instances_manager import get_model
from model.team import Team
from view.object import components
from view.object.animation import LinearAnimation
from view.object.object_base import ObjectBase
from view.screen_info import ScreenInfo as SI
from view.textutil import font_loader


class Scorebox:

    def __init__(self, team: Team, initial_position: tuple[int, int]):
        self.__canvas = pg.Surface(SI.translate((SCOREBOX_WIDTH, SCOREBOX_HEIGHT)), pg.SRCALPHA)
        self.font_primary = font_loader.get_font(size=SCOREBOX_FONT_SIZE_PRIMARY)
        self.font_secondary = font_loader.get_font(size=SCOREBOX_FONT_SIZE_SECONDARY)
        self.__team = team
        self.__team_score = self.__team.points
        self.__team_name_surface = self.font_primary.render(
            f"Team {self.__team.team_id}", False, 'black')
        self.__team_avatar = components.createTeamAvatar(
            self.__team, int(SI.scale(SCOREBOX_AVATAR_SIZE)))
        self.__position_x = initial_position[0]
        self.__position_y = LinearAnimation(
            initial_position[1], SCOREBOX_ANIMATION_DURATION)
        self.has_tower = False

    def draw(self, canvas: pg.Surface):
        # pg.draw.rect(self.__canvas, pg.color.Color(255, 255, 255, 127),
        #              (*SI.translate((0, 0), position), SI.scale(SCOREBOX_WIDTH), SI.scale(SCOREBOX_HEIGHT)))
        self.__canvas.fill(pg.Color(0, 0, 0, 0))
        # avatar
        self.__canvas.blit(self.__team_avatar, self.__team_avatar.get_rect(
            topright=SI.scale((SCOREBOX_WIDTH, 0))))
        # team name
        self.__canvas.blit(
            self.__team_name_surface,
            self.__team_name_surface.get_rect(
                midleft=SI.scale((0, SCOREBOX_AVATAR_SIZE / 2))
            )
        )
        # score
        score_text = self.font_primary.render(f"10{self.__team_score:.2f}", False, 'black')
        self.__canvas.blit(
            score_text,
            score_text.get_rect(bottomleft=SI.scale((0, SCOREBOX_HEIGHT)))
        )
        # kill count
        kill_icon = pg.image.load(SCOREBOX_ICON_KILL)
        kill_icon = pg.transform.scale(kill_icon, SI.scale((7, 7)))
        self.__canvas.blit(kill_icon, kill_icon.get_rect(
            midright=SI.scale((SCOREBOX_WIDTH, SCOREBOX_HEIGHT - 13.5))))
        kill_text = self.font_secondary.render(f"114", False, 'black')
        self.__canvas.blit(kill_text, kill_text.get_rect(
            bottomright=SI.scale((SCOREBOX_WIDTH - 8, SCOREBOX_HEIGHT - 9))))
        # unit count
        unit_icon = pg.image.load(SCOREBOX_ICON_UNIT)
        unit_icon = pg.transform.scale(unit_icon, SI.scale((7, 7)))
        self.__canvas.blit(unit_icon, unit_icon.get_rect(
            midright=SI.scale((SCOREBOX_WIDTH, SCOREBOX_HEIGHT - 4.5))))
        unit_text = self.font_secondary.render(f"514", False, 'black')
        self.__canvas.blit(unit_text, unit_text.get_rect(
            bottomright=SI.scale((SCOREBOX_WIDTH - 8, SCOREBOX_HEIGHT))))
        # tower icon
        if self.has_tower:
            tower_icon = pg.image.load(SCOREBOX_ICON_NEUTRALTOWER)
            tower_icon = pg.transform.scale(tower_icon, SI.scale((7, 7)))
            self.__canvas.blit(tower_icon, tower_icon.get_rect(
                midleft=SI.scale((0, SCOREBOX_HEIGHT / 2))))

        # text = self.font_secondary.render(f"1234", False, 'black')
        # rect = text.get_rect(bottomright = SI.scale((SCOREBOX_WIDTH, SCOREBOX_HEIGHT)))
        # self.__canvas.blit(text, rect)
        # pg.draw.rect(self.__canvas, 'white', rect, width=1)

        position = (self.__position_x, self.__position_y.value)
        canvas.blit(self.__canvas, SI.scale(position))

    def update(self, position_y: float):
        self.__team_score = self.__team.points
        self.__position_y.value = position_y

    def cur_score(self):
        return self.__team_score


class ScoreboxesView(ObjectBase):
    def __init__(self, canvas: pg.Surface):
        super().__init__(canvas, [8])
        self.__initialized = False
        self.__canvas = canvas
        self.__boxes: list[Scorebox] = []

    def initialize(self):
        cur_y = SCOREBOX_POSITION[1]
        for team in get_model().teams:
            self.__boxes.append(
                Scorebox(team, (SCOREBOX_POSITION[0], cur_y)))
            cur_y += SCOREBOX_HEIGHT + SCOREBOX_SPACING
        self.__boxes[0].has_tower = True

    def draw(self):
        if not self.__initialized:
            self.initialize()
            self.__initialized = True
        import random
        if random.randint(1, 50) == 1:
            for box in self.__boxes:
                box.has_tower = False
            teamid = random.randint(0, len(self.__boxes) - 1)
            self.__boxes[teamid].has_tower = True
        for box in self.__boxes:
            box.draw(self.__canvas)

    def update(self):
        self.__boxes.sort(key=lambda box: box.cur_score(), reverse=True)
        cur_y = SCOREBOX_POSITION[1]
        for box in self.__boxes:
            box.update(cur_y)
            cur_y += SCOREBOX_HEIGHT + SCOREBOX_SPACING


"""
font size / real height / virtual height
2   9    2.34
4   18   4.68
6   27   7.03
8   35   9.11
10  45  11.71
12  54  14.06
14  62  16.14
16  72  18.75
18  81  21.09
20  89  23.17
"""
