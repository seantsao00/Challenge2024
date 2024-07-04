import pygame as pg
import sys
import const
class PartySelection:
    def __init__(self):
        self.parties = [const.PartyTypes.JUNIOR, const.PartyTypes.FBI, const.PartyTypes.POLICE, const.PartyTypes.BLACK, const.PartyTypes.MAORI]
        self.selected_indices = [0, 0, 0, 0]  
        self.selected_parties = [const.PartyTypes.JUNIOR, const.PartyTypes.JUNIOR, const.const.PartyTypes.JUNIOR, const.PartyTypes.JUNIOR]  
        self.player_controls = [const.PARTY_KEYS_MAP['team1'], const.PARTY_KEYS_MAP['team2'], const.PARTY_KEYS_MAP['team3'], const.PARTY_KEYS_MAP['team4']]
    def handle_select_party(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                for i, controls in enumerate(self.player_controls):
                    if event.key == controls['left']:
                        self.selected_indices[i] = (self.selected_indices[i] + 4) % len(self.parties)
                        self.selected_parties[i] = self.parties[self.selected_indices[i]]
                    elif event.key == controls['right']:
                        self.selected_indices[i] = (self.selected_indices[i] + 1) % len(self.parties)
                        self.selected_parties[i] = self.parties[self.selected_indices[i]]
                    elif event.key == controls['enter']:
                        self.selected_parties[i] = self.parties[self.selected_indices[i]]
                        print(f'Player {i + 1} chooses {self.selected_parties[i]}')
