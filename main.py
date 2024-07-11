"""
The program's entry point is the main function in this module.

Import paths should be relative to the location of this file.
"""

import os

# pylint: disable=wrong-import-position
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # nopep8

import argparse

import pygame as pg

import instances_manager
from controller import Controller
from event_manager import EventManager
from model import Model, ModelArguments
from music.music import BackgroundMusic
from util import set_verbosity
from view import View

# import faulthandler


def main():
    # Initialization
    pg.init()
    # faulthandler.enable()
    # Argument parser
    parser = argparse.ArgumentParser(prog='Challenge2024')
    parser.add_argument(
        'map', help='The name of maps. It can be test_map'
    )
    parser.add_argument(
        'team_controls', nargs='+', help='assign ai to teams or "human" if the team is controlled by human.'
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
    parser.add_argument('-q', '--skip-character-selection', action='store_true',
                        help='skip the character selection and quick start')

    args = parser.parse_args()
    set_verbosity(args.verbose)

    ev_manager = EventManager()
    instances_manager.register_event_manager(ev_manager)

    model = Model(ModelArguments(
        topography=args.map,
        team_controls=args.team_controls,
        show_view_range=args.show_view_range or args.range,
        show_attack_range=args.show_attack_range or args.range,
        skip_character_selection=args.skip_character_selection
    ))
    instances_manager.register_model(model)

    Controller()
    View()

    if args.music:
        BackgroundMusic()

    # Main loop
    model.run()


if __name__ == "__main__":
    main()
