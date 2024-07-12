"""
The program's entry point is the main function in this module.

Import paths should be relative to the location of this file.
"""

import os

# pylint: disable=wrong-import-position
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # nopep8

import argparse
import sys

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
    parser.add_argument('-m', '--mute', action='store_true', help='mute the BGM and sound effects')
    parser.add_argument('-q', '--skip-character-selecting', action='store_true',
                        help='automatically randomly select parties for each team')

    args = parser.parse_args()
    if not check_input_validity(args):
        sys.exit()
    set_verbosity(args.verbose)

    ev_manager = EventManager()
    instances_manager.register_event_manager(ev_manager)

    model = Model(ModelArguments(
        topography=args.map,
        team_controls=args.team_controls,
        show_view_range=args.show_view_range or args.range,
        show_attack_range=args.show_attack_range or args.range,
        skip_character_selecting=args.skip_character_selecting
    ))
    instances_manager.register_model(model)

    View()
    Controller()

    if not args.mute:
        BackgroundMusic()

    # Main loop
    model.run()


def check_input_validity(args) -> bool:
    team_controls = args.team_controls
    game_map = args.map

    if len(team_controls) > 4:
        print('Too many teams')
        return False
    if team_controls.count('human') > 1:
        print('At most one human')
        return False
    for team in team_controls:
        if team != 'human' and not os.path.isfile(f'./ai/{team}.py'):
            print(f'{team}.py does not exist')
            return False
    if not os.path.isdir(f'./topography/{game_map}'):
        print(f'{game_map} map does not exist')
        return False

    return True


if __name__ == "__main__":
    main()
