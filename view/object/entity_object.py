from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from event_manager import EventDiscardEntity
from instances_manager import get_event_manager
from view.object.object_base import ObjectBase
# if TYPE_CHECKING:
#     from view.object.range import ViewRangeView, AttackRangeView

if TYPE_CHECKING:
    from model import Entity


class EntityObject(ObjectBase):

    def __init__(self, canvas: pg.Surface, entity: Entity, priority: float = const.WINDOW_SIZE[1] + 10):
        self.entity: Entity = entity
        self.position: pg.Vector2 = self.entity.position.copy()
        super().__init__(canvas, priority)
        self.register_listeners()

    def handle_discard_entity(self, _: EventDiscardEntity):
        from view.object.range import ViewRangeView, AttackRangeView
        self.exist = False

    def register_listeners(self):
        """Register all listeners of this object with the event manager."""
        ev_manager = get_event_manager()
        ev_manager.register_listener(
            EventDiscardEntity, self.handle_discard_entity, self.entity.id)
    
    def unregister_listeners(self):
        ev_manager = get_event_manager()
        ev_manager.unregister_listener(
            EventDiscardEntity, self.handle_discard_entity, self.entity.id)

        
        
"""
after discard event manager listen <view.object.entity.EntityView object at 0x73b4660c0670> 4
<class 'event_manager.events.EventDiscardEntity'> 4
<bound method EntityObject.handle_discard_entity of <view.object.entity.EntityView object at 0x73b4660c0670>>
<bound method EntityObject.handle_discard_entity of <view.object.entity.EntityView object at 0x73b4660c0670>>
<bound method EntityObject.handle_discard_entity of <view.object.range.ViewRangeView object at 0x73b4660c0700>>
<bound method EntityObject.handle_discard_entity of <view.object.range.AttackRangeView object at 0x73b4660c0760>>
<bound method EntityObject.handle_discard_entity of <view.object.abilities_cd.AbilitiesCDView object at 0x73b4660c07c0>>
<bound method EntityObject.handle_discard_entity of <view.object.abilities_cd.AbilitiesCDView object at 0x73b4660c07c0>>
<bound method EntityObject.handle_discard_entity of <view.object.health.HealthView object at 0x73b4660c0850>>
<class 'event_manager.events.EventAttack'> 4
<bound method Melee.take_damage of <model.character.melee.Melee object at 0x73b4660c0340>>
after discard event manager listen <view.object.entity.EntityView object at 0x73b4660c0670> 4
<class 'event_manager.events.EventDiscardEntity'> 4
<bound method EntityObject.handle_discard_entity of <view.object.entity.EntityView object at 0x73b4660c0670>>
<bound method EntityObject.handle_discard_entity of <view.object.entity.EntityView object at 0x73b4660c0670>>
<bound method EntityObject.handle_discard_entity of <view.object.range.ViewRangeView object at 0x73b4660c0700>>
<bound method EntityObject.handle_discard_entity of <view.object.range.AttackRangeView object at 0x73b4660c0760>>
<bound method EntityObject.handle_discard_entity of <view.object.abilities_cd.AbilitiesCDView object at 0x73b4660c07c0>>
<bound method EntityObject.handle_discard_entity of <view.object.abilities_cd.AbilitiesCDView object at 0x73b4660c07c0>>
<bound method EntityObject.handle_discard_entity of <view.object.health.HealthView object at 0x73b4660c0850>>
<class 'event_manager.events.EventAttack'> 4
<bound method Melee.take_damage of <model.character.melee.Melee object at 0x73b4660c0340>>
after discard event manager listen <view.object.range.ViewRangeView object at 0x73b4660c0700> 4
<class 'event_manager.events.EventDiscardEntity'> 4
<bound method EntityObject.handle_discard_entity of <view.object.entity.EntityView object at 0x73b4660c0670>>
<bound method EntityObject.handle_discard_entity of <view.object.entity.EntityView object at 0x73b4660c0670>>
<bound method EntityObject.handle_discard_entity of <view.object.range.ViewRangeView object at 0x73b4660c0700>>
<bound method EntityObject.handle_discard_entity of <view.object.range.AttackRangeView object at 0x73b4660c0760>>
<bound method EntityObject.handle_discard_entity of <view.object.abilities_cd.AbilitiesCDView object at 0x73b4660c07c0>>
<bound method EntityObject.handle_discard_entity of <view.object.abilities_cd.AbilitiesCDView object at 0x73b4660c07c0>>
<bound method EntityObject.handle_discard_entity of <view.object.health.HealthView object at 0x73b4660c0850>>
<class 'event_manager.events.EventAttack'> 4
<bound method Melee.take_damage of <model.character.melee.Melee object at 0x73b4660c0340>>
after discard event manager listen <view.object.range.AttackRangeView object at 0x73b4660c0760> 4
<class 'event_manager.events.EventDiscardEntity'> 4
<bound method EntityObject.handle_discard_entity of <view.object.entity.EntityView object at 0x73b4660c0670>>
<bound method EntityObject.handle_discard_entity of <view.object.entity.EntityView object at 0x73b4660c0670>>
<bound method EntityObject.handle_discard_entity of <view.object.range.ViewRangeView object at 0x73b4660c0700>>
<bound method EntityObject.handle_discard_entity of <view.object.range.AttackRangeView object at 0x73b4660c0760>>
<bound method EntityObject.handle_discard_entity of <view.object.abilities_cd.AbilitiesCDView object at 0x73b4660c07c0>>
<bound method EntityObject.handle_discard_entity of <view.object.abilities_cd.AbilitiesCDView object at 0x73b4660c07c0>>
<bound method EntityObject.handle_discard_entity of <view.object.health.HealthView object at 0x73b4660c0850>>
<class 'event_manager.events.EventAttack'> 4
<bound method Melee.take_damage of <model.character.melee.Melee object at 0x73b4660c0340>>
after discard event manager listen <view.object.abilities_cd.AbilitiesCDView object at 0x73b4660c07c0> 4
<class 'event_manager.events.EventDiscardEntity'> 4
<bound method EntityObject.handle_discard_entity of <view.object.entity.EntityView object at 0x73b4660c0670>>
<bound method EntityObject.handle_discard_entity of <view.object.entity.EntityView object at 0x73b4660c0670>>
<bound method EntityObject.handle_discard_entity of <view.object.range.ViewRangeView object at 0x73b4660c0700>>
<bound method EntityObject.handle_discard_entity of <view.object.range.AttackRangeView object at 0x73b4660c0760>>
<bound method EntityObject.handle_discard_entity of <view.object.abilities_cd.AbilitiesCDView object at 0x73b4660c07c0>>
<bound method EntityObject.handle_discard_entity of <view.object.abilities_cd.AbilitiesCDView object at 0x73b4660c07c0>>
<bound method EntityObject.handle_discard_entity of <view.object.health.HealthView object at 0x73b4660c0850>>
<class 'event_manager.events.EventAttack'> 4
<bound method Melee.take_damage of <model.character.melee.Melee object at 0x73b4660c0340>>
after discard event manager listen <view.object.abilities_cd.AbilitiesCDView object at 0x73b4660c07c0> 4
<class 'event_manager.events.EventDiscardEntity'> 4
<bound method EntityObject.handle_discard_entity of <view.object.entity.EntityView object at 0x73b4660c0670>>
<bound method EntityObject.handle_discard_entity of <view.object.entity.EntityView object at 0x73b4660c0670>>
<bound method EntityObject.handle_discard_entity of <view.object.range.ViewRangeView object at 0x73b4660c0700>>
<bound method EntityObject.handle_discard_entity of <view.object.range.AttackRangeView object at 0x73b4660c0760>>
<bound method EntityObject.handle_discard_entity of <view.object.abilities_cd.AbilitiesCDView object at 0x73b4660c07c0>>
<bound method EntityObject.handle_discard_entity of <view.object.abilities_cd.AbilitiesCDView object at 0x73b4660c07c0>>
<bound method EntityObject.handle_discard_entity of <view.object.health.HealthView object at 0x73b4660c0850>>
<class 'event_manager.events.EventAttack'> 4
<bound method Melee.take_damage of <model.character.melee.Melee object at 0x73b4660c0340>>
after discard event manager listen <view.object.health.HealthView object at 0x73b4660c0850> 4
<class 'event_manager.events.EventDiscardEntity'> 4
<bound method EntityObject.handle_discard_entity of <view.object.entity.EntityView object at 0x73b4660c0670>>
<bound method EntityObject.handle_discard_entity of <view.object.entity.EntityView object at 0x73b4660c0670>>
<bound method EntityObject.handle_discard_entity of <view.object.range.ViewRangeView object at 0x73b4660c0700>>
<bound method EntityObject.handle_discard_entity of <view.object.range.AttackRangeView object at 0x73b4660c0760>>
<bound method EntityObject.handle_discard_entity of <view.object.abilities_cd.AbilitiesCDView object at 0x73b4660c07c0>>
<bound method EntityObject.handle_discard_entity of <view.object.abilities_cd.AbilitiesCDView object at 0x73b4660c07c0>>
<bound method EntityObject.handle_discard_entity of <view.object.health.HealthView object at 0x73b4660c0850>>
<class 'event_manager.events.EventAttack'> 4
<bound method Melee.take_damage of <model.character.melee.Melee object at 0x73b4660c0340>>
"""