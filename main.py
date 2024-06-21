"""
The program's entry point is the main function in this module.

Import paths should be relative to the location of this file.
"""

import argparse

import pygame as pg

import const
import instances_manager
from controller import Controller
from event_manager import EventManager
from model import Model
from model.entity import Entity
from view import View


def main():
    # Initialization
    pg.init()

    # Reset Window/Arena Size, maximum 16 : 9 in current screen
    size = pg.display.Info()
    print(size.current_w, size.current_h)
    window_w = min(size.current_w, size.current_h / 9 * 16)
    window_h = min(size.current_h, size.current_w / 16 * 9)
    const.WINDOW_SIZE = (window_w, window_h)
    const.ARENA_SIZE = (window_h, window_h)

    # Argument parser
    parser = argparse.ArgumentParser(prog='Challenge2023')
    args = parser.parse_args()

    ev_manager = EventManager()
    instances_manager.register_event_manager(ev_manager)

    model = Model()
    instances_manager.register_model(model)

    Controller()
    View()

    

    # Main loop
    model.run()


if __name__ == "__main__":
    main()
