import pygame as pg

import const
from event_manager import *
from instances_manager import get_event_manager, get_model


class BackgroundMusic:
    def __init__(self):
        """
        This function is called when the BackGroundMusic is created to play 
        the background music.
        """
        pg.mixer.init()
        pg.mixer.music.load(const.BGM_PATH[const.PartyType.NEUTRAL])
        pg.mixer.music.play(-1)
        self.default_volume = const.BGM_VOLUME
        pg.mixer.music.set_volume(self.default_volume/3)
        self.sound = {}
        for effect, path in const.EFFECT_PATH.items():
            self.sound[effect] = pg.mixer.Sound(path)
            self.sound[effect].set_volume(const.EFFECT_VOLUME[effect])
        self.__register_listeners()

    def __handle_start(self, _: EventStartGame):
        """
        The variation for the in-game Background Music is determined by
        the party NOT present in game.
        """
        model = get_model()
        parties = [team.party for team in model.teams]
        missing_party = [
            party for party in const.PartyType if party not in parties and party != const.PartyType.NEUTRAL][0]
        if missing_party is not None:
            pg.mixer.music.fadeout(500)
            pg.mixer.music.unload()
            print(const.BGM_PATH[missing_party])
            pg.mixer.music.load(const.BGM_PATH[missing_party])
            pg.mixer.music.play(-1)
            pg.mixer.music.set_volume(self.default_volume)

    def __handle_pause(self, _: EventPauseModel):
        if pg.mixer.music.get_busy():
            pg.mixer.music.set_volume(self.default_volume / 4)

    def __handle_resume(self, _: EventResumeModel):
        if pg.mixer.music.get_busy():
            pg.mixer.music.set_volume(self.default_volume)

    def __handle_change_party(self, _: EventChangeParty):
        self.sound[const.EffectType.SELECT].play()

    def __handle_attack(self, event: EventAttack):
        if event.attacker.entity_type == const.CharacterType.MELEE:
            self.sound[const.EffectType.ATTACK_MELEE].play()
        else:
            self.sound[const.EffectType.ATTACK_RANGE].play()

    def __handle_create_entity(self, event: EventCreateEntity):
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventAttack, self.__handle_attack, event.entity.id)

    def __handle_character_died(self, event: EventCharacterDied):
        ev_manager = get_event_manager()
        ev_manager.unregister_listener(EventAttack, self.__handle_attack, event.character.id)


    def __register_listeners(self):
        """Register every listeners of this object into the event manager."""
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventStartGame, self.__handle_start)
        ev_manager.register_listener(EventPauseModel, self.__handle_pause)
        ev_manager.register_listener(EventResumeModel, self.__handle_resume)
        ev_manager.register_listener(EventChangeParty, self.__handle_change_party)
        ev_manager.register_listener(EventCreateEntity, self.__handle_create_entity)
        ev_manager.register_listener(EventCharacterDied, self.__handle_character_died)
