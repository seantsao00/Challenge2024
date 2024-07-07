"""
The program's entry point is the main function in this module.

Import paths should be relative to the location of this file.
"""

import argparse

import pygame as pg

import instances_manager
from controller import Controller
from event_manager import EventManager
from model import Model
from view import View


def main():
    # Initialization
    pg.init()

    # Argument parser
    parser = argparse.ArgumentParser(prog='Challenge2024')
    parser.add_argument(
        'map', help='The name of maps. It can be test_map'
    )
    parser.add_argument(
        'team_control', nargs='+', help='assign ai to teams or "human" if the team is controlled by human.'
    )

    parser.add_argument('-v', '--show-view-range', action='store_true',
                        help='If added, the view range of entities will be shown')
    parser.add_argument('-a', '--show-attack-range', action='store_true',
                        help='If added, the attack range of entities will be shown')
    parser.add_argument('--vision-of', default='all',
                        help='Display the vision of which player. If not assigned or assigned "all", all visible entities are displayed. Team id or team name can be assigned.')

    args = parser.parse_args()
    teams: list[str] = args.team_control

    ev_manager = EventManager()
    instances_manager.register_event_manager(ev_manager)

    model = Model(args.map, teams,
                  args.show_view_range, args.show_attack_range)
    instances_manager.register_model(model)

    Controller()
    View(args.vision_of)

    # Main loop
    model.run()


if __name__ == "__main__":
    main()
