import pygame as pg

import const
from event_manager import (EventAttack, EventChangeParty, EventCharacterDied, EventCreateEntity,
                           EventGameOver, EventPauseModel, EventResultChamp,
                           EventResultChoseCharacter, EventResultWandering, EventResumeModel,
                           EventStartGame, EventNyanCat)
from instances_manager import get_event_manager, get_model


class BackgroundMusic:
    def __init__(self):
        """
        This function is called when the BackGroundMusic is created to play 
        the background music.
        """
        if pg.mixer.get_init() is not None:
            pg.mixer.init()
        pg.mixer.music.load(const.BGM_PATH[const.PartyType.NEUTRAL])
        pg.mixer.music.play(loops=-1)
        self.__default_volume = const.BGM_VOLUME
        pg.mixer.music.set_volume(self.__default_volume / 3)
        self.__sound = {}
        self.__selected_track = const.BGM_PATH[const.PartyType.NEUTRAL]
        for effect, path in const.EFFECT_PATH.items():
            self.__sound[effect] = pg.mixer.Sound(path)
            self.__sound[effect].set_volume(const.EFFECT_VOLUME[effect])
        self.__register_listeners()

    def __handle_start(self, _: EventStartGame):
        """
        The variation for the in-game Background Music is determined by
        the party NOT present in game.
        """
        model = get_model()
        parties = [team.party for team in model.teams]
        missing_party = [party for party in const.PartyType
                         if party not in parties and party != const.PartyType.NEUTRAL][0]
        self.__selected_track = const.BGM_PATH[missing_party]
        pg.mixer.music.fadeout(500)
        pg.mixer.music.unload()
        pg.mixer.music.load(self.__selected_track)
        pg.mixer.music.play(loops=-1)
        pg.mixer.music.set_volume(self.__default_volume)

    def __handle_pause(self, _: EventPauseModel):
        if pg.mixer.music.get_busy():
            pg.mixer.music.set_volume(self.__default_volume / 4)

    def __handle_resume(self, _: EventResumeModel):
        if pg.mixer.music.get_busy():
            pg.mixer.music.set_volume(self.__default_volume)

    def __handle_change_party(self, _: EventChangeParty):
        self.__sound[const.EffectType.SELECT].play()

    def __handle_attack(self, event: EventAttack):
        if event.attacker.entity_type == const.CharacterType.MELEE:
            self.__sound[const.EffectType.ATTACK_MELEE].play()
        else:
            self.__sound[const.EffectType.ATTACK_RANGE].play()

    def __handle_create_entity(self, event: EventCreateEntity):
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventAttack, self.__handle_attack, event.entity.id)

    def __handle_character_died(self, event: EventCharacterDied):
        ev_manager = get_event_manager()
        ev_manager.unregister_listener(EventAttack, self.__handle_attack, event.character.id)

    def __handle_change_party(self, _: EventChangeParty):
        self.__sound[const.EffectType.SELECT].play()

    def __handle_attack(self, event: EventAttack):
        if event.attacker.entity_type == const.CharacterType.MELEE:
            self.__sound[const.EffectType.ATTACK_MELEE].play()
        else:
            self.__sound[const.EffectType.ATTACK_RANGE].play()

    def __handle_create_entity(self, event: EventCreateEntity):
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventAttack, self.__handle_attack, event.entity.id)

    def __handle_character_died(self, event: EventCharacterDied):
        ev_manager = get_event_manager()
        ev_manager.unregister_listener(EventAttack, self.__handle_attack, event.character.id)

    def __handle_game_over(self, _: EventGameOver):
        pg.mixer.music.fadeout(500)
        pg.mixer.music.unload()
        pg.mixer.music.load(const.BGM_ROLL_PATH)
        pg.mixer.music.set_volume(self.__default_volume / 4)
        pg.mixer.music.play(loops=-1)

    def __handle_result_wandering(self, _: EventResultWandering):
        if pg.mixer.music.get_busy():
            pg.mixer.music.set_volume(self.__default_volume)

    def __handle_chose_character(self, _: EventResultChoseCharacter):
        if pg.mixer.music.get_busy():
            pg.mixer.music.set_volume(self.__default_volume / 4)
        self.__sound[const.EffectType.SHOT].play()

    def __handle_result_champ(self, _: EventResultChamp):
        pg.mixer.music.load(const.BGM_END_PATH)
        pg.mixer.music.set_volume(self.__default_volume * 1.5)
        pg.mixer.music.play(loops=0)

    def __handle_nyan(self, _: EventNyanCat):
        paused_pos = pg.mixer.music.get_pos()
        pg.mixer.music.load(const.BGM_NYAN_PATH)
        pg.mixer.music.play(loops=0)
        pg.mixer.music.queue(self.__selected_track)

    def __register_listeners(self):
        """Register every listeners of this object into the event manager."""
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventStartGame, self.__handle_start)
        ev_manager.register_listener(EventPauseModel, self.__handle_pause)
        ev_manager.register_listener(EventResumeModel, self.__handle_resume)
        ev_manager.register_listener(EventChangeParty, self.__handle_change_party)
        ev_manager.register_listener(EventCreateEntity, self.__handle_create_entity)
        ev_manager.register_listener(EventCharacterDied, self.__handle_character_died)
        ev_manager.register_listener(EventGameOver, self.__handle_game_over)
        ev_manager.register_listener(EventResultWandering, self.__handle_result_wandering)
        ev_manager.register_listener(EventResultChoseCharacter, self.__handle_chose_character)
        ev_manager.register_listener(EventResultChamp, self.__handle_result_champ)
        ev_manager.register_listener(EventNyanCat, self.__handle_nyan)
