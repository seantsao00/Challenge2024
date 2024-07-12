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


def check_input_validity(received_args) -> bool:
    team_controls = received_args.team_controls
    game_map = received_args.map

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
    # import faulthandler
    # faulthandler.enable()

    # Argument parser
    parser = argparse.ArgumentParser(prog='Challenge2024')
    parser.add_argument('map',
                        help='Specify the map name from the topography/ directory, e.g., "ruins".')
    parser.add_argument('team_controls', nargs='+',
                        help='List who controls the teams: AI names from the ai/ directory or '
                             '"human" for player-controlled teams. Accepts 1 to 4 entries.')
    parser.add_argument('--show-view-range', action='store_true',
                        help='Displays the viewing range of all characters and towers.')
    parser.add_argument('--show-attack-range', action='store_true',
                        help='Displays the attack range of all characters and towers.')
    parser.add_argument('-r', '--show-attack-view-range', action='store_true',
                        help='Shorthand of combination of --show-view-range and --show-attack-range.')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='Controls verbosity: 0 for critical messages, 1 for warnings, '
                             '2 for informational messages.')
    parser.add_argument('-m', '--mute', action='store_true',
                        help='Mute all background music and sound effects.')
    parser.add_argument('-q', '--skip-character-selecting', action='store_true',
                        help='Skip character selection and randomly assign characters to teams '
                             'for quick test.')

    args = parser.parse_args()

    if not check_input_validity(args):
        sys.exit()
    set_verbosity(args.verbose)
    pg.init()

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
