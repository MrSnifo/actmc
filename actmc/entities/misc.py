from __future__ import annotations

from typing import Any, Optional


from .entity import Entity


class AreaEffectCloud(Entity):
    """Area Effect Cloud entity extending Entity."""
    __slots__ = ()

    @property
    def radius(self) -> float:
        """Cloud radius from metadata index 6."""
        return float(self.get_metadata_value(6, 0.5))

    @property
    def color(self) -> int:
        """Cloud color from metadata index 7."""
        return int(self.get_metadata_value(7, 0))

    @property
    def ignore_radius(self) -> bool:
        """Whether to ignore radius from metadata index 8."""
        return bool(self.get_metadata_value(8, False))

    @property
    def particle_id(self) -> int:
        """Particle ID from metadata index 9."""
        return int(self.get_metadata_value(9, 15))  # mobSpell

    @property
    def particle_param1(self) -> int:
        """Particle parameter 1 from metadata index 10."""
        return int(self.get_metadata_value(10, 0))

    @property
    def particle_param2(self) -> int:
        """Particle parameter 2 from metadata index 11."""
        return int(self.get_metadata_value(11, 0))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}, radius={self.radius}>"


class FishingHook(Entity):
    """Fishing Hook entity extending Entity."""
    __slots__ = ()

    @property
    def hooked_entity_id(self) -> int:
        """Hooked entity ID from metadata index 6."""
        return int(self.get_metadata_value(6, 0))

    @property
    def has_hooked_entity(self) -> bool:
        """Whether the fishing hook has hooked an entity."""
        return self.hooked_entity_id > 0

    @property
    def actual_hooked_entity_id(self) -> int:
        """Get the actual hooked entity ID (metadata stores id + 1)."""
        return self.hooked_entity_id - 1 if self.has_hooked_entity else 0

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class EnderCrystal(Entity):
    """Ender Crystal entity extending Entity."""
    __slots__ = ()

    @property
    def beam_target(self) -> Optional[Any]:
        """Beam target from metadata index 6."""
        return self.get_metadata_value(6)

    @property
    def show_bottom(self) -> bool:
        """Whether to show bottom from metadata index 7."""
        return bool(self.get_metadata_value(7, True))

    @property
    def has_beam_target(self) -> bool:
        """Whether the crystal has a beam target."""
        return self.beam_target is not None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Hanging(Entity):
    """Hanging entity extending Entity."""
    __slots__ = ()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class ItemFrame(Hanging):
    """Item Frame entity extending Hanging."""
    __slots__ = ()

    @property
    def item(self) -> Optional[Any]:
        """Item in frame from metadata index 6."""
        return self.get_metadata_value(6)

    @property
    def rotation_value(self) -> int:
        """Item rotation value from metadata index 7."""
        return int(self.get_metadata_value(7, 0))

    @property
    def has_item(self) -> bool:
        """Whether the item frame contains an item."""
        return self.item is not None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Item(Entity):
    """Item entity extending Entity."""
    __slots__ = ()

    @property
    def item(self) -> Optional[Any]:
        """Item data from metadata index 6."""
        return self.get_metadata_value(6)

    @property
    def has_item(self) -> bool:
        """Whether the item entity contains an item."""
        return self.item is not None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}, item={self.item}>"


class Flying(Entity):
    """Flying entity extending Entity (via Insentient in hierarchy)."""
    __slots__ = ()

    @property
    def hand_states(self) -> int:
        """Hand state bit mask from metadata index 6."""
        return int(self.get_metadata_value(6, 0))

    @property
    def health(self) -> float:
        """Current health value from metadata index 7."""
        return float(self.get_metadata_value(7, 1.0))

    @property
    def potion_effect_color(self) -> int:
        """Potion effect particle color from metadata index 8."""
        return int(self.get_metadata_value(8, 0))

    @property
    def is_potion_effect_ambient(self) -> bool:
        """Whether potion effect is ambient from metadata index 9."""
        return bool(self.get_metadata_value(9, False))

    @property
    def arrows_in_entity(self) -> int:
        """Number of arrows stuck in entity from metadata index 10."""
        return int(self.get_metadata_value(10, 0))

    @property
    def insentient_bit_mask(self) -> int:
        """Insentient-specific bit mask from metadata index 11."""
        return int(self.get_metadata_value(11, 0))

    @property
    def is_hand_active(self) -> bool:
        """Whether hand is active (using item)."""
        return bool(self.hand_states & 0x01)

    @property
    def active_hand(self) -> int:
        """Which hand is active (0=main, 1=off)."""
        return (self.hand_states & 0x02) >> 1

    @property
    def no_ai(self) -> bool:
        """Whether AI is disabled (bit 0)."""
        return bool(self.insentient_bit_mask & 0x01)

    @property
    def left_handed(self) -> bool:
        """Whether entity is left-handed (bit 1)."""
        return bool(self.insentient_bit_mask & 0x02)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}, health={self.health}>"