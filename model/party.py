import pygame as pg
import sys
import const

class PartySelection:
    """
    Class for selecting parties in the game.
    Each PartySelection has the following properties:
     - parties: List of available parties to choose from.
     - selected_indices: List of indices indicating the current selection for each player.
     - selected_parties: List of parties currently selected by each player.
     - player_controls: List of control mappings for each player.
    """
    
    def __init__(self):
        self.selected_parties = [const.PartyTypes[0] for _ in range(4)]  
        self.player_controls = [const.PARTY_KEYS_MAP['team1'], const.PARTY_KEYS_MAP['team2'], const.PARTY_KEYS_MAP['team3'], const.PARTY_KEYS_MAP['team4']]
    
    def handle_select_party(self):
        """
        Handle input events for party selection.
        
        This function processes QUIT and KEYDOWN events. For KEYDOWN events,
        it updates the selected party for each player based on their controls.
        """
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                for i, controls in enumerate(self.player_controls):
                    if event.key == controls['left']:
                        (self.selected_parties[i] + 4) % len(const.PartyTypes)
                    elif event.key == controls['right']:
                        (self.selected_parties[i] + 1) % len(const.PartyTypes)
