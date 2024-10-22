"""
The module defines Controller class.
"""

import pygame as pg

import const
from event_manager import (EventChangeParty, EventGameOver, EventHumanInput, EventInitialize,
                           EventNyanCat, EventPauseModel, EventQuit, EventResumeModel,
                           EventSelectCharacter, EventSelectParty, EventUnconditionalTick,
                           EventUseRangerAbility, EventViewChangeTeam, EventViewPathSwitch,
                           EventViewShowRangeSwitch)
from instances_manager import get_event_manager, get_model
from model import Character, TimerManager, Tower
from util import log_info
from view import ScreenInfo


class Controller:
    """
    The object handles the control input, either from keyboard or from AI.
    """

    def __init__(self):
        """
        Initialize the Controller object.

        This function is called when the Controller is created.
        For more specific objects related to a game instance,
        they should be initialized in Controller.initialize()
        """
        self.__resize_ratio: float = ScreenInfo.resize_ratio
        self.register_listeners()
        self.egg_record = 0

    def initialize(self, _: EventInitialize):
        """Initialize attributes related to a game."""

    def transform(self, x: float, y: float) -> tuple[float, float]:
        """Transform control position to position in model's coordinate."""
        x = x / self.__resize_ratio
        y = y / self.__resize_ratio
        x -= (const.WINDOW_SIZE[0] - const.ARENA_SIZE[0]) / 2
        return (x, y)

    def handle_unconditional_tick(self, _: EventUnconditionalTick):
        """Do actions that should be executed every tick, regardless of whether the game is in a paused state or not."""
        ev_manager = get_event_manager()
        model = get_model()
        # Called once per game tick. We check our keyboard presses here.
        pg_events = pg.event.get()
        for pg_event in pg_events:
            # Handle window manager closing our window
            if pg_event.type == pg.QUIT:
                ev_manager.post(EventQuit())
            TimerManager.handle_event(pg_event)

        if model.state is const.State.PLAY:
            self.ctrl_play(pg_events)
        elif model.state is const.State.PAUSE:
            self.ctrl_pause(pg_events)
        elif model.state is const.State.COVER:
            self.ctrl_cover(pg_events)
        elif model.state is const.State.SELECT_PARTY:
            self.ctrl_select_party(pg_events)
        elif model.state is const.State.RESULT:
            self.ctrl_result(pg_events)

    def ctrl_play(self, pg_events: list[pg.event.Event]):
        """
        Control depending on key input when the model.state is PLAY.

        When the method called, controller get what keys is pressed in this tick,
        and post EventHumanInput according to the keys pressed.
        """
        ev_manager = get_event_manager()
        model = get_model()

        for pg_event in pg_events:
            if pg_event.type == pg.KEYDOWN:
                key = pg_event.key
                if key == const.PAUSE_BUTTON:
                    ev_manager.post(EventPauseModel())
                if key == const.ABILITY_KEY:
                    ev_manager.post(EventHumanInput(
                        input_type=const.InputTypes.ABILITY))
                if key in const.TOWER_CHANGE_TYPE_BUTTONS_MAP:
                    character_type = const.TOWER_CHANGE_TYPE_BUTTONS_MAP[key]
                    ev_manager.post(EventSelectCharacter(
                        character_type=character_type))
                if key == const.CHANGE_TEAM_VISION_KEY:
                    ev_manager.post(EventViewChangeTeam())
                if key == const.SHOW_PATH_SWITCH_KEY:
                    ev_manager.post(EventViewPathSwitch())
                if key == const.SHOW_RANGE_SWITCH_KEY:
                    ev_manager.post(EventViewShowRangeSwitch())
                # ???
                if key == const.EGG_SEQ[self.egg_record]:
                    self.egg_record += 1
                else:
                    if key == const.EGG_SEQ[0]:
                        if self.egg_record <= 2:
                            pass
                        else:
                            self.egg_record = 1
                    else:
                        self.egg_record = 0
                if self.egg_record == len(const.EGG_SEQ):
                    ev_manager.post(EventNyanCat())
                    self.egg_record = 0

            if pg_event.type == pg.MOUSEBUTTONDOWN:
                x, y = pg_event.pos
                x, y = self.transform(x, y)
                y -= const.DRAW_DISPLACEMENT_Y

                if pg_event.button == 1:  # Left mouse button
                    log_info(f"[Controller] Mouse click position: ({x}, {y})")
                    if model.ranger_ability:
                        ability_target = pg.Vector2(x, y)
                        if model.ranger_controlling.reachable(ability_target):
                            ev_manager.post(EventUseRangerAbility(position=ability_target),
                                            channel_id=model.ranger_controlling.id)
                            model.ranger_controlling.abilities_time = model.get_time()
                            log_info("[Ranger] manual control success")
                        else:
                            log_info(
                                "[Ranger] manual control failed: out of range")
                        get_model().ranger_ability = False
                    else:
                        clicked = None
                        with model.entity_lock:
                            for entity in model.characters + model.towers:
                                if (pg.Vector2(x, y) - entity.position).length() < const.CLICK_SIZE[entity.entity_type][entity.state]:
                                    clicked = entity
                                    break
                        if isinstance(clicked, Character):
                            ev_manager.post(EventHumanInput(input_type=const.InputTypes.PICK,
                                                            clicked_entity=clicked))

                if pg_event.button == 3:  # Right mouse button
                    log_info(f"[Controller] Right click position: ({x}, {y})")
                    model.ranger_ability = False
                    clicked = None
                    for entity in model.towers + model.characters:  # Tower first
                        if (entity.alive and (pg.Vector2(x, y) - entity.position).length()
                                < const.CLICK_SIZE[entity.entity_type][entity.state]):
                            clicked = entity
                            log_info(f"[Controller] Right click on: {clicked}")
                            break
                    if isinstance(clicked, Character):
                        ev_manager.post(EventHumanInput(input_type=const.InputTypes.ATTACK,
                                                        clicked_entity=clicked))
                    elif isinstance(clicked, Tower):
                        ev_manager.post(EventHumanInput(input_type=const.InputTypes.PICK,
                                        clicked_entity=clicked))
                    else:
                        log_info(
                            '[Controller] Right click non interactable object')

        pressed_keys = pg.key.get_pressed()
        direction = pg.Vector2(0, 0)
        for key, val in const.DIRECTION_BUTTONS_MAP.items():
            if pressed_keys[key]:
                direction += val
        # Try to move as far as the player can.
        ev_manager.post(EventHumanInput(
            input_type=const.InputTypes.MOVE, displacement=direction))

    def ctrl_pause(self, pg_events: list[pg.event.Event]):
        """
        Control depending on key input when the model.state is PAUSE.
        """
        ev_manager = get_event_manager()
        model = get_model()

        for pg_event in pg_events:
            if pg_event.type == pg.KEYDOWN:
                key = pg_event.key
                if key == const.PAUSE_BUTTON:
                    ev_manager.post(EventResumeModel())
                elif key == pg.K_DOWN:
                    model.pause_menu.move_cursor(1)
                elif key == pg.K_UP:
                    model.pause_menu.move_cursor(-1)
                elif key in const.CONFIRM_BUTTONS:
                    model.pause_menu.execute()

    def ctrl_result(self, pg_events: list[pg.event.Event]):
        """
        Control depending on key input when the model.state is RESULT.
        """
        model = get_model()

        for pg_event in pg_events:
            if pg_event.type == pg.KEYDOWN:
                if pg_event.key in const.CONFIRM_BUTTONS:
                    model.result.handle_scopemoving_start()
                    model.result.handle_ending()

    def ctrl_cover(self, pg_events: list[pg.event.Event]):
        """
        Control depending on key input when the model.state is COVER.
        """
        ev_manager = get_event_manager()

        for pg_event in pg_events:
            if pg_event.type == pg.KEYDOWN:
                # For pausing the game
                if pg_event.key in const.CONFIRM_BUTTONS:
                    ev_manager.post(EventSelectParty())

    def ctrl_select_party(self, pg_events: list[pg.event.Event]):
        """Select party for each team."""
        ev_manager = get_event_manager()
        for pg_event in pg_events:
            if pg_event.type == pg.KEYDOWN:
                key = pg_event.key
                if key in const.PARTY_SELECTOR_BUTTONS_MAP:
                    ev_manager.post(EventChangeParty(
                        select_input=const.PARTY_SELECTOR_BUTTONS_MAP[key]))

    def register_listeners(self):
        """Register every listeners of this object into the event manager."""
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventInitialize, self.initialize)
        ev_manager.register_listener(
            EventUnconditionalTick, self.handle_unconditional_tick)
        # Listeners for TimerManager
        ev_manager.register_listener(
            EventPauseModel, TimerManager.pause_all_timer)
        ev_manager.register_listener(
            EventResumeModel, TimerManager.resume_all_timer)
        ev_manager.register_listener(
            EventGameOver, TimerManager.handle_game_over)
