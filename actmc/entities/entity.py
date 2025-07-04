"""
The MIT License (MIT)

Copyright (c) 2025-present Snifo

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, Any, Union, TypeVar, Optional
    from ..ui import gui
    from ..math import Vector3D, Rotation
    T = TypeVar('T', int, str, default=int)

__all__ = ('BaseEntity', 'Entity', 'Living', 'Insentient', 'Creature')


class BaseEntity[T]:
    """
    Base entity class with generic ID type.

    Parameters
    ----------
    entity_id: T
        Unique identifier for the entity
    """
    __slots__ = ('id',)

    def __init__(self, entity_id: T) -> None:
        self.id: T = entity_id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"


class Entity(BaseEntity[int]):
    """
    Base Entity class with common metadata fields and attributes.

    Parameters
    ----------
    entity_id: int
        Unique entity ID
    uuid: str
        Entity UUID string
    position: Vector3D[float]
        3D position coordinates
    rotation: Rotation
        Entity rotation data
    metadata: Dict[int, Any]
        Raw metadata dictionary from server
    """
    __slots__ = ('uuid', 'position', 'rotation', 'raw_metadata', 'properties')

    def __init__(self, entity_id: int, uuid: str, position: Vector3D[float], rotation: Rotation,
                 metadata: Dict[int, Any]) -> None:
        super().__init__(entity_id)
        self.uuid: str = uuid
        self.position: Vector3D[float] = position
        self.rotation: Rotation = rotation
        self.raw_metadata: Dict[int, Any] = metadata
        self.properties: Dict[str, Dict[str, Any]] = {}

    @property
    def _bit_mask(self) -> int:
        """Entity bit mask flags."""
        return int(self.get_metadata_value(0, 0))

    @property
    def air(self) -> int:
        """
        Remaining air ticks.

        Returns
        -------
        int
            Number of air ticks remaining before drowning
        """
        return int(self.get_metadata_value(1, 300))

    @property
    def custom_name(self) -> Optional[str]:
        """
        Custom name text component or None.

        Returns
        -------
        Optional[str]
            Custom display name for the entity, or None if not set
        """
        name = self.get_metadata_value(2)
        return str(name) if name is not None else None

    @property
    def is_custom_name_visible(self) -> bool:
        """
        Whether custom name is visible above entity.

        Returns
        -------
        bool
            True if custom name should be displayed above the entity
        """
        return bool(self.get_metadata_value(3, False))

    @property
    def is_silent(self) -> bool:
        """
        Whether entity makes sounds.

        Returns
        -------
        bool
            True if entity is silent and won't produce sounds
        """
        return bool(self.get_metadata_value(4, False))

    @property
    def no_gravity(self) -> bool:
        """
        Whether entity is affected by gravity.

        Returns
        -------
        bool
            True if entity ignores gravity effects
        """
        return bool(self.get_metadata_value(5, False))

    def update_metadata(self, metadata: Dict[int, Any]) -> None:
        """
        Update entity metadata from metadata packet.

        Parameters
        ----------
        metadata: Dict[int, Any]
            New metadata values indexed by metadata ID
        """
        self.raw_metadata.update(metadata)

    def update_properties(self, properties: Dict[str, Dict[str, Any]]) -> None:
        """
        Update entity attributes from properties packet.

        Parameters
        ----------
        properties: Dict[str, Dict[str, Any]]
            Attribute properties containing base values and modifiers
        """
        for key, prop_data in properties.items():
            if not isinstance(prop_data, dict) or 'value' not in prop_data:
                continue

            base_value = float(prop_data['value'])
            modifiers = prop_data.get('modifiers', {})

            if not isinstance(modifiers, dict):
                modifiers = {}

            final_value = self._calculate_final_value(base_value, modifiers)

            self.properties[key] = {
                'base': base_value,
                'final': final_value,
                'modifiers': modifiers
            }

    @staticmethod
    def _calculate_final_value(base_value: float, modifiers: Dict[str, Dict[str, Union[int, float]]]) -> float:
        """Calculate final attribute value with modifiers."""
        if not modifiers:
            return base_value

        value = base_value
        mod_list = list(modifiers.values())

        for mod in mod_list:
            if isinstance(mod, dict) and mod.get('operation') == 0:
                amount = mod.get('amount', 0)
                if isinstance(amount, (int, float)):
                    value += float(amount)

        multiply_base = 0.0
        for mod in mod_list:
            if isinstance(mod, dict) and mod.get('operation') == 1:
                amount = mod.get('amount', 0)
                if isinstance(amount, (int, float)):
                    multiply_base += float(amount)

        if multiply_base:
            value += base_value * multiply_base

        for mod in mod_list:
            if isinstance(mod, dict) and mod.get('operation') == 2:
                amount = mod.get('amount', 0)
                if isinstance(amount, (int, float)):
                    value *= (1 + float(amount))
        return value

    def get_attribute(self, key: str, default: float = 0.0) -> float:
        """
        Get final attribute value.

        Parameters
        ----------
        key: str
            Attribute key name
        default: float
            Default value if attribute not found.

        Returns
        -------
        float
            Final attribute value after applying modifiers
        """
        if key in self.properties:
            final_value = self.properties[key].get('final')
            if isinstance(final_value, (int, float)):
                return float(final_value)
        return default

    def get_metadata_value(self, index: int, default: Any = None) -> Any:
        """
        Get metadata value by index with default fallback.

        Parameters
        ----------
        index: int
            Metadata index to retrieve
        default: Any
            Default value if metadata not found.

        Returns
        -------
        Any
            Metadata value at the specified index, or default if not found
        """
        if index in self.raw_metadata:
            return self.raw_metadata[index]['value']
        return default

    @property
    def max_health(self) -> float:
        """
        Maximum health attribute value.

        Returns
        -------
        float
            Maximum health points for this entity
        """
        return self.get_attribute('generic.maxHealth', 20.0)

    @property
    def movement_speed(self) -> float:
        """
        Movement speed attribute value.

        Returns
        -------
        float
            Movement speed multiplier for this entity
        """
        return self.get_attribute('generic.movementSpeed', 0.1)

    @property
    def armor(self) -> float:
        """
        Armor attribute value.

        Returns
        -------
        float
            Armor points providing damage reduction
        """
        return self.get_attribute('generic.armor', 0.0)

    @property
    def attack_speed(self) -> float:
        """
        Attack speed attribute value.

        Returns
        -------
        float
            Attack speed multiplier for this entity
        """
        return self.get_attribute('generic.attackSpeed', 4.0)

    @property
    def on_fire(self) -> bool:
        """
        Whether entity is on fire (bit 0).

        Returns
        -------
        bool
            True if entity is currently on fire
        """
        return bool(self._bit_mask & 0x01)

    @property
    def crouched(self) -> bool:
        """
        Whether entity is crouching (bit 1).

        Returns
        -------
        bool
            True if entity is in crouching state
        """
        return bool(self._bit_mask & 0x02)

    @property
    def sprinting(self) -> bool:
        """
        Whether entity is sprinting (bit 3).

        Returns
        -------
        bool
            True if entity is currently sprinting
        """
        return bool(self._bit_mask & 0x08)

    @property
    def invisible(self) -> bool:
        """
        Whether entity is invisible (bit 5).

        Returns
        -------
        bool
            True if entity has invisibility effect active
        """
        return bool(self._bit_mask & 0x20)

    @property
    def glowing(self) -> bool:
        """
        Whether entity is glowing (bit 6).

        Returns
        -------
        bool
            True if entity has glowing outline effect
        """
        return bool(self._bit_mask & 0x40)

    @property
    def flying_with_elytra(self) -> bool:
        """
        Whether entity is flying with elytra (bit 7).

        Returns
        -------
        bool
            True if entity is gliding with elytra wings
        """
        return bool(self._bit_mask & 0x80)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Living(Entity):
    """Living entity extending Entity with health and status effects."""

    __slots__ = ('_equipment',)

    def __init__(self, entity_id: int, uuid: str, position: Vector3D[float], rotation: Rotation,
                 metadata: Dict[int, Any]):
        super().__init__(entity_id, uuid, position, rotation, metadata)
        self._equipment: Dict[int, gui.Slot] = {}

    def set_equipment(self, slot: gui.Slot) -> None:
        """
        Set equipment in the specified slot.

        Returns
        -------
        None
        """
        self._equipment[slot.index] = slot

    @property
    def equipment(self) -> Dict[int, gui.Slot]:
        """
        Get all equipment slots.

        Returns
        -------
        Dict[int, gui.Slot]
            Dictionary mapping slot IDs to their equipment slots.
        """
        return self._equipment

    @property
    def has_equipment(self) -> bool:
        """
        Check if the entity has any equipment.

        Returns
        -------
        bool
            True if entity has equipment, False otherwise.
        """
        return bool(self._equipment)

    @property
    def hand_states(self) -> int:
        """
        Hand state bit mask.

        Returns
        -------
        int
            Bit mask containing hand usage states
        """
        return int(self.get_metadata_value(6, 0))

    @property
    def health(self) -> float:
        """
        Current health value.

        Returns
        -------
        float
            Current health points remaining
        """
        return float(self.get_metadata_value(7, 1.0))

    @property
    def potion_effect_color(self) -> int:
        """
        Potion effect particle color.

        Returns
        -------
        int
            RGB color value for potion effect particles
        """
        return int(self.get_metadata_value(8, 0))

    @property
    def is_potion_effect_ambient(self) -> bool:
        """
        Whether potion effect is ambient.

        Returns
        -------
        bool
            True if potion effect particles are ambient (less visible)
        """
        return bool(self.get_metadata_value(9, False))

    @property
    def arrows_in_entity(self) -> int:
        """
        Number of arrows stuck in entity.

        Returns
        -------
        int
            Count of arrows visually stuck in the entity
        """
        return int(self.get_metadata_value(10, 0))

    @property
    def is_hand_active(self) -> bool:
        """
        Whether hand is active (using item).

        Returns
        -------
        bool
            True if entity is currently using an item with their hand
        """
        return bool(self.hand_states & 0x01)

    @property
    def active_hand(self) -> int:
        """
        Which hand is active (0=main, 1=off).

        Returns
        -------
        int
            Hand index: 0 for main hand, 1 for off-hand
        """
        return (self.hand_states & 0x02) >> 1


class Insentient(Living):
    """Insentient entity extending Living (base for mobs with AI)."""

    __slots__ = ()

    @property
    def _insentient_bit_mask(self) -> int:
        """Insentient-specific bit mask."""
        return int(self.get_metadata_value(11, 0))

    @property
    def no_ai(self) -> bool:
        """
        Whether AI is disabled (bit 0).

        Returns
        -------
        bool
            True if entity's AI behavior is disabled
        """
        return bool(self._insentient_bit_mask & 0x01)

    @property
    def left_handed(self) -> bool:
        """
        Whether entity is left-handed (bit 1).

        Returns
        -------
        bool
            True if entity prefers using left hand for actions
        """
        return bool(self._insentient_bit_mask & 0x02)


class Creature(Insentient):
    """Creature entity extending Insentient."""

    __slots__ = ()

