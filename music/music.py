import os

import pygame as pg

import const
from event_manager.events import *
from instances_manager import get_event_manager, get_model


class BackgroundMusic:
    def __init__(self):
        """
        This function is called when the BackGroundMusic is created to play 
        the background music.
        """
        pg.mixer.init()
        pg.mixer.music.load(os.path.join(
            const.MUSIC_DIR, const.MUSIC_PATH[const.PartyType.NEUTRAL]))
        pg.mixer.music.play(-1)
        float: self.defualt_volume = pg.mixer.music.get_volume()
        self.__register_listeners()

    def __initialize(self, _: EventInitialize):
        """
        The variation for the in-game Background Music is determined by
        the party NOT present in game.
        """
        model = get_model()
        parties = [team.party for team in model.teams]
        missing_party = [
            party for party in const.PartyType if party not in parties and party != const.PartyType.NEUTRAL][0]
        if missing_party != None:
            pg.mixer.music.fadeout(500)
            pg.mixer.music.unload()
            pg.mixer.music.load(os.path.join(const.MUSIC_DIR, const.MUSIC_PATH[missing_party]))
            print(const.MUSIC_PATH[missing_party])
            pg.mixer.music.play(-1)
            self.defualt_volume = pg.mixer.music.get_volume()

    def __handle_pause(self, _: EventPauseModel):
        if pg.mixer.music.get_busy():
            pg.mixer.music.set_volume(self.defualt_volume/4)

    def __handle_resume(self, _: EventResumeModel):
        if pg.mixer.music.get_busy():
            pg.mixer.music.set_volume(self.defualt_volume)

    def __register_listeners(self):
        """Register every listeners of this object into the event manager."""
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventInitialize, self.__initialize)
        ev_manager.register_listener(EventPauseModel, self.__handle_pause)
        ev_manager.register_listener(EventResumeModel, self.__handle_resume)
