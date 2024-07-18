import pygame as pg

from instances_manager import get_model
from view.screen_info import ScreenInfo


class Particle:
    def __init__(self, canvas: pg.Surface, position: pg.Vector2, actual_position: pg.Vector2, direction: pg.Vector2,
                 speed: float, size: float, duration: float, color: pg.Color):

        self.position = position
        self.__canvas = canvas
        self.__actual_position = actual_position
        self.__direction = direction
        self.__speed = speed
        self.__size = size
        self.__color = color
        self.__duration = duration
        self.__elapsed_time: float = 0.0

        self.dead = False

    def draw(self):
        pg.draw.circle(self.__canvas, self.__color, self.__actual_position,
                       self.__size * ScreenInfo.resize_ratio)

    def move(self):
        dt = get_model().dt
        self.__actual_position += self.__direction * self.__speed * dt
        self.__elapsed_time += dt

        if self.__elapsed_time >= self.__duration:
            self.dead = True
