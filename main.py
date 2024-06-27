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

    # Argument parser
    parser = argparse.ArgumentParser(prog='Challenge2023')
    parser.add_argument(
        'map', help='The name of maps. It can be single_map or test_map'
    )
    parser.add_argument(
        'team1', help='team1 Use "human" if this team is controlled by human.'
    )
    # parser.add_argument(
    #     'team2', help='team2'
    # )
    # parser.add_argument(
    #     'team3', help='team3'
    # )
    # parser.add_argument(
    #     'team4', help='team4'
    # )
    # Here is WIP

    parser.add_argument('-v', '--show-view-range', action='store_true',
                        help='If added, the view range of entities will be shown')
    parser.add_argument('-a', '--show-attack-range', action='store_true',
                        help='If added, the attack range of entities will be shown')

    args = parser.parse_args()
    teams = [args.team1]

    ev_manager = EventManager()
    instances_manager.register_event_manager(ev_manager)

    model = Model(args.map, teams,
                  args.show_view_range, args.show_attack_range)
    instances_manager.register_model(model)

    Controller()
    View()

    # Main loop
    model.run()


if __name__ == "__main__":
    main()
