import argparse

import pygame as pg

from event_manager.event_manager import eventManager
from model.model import GameEngine
from controller.controller import Controller
from view.view import GraphicalView

def main():
    # Initialization
    pg.init()

    # Argument parser
    parser = argparse.ArgumentParser(prog='Challenge2023')
    args = parser.parse_args()
    
    # EventManager listen to events and notice model, controller, view
    ev_manager = EventManager()
    model      = GameEngine(ev_manager)
    controller = Controller(ev_manager, model)
    view       = GraphicalView(ev_manager, model)

    # Main loop
    model.run()

if __name__ == "__main__":
    main()