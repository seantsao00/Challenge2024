"""
The program's entry point is the main function in this module.

Import paths should be relative to the location of this file.
"""

import argparse
import faulthandler
import pygame as pg

import instances_manager
from controller import Controller
from event_manager import EventManager
from model import Model
from music.music import BackgroundMusic
from util import set_verbosity
from view import View


def main():
    # Initialization
    pg.init()
    faulthandler.enable()
    # Argument parser
    parser = argparse.ArgumentParser(prog='Challenge2024')
    parser.add_argument(
        'map', help='The name of maps. It can be test_map'
    )
    parser.add_argument(
        'team_control', nargs='+', help='assign ai to teams or "human" if the team is controlled by human.'
    )

    parser.add_argument('-r', '--range', action='store_true',
                        help='Shorthand of --show-view-range --show-attack-range')
    parser.add_argument('--show-view-range', action='store_true',
                        help='Showing the view range of all entities')
    parser.add_argument('--show-attack-range', action='store_true',
                        help='Showing the attack range of all entities')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='Increase verbosity (can be used multiple times).')
    parser.add_argument('-m', '--music', action='store_true', help='play the BGM')

    args = parser.parse_args()
    set_verbosity(args.verbose)

    teams: list[str] = args.team_control

    ev_manager = EventManager()
    instances_manager.register_event_manager(ev_manager)

    model = Model(args.map, teams,
                  args.show_view_range or args.range, args.show_attack_range or args.range)
    instances_manager.register_model(model)

    Controller()
    View()

    if args.music:
        BackgroundMusic()

    # Main loop
    model.run()


if __name__ == "__main__":
    main()
