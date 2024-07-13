import pygame as pg

import const
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
        self.__team_stats = self.__team.stats
        self.__team_name_surface = self.font_primary.render(
            f"{self.__team.team_name}", False, 'black')
        self.__team_avatar = components.createTeamAvatar(
            self.__team, int(SI.scale(SCOREBOX_AVATAR_SIZE)))
        self.__team_towers_count: int = 0
        self.__position_x = initial_position[0]
        self.__position_y = LinearAnimation(
            initial_position[1], SCOREBOX_ANIMATION_DURATION)

    def draw(self, canvas: pg.Surface):
        self.__canvas.fill(pg.Color(0, 0, 0, 0))
        # avatar
        self.__canvas.blit(self.__team_avatar, self.__team_avatar.get_rect(
            midleft=SI.scale((3, 12))))
        # team name
        team_name_rect = self.__team_name_surface.get_rect(
            bottomright=(SI.scale((SCOREBOX_WIDTH - 5, 12))))

        def offset(p): return (p[0], p[1] + self.font_primary.get_descent())
        pg.draw.line(self.__canvas, const.HEALTH_BAR_COLOR[self.__team.team_id], offset(
            team_name_rect.bottomleft), offset(team_name_rect.bottomright), width=8)
        self.__canvas.blit(self.__team_name_surface, team_name_rect)
        # score
        score_text = self.font_primary.render(f"{int(self.__team_stats.score)}", False, 'black')
        score_rect = score_text.get_rect(topright=(SI.scale((SCOREBOX_WIDTH - 5, 12))))
        self.__canvas.blit(score_text, score_rect)
        # show towers owned
        tower_icon = components.createIcon(
            SCOREBOX_ICON_NEUTRALTOWER, SI.scale(SCOREBOX_ICON_SIZE))
        midright = score_rect.midleft
        midright = (midright[0] - SI.scale(2), midright[1])
        for _ in range(self.__team_towers_count):
            self.__canvas.blit(tower_icon, tower_icon.get_rect(midright=midright))
            midright = (midright[0] - SI.scale(4), midright[1])

        def blitIconAndText(icon_name: str, text_string: str, bottomleft: list[float, float], width: float):
            icon = components.createIcon(icon_name, SI.scale(SCOREBOX_ICON_SIZE))
            text = self.font_secondary.render(text_string, True, 'black')
            height = max(icon.get_size()[1], text.get_size()[1])
            self.__canvas.blit(icon, icon.get_rect(
                midleft=(bottomleft[0], bottomleft[1] - height / 2)))
            self.__canvas.blit(text, text.get_rect(
                center=(bottomleft[0] + icon.get_size()[0] / 2 + width / 2, bottomleft[1] - height / 2)))
        field_width = SI.scale(SCOREBOX_WIDTH / 3)
        # unit count
        bottomleft = SI.scale([0, SCOREBOX_HEIGHT])
        blitIconAndText(SCOREBOX_ICON_UNIT, str(
            self.__team_stats.units_alive), bottomleft, field_width)
        # kill count
        bottomleft[0] += field_width
        blitIconAndText(SCOREBOX_ICON_KILL, str(
            self.__team_stats.units_killed), bottomleft, field_width)
        # dead count
        bottomleft[0] += field_width
        blitIconAndText(SCOREBOX_ICON_DEAD, str(
            self.__team_stats.units_dead), bottomleft, field_width)

        # actually draw the box onto the screen
        position = (self.__position_x, self.__position_y.value)
        canvas.blit(self.__canvas, SI.scale(position))

    def update(self, position: tuple[float, float]):
        self.__team_stats = self.__team.stats
        self.__team_towers_count = len(self.__team.towers)
        if self.__team.fountain is not None:
            self.__team_towers_count -= 1
        self.__position_y.value = position[1]

    def cur_score(self):
        return self.__team_stats.score

    def get_team(self):
        return self.__team


class ScoreboardView(ObjectBase):
    def __init__(self, canvas: pg.Surface):
        super().__init__(canvas, [8])
        self.__initialized = False
        self.__canvas = canvas
        self.__team_count: int = 0
        self.__box_positions: list[int] = []
        self.__boxes: list[Scorebox] = []

    def initialize(self):
        if self.__initialized:
            return
        self.__team_count = len(get_model().teams)
        cur_y = SCOREBOX_POSITION[1]
        for _ in range(self.__team_count):
            self.__box_positions.append((SCOREBOX_POSITION[0], cur_y))
            cur_y += SCOREBOX_HEIGHT + SCOREBOX_SPACING
        for i in range(self.__team_count):
            self.__boxes.append(Scorebox(get_model().teams[i], self.__box_positions[i]))
        self.__initialized = True

    def draw(self):
        self.initialize()
        for box in self.__boxes:
            box.draw(self.__canvas)

    def update(self):
        self.initialize()
        self.__boxes.sort(key=lambda box: box.cur_score(), reverse=True)
        for i in range(self.__team_count):
            self.__boxes[i].update(self.__box_positions[i])
