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
        self.__canvas.fill(pg.Color(0, 0, 0, 0))
        # avatar
        self.__canvas.blit(self.__team_avatar, self.__team_avatar.get_rect(
            midleft=SI.scale((3, 12))))
        # team name
        self.__canvas.blit(
            self.__team_name_surface,
            self.__team_name_surface.get_rect(bottomright=(SI.scale((SCOREBOX_WIDTH - 5, 12))))
        )
        # score
        score_text = self.font_primary.render(f"{self.__team_score + 1000:.2f}", False, 'black')
        self.__canvas.blit(
            score_text,
            score_text.get_rect(topright=(SI.scale((SCOREBOX_WIDTH - 5, 12))))
        )

        def blitIconAndText(icon_name: str, text_string: str, bottomleft: list[float, float]):
            icon = components.createIcon(icon_name, SI.scale(SCOREBOX_ICON_SIZE))
            text = self.font_secondary.render(text_string, True, 'black')
            height = max(icon.get_size()[1], text.get_size()[1])
            midleft = [bottomleft[0], bottomleft[1] - height / 2]
            self.__canvas.blit(icon, icon.get_rect(midleft=midleft))
            midleft[0] += icon.get_size()[0] + SI.scale(1)
            self.__canvas.blit(text, text.get_rect(midleft=midleft))

        # unit count
        bottomleft = SI.scale([0, SCOREBOX_HEIGHT])
        blitIconAndText(SCOREBOX_ICON_UNIT, "114", bottomleft)
        # kill count
        bottomleft[0] += SI.scale(SCOREBOX_WIDTH / 3)
        blitIconAndText(SCOREBOX_ICON_KILL, "514", bottomleft)
        # dead count
        bottomleft[0] += SI.scale(SCOREBOX_WIDTH / 3)
        blitIconAndText(SCOREBOX_ICON_DEAD, "888", bottomleft)

        position = (self.__position_x, self.__position_y.value)
        canvas.blit(self.__canvas, SI.scale(position))

    def update(self, position_y: float):
        self.__team_score = self.__team.points
        self.__position_y.value = position_y

    def cur_score(self):
        return self.__team_score

    def get_team(self):
        return self.__team


class ScoreboxesView(ObjectBase):
    def __init__(self, canvas: pg.Surface):
        super().__init__(canvas, [8])
        self.__initialized = False
        self.__canvas = canvas
        self.__boxes: list[Scorebox] = []

    def initialize(self):
        if self.__initialized:
            return
        cur_y = SCOREBOX_POSITION[1]
        for team in get_model().teams:
            self.__boxes.append(
                Scorebox(team, (SCOREBOX_POSITION[0], cur_y)))
            cur_y += SCOREBOX_HEIGHT + SCOREBOX_SPACING
        self.__boxes[0].has_tower = True
        self.__initialized = True

    def draw(self):
        self.initialize()

        # fake update: another team gets the tower
        import random
        if random.randint(1, 50) == 1:
            for box in self.__boxes:
                box.has_tower = False
            teamid = random.randint(0, len(self.__boxes) - 1)
            self.__boxes[teamid].has_tower = True

        for box in self.__boxes:
            box.draw(self.__canvas)

    def update(self):
        self.initialize()

        # fake update: random team gets 10 points
        import random
        if random.randint(1, 50) == 1:
            teamid = random.randint(0, len(self.__boxes) - 1)
            for _ in range(10):
                self.__boxes[teamid].get_team().gain_point_kill()

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
