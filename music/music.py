import pygame as pg

import const
from event_manager import EventInitialize, EventPauseModel, EventResumeModel
from instances_manager import get_event_manager, get_model
from util import log_info


class BackgroundMusic:
    def __init__(self):
        """
        This function is called when the BackGroundMusic is created to play 
        the background music.
        """
        pg.mixer.init()
        pg.mixer.music.load(const.BGM_PATH[const.PartyType.NEUTRAL])
        pg.mixer.music.play(loops=-1)
        self.__default_volume: float = pg.mixer.music.get_volume()
        self.__register_listeners()

    def __initialize(self, _: EventInitialize):
        """
        The variation for the in-game Background Music is determined by
        the party NOT present in game.
        """
        model = get_model()
        parties = [team.party for team in model.teams]
        missing_party = [party for party in const.PartyType
                         if party not in parties and party != const.PartyType.NEUTRAL][0]
        pg.mixer.music.fadeout(500)
        pg.mixer.music.unload()
        log_info(const.BGM_PATH[missing_party])
        pg.mixer.music.load(const.BGM_PATH[missing_party])
        pg.mixer.music.play(loops=-1)
        self.__default_volume = pg.mixer.music.get_volume()

    def __handle_pause(self, _: EventPauseModel):
        if pg.mixer.music.get_busy():
            pg.mixer.music.set_volume(self.__default_volume / 4)

    def __handle_resume(self, _: EventResumeModel):
        if pg.mixer.music.get_busy():
            pg.mixer.music.set_volume(self.__default_volume)

    def __register_listeners(self):
        """Register every listeners of this object into the event manager."""
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventInitialize, self.__initialize)
        ev_manager.register_listener(EventPauseModel, self.__handle_pause)
        ev_manager.register_listener(EventResumeModel, self.__handle_resume)
