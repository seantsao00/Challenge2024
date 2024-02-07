import argparse

import pygame as pg

import const
import event_manager.events
import instances_manager
from controller.controller import Controller
from event_manager.event_manager import EventManager
from model.model import Model
from view import view


def main():
    # Initialization
    pg.init()

    # Argument parser
    parser = argparse.ArgumentParser(prog='Challenge2023')
    args = parser.parse_args()

    ev_manager = EventManager()
    instances_manager.register_event_manager(ev_manager)

    model = Model()
    instances_manager.register_model(model)

    Controller()
    view()

    # Main loop
    model.run()


if __name__ == "__main__":
    main()
