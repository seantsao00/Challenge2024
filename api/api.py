"""
This file ONLY defines prototype. No actual thing is done in this file.
"""

from enum import IntEnum, auto


class Character:
    """Character used for maniplutaing (prevents direct access to actual character)"""
    pass


class Tower:
    """Tower used for maniplutaing (prevents direct access to actual tower)"""
    pass


class TowerSpawnType(IntEnum):
    """Class for specifing tower spawning character type."""
    melee = auto()
    lookout = auto()
    ranged = auto()
    pass


class API:
    def get_time(self):
        """Return the current in-game time."""
        pass

    def get_characters(self) -> list[Character]:
        """Return the list of character owned by the team."""
        pass

    def get_towers(self) -> list[Tower]:
        """Return the list of tower owned by the team."""
        pass

    def get_team_id(self) -> int:
        """Return current team's `id`."""

    def get_score(self, index=0) -> int:
        """Return the score of team `index`. If `index` is 0, return the current team's score."""
        pass

    def look_characters(self) -> list[Character]:
        """Return the list of charactervisible from the team."""
        pass

    def look_towers(self) -> list[Tower]:
        """Return the list of tower visible from the team."""
        pass

    def look_grid(self) -> list[Tower]:
        """Return a grid of current vision."""
        pass

    def action_move_to(self, characters: list[Character], destination: tuple[float, float]):
        """
        Make all characters in the list move to the destination, using internal A* algorithm.
        This function override previous action.
        """
        pass

    def action_attack(self, characters: list[Character], target: Character | Tower):
        """
        Make all characters in the list attack the target. Target has to be in their attack radii.
        This function override previous action.
        """
        pass

    def action_move_along(self, characters: list[Character], direction: tuple[float, float]):
        """
        Make all characters in the list move along the direction. May bump into the wall or border.
        This function override previous action.
        """
        pass

    def action_clear(self, characters: list[Character]):
        """
        Clear previous assigned action of all characters in the list. (They will stand still)
        """
        pass

    def change_spawn_type(self, tower: Tower, spawn_type: TowerSpawnType):
        """Change the spawning character type of a tower."""
        pass

    def sort_by_distance(self, characters: list[Character], target: tuple[float, float]):
        """Sort the whole character list according to the distance from target. Tie breaked arbitrarily."""
        pass
