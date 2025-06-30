from __future__ import annotations

from typing import Dict, Any, Optional
from .entity import Entity, Living

__all__ = ('Item', 'XPOrb', 'AreaEffectCloud', 'ArmorStand', 'FallingBlock', 'FireworksRocket', 'TNTPrimed',
           'LeashKnot', 'EvocationFangs', 'FishingHook', 'EnderCrystal')

class Item(Entity):
    """Item entity representing a dropped item in the world."""

    __slots__ = ()
    ENTITY_TYPE = "minecraft:item"

    @property
    def item_stack(self) -> Optional[Dict[str, Any]]:
        """
        Item stack data from metadata index 6.

        Returns
        -------
        Optional[Dict[str, Any]]
            Item stack information or None if empty
        """
        item = self.get_metadata_value(6)
        return item if item is not None else None

    @property
    def has_item(self) -> bool:
        """
        Whether the item entity contains an item stack.

        Returns
        -------
        bool
            True if item stack is present
        """
        return self.item_stack is not None


class XPOrb(Entity):
    """Experience orb entity."""

    __slots__ = ()
    ENTITY_TYPE = "minecraft:xp_orb"


class AreaEffectCloud(Entity):
    """Area effect cloud entity for potion effects and particles."""

    __slots__ = ()
    ENTITY_TYPE = "minecraft:area_effect_cloud"

    @property
    def radius(self) -> float:
        """
        Effect cloud radius from metadata index 6.

        Returns
        -------
        float
            Cloud radius in blocks, default 0.5
        """
        return float(self.get_metadata_value(6, 0.5))

    @property
    def color(self) -> int:
        """
        Effect cloud color from metadata index 7.

        Returns
        -------
        int
            Color value for mob spell particle, default 0
        """
        return int(self.get_metadata_value(7, 0))

    @property
    def ignore_radius(self) -> bool:
        """
        Whether to ignore radius and show as single point from metadata index 8.

        Returns
        -------
        bool
            True if should show as single point, default False
        """
        return bool(self.get_metadata_value(8, False))

    @property
    def particle_id(self) -> int:
        """
        Particle type ID from metadata index 9.

        Returns
        -------
        int
            Particle ID, default 15 (mobSpell)
        """
        return int(self.get_metadata_value(9, 15))

    @property
    def particle_param1(self) -> int:
        """
        First particle parameter from metadata index 10.

        Returns
        -------
        int
            Particle parameter 1, default 0
        """
        return int(self.get_metadata_value(10, 0))

    @property
    def particle_param2(self) -> int:
        """
        Second particle parameter from metadata index 11.

        Returns
        -------
        int
            Particle parameter 2, default 0
        """
        return int(self.get_metadata_value(11, 0))


class ArmorStand(Living):
    """Armor stand entity extending Living."""

    __slots__ = ()
    ENTITY_TYPE = "minecraft:armor_stand"

    @property
    def _armor_stand_bit_mask(self) -> int:
        """
        Armor stand bit mask from metadata index 11.

        Returns
        -------
        int
            Bit mask flags, default 0
        """
        return int(self.get_metadata_value(11, 0))

    @property
    def is_small(self) -> bool:
        """
        Whether armor stand is small size (bit 0).

        Returns
        -------
        bool
            True if small size
        """
        return bool(self._armor_stand_bit_mask & 0x01)

    @property
    def has_arms(self) -> bool:
        """
        Whether armor stand has arms (bit 2).

        Returns
        -------
        bool
            True if has arms
        """
        return bool(self._armor_stand_bit_mask & 0x04)

    @property
    def has_base_plate(self) -> bool:
        """
        Whether armor stand has baseplate (bit 3 inverted).

        Returns
        -------
        bool
            True if it has baseplate
        """
        return not bool(self._armor_stand_bit_mask & 0x08)

    @property
    def is_marker(self) -> bool:
        """
        Whether armor stand is marker (bit 4).

        Returns
        -------
        bool
            True if is marker
        """
        return bool(self._armor_stand_bit_mask & 0x10)

    @property
    def head_rotation(self) -> Optional[tuple[float, float, float]]:
        """
        Head rotation from metadata index 12.

        Returns
        -------
        Optional[tuple[float, float, float]]
            (x, y, z) rotation values, default (0.0, 0.0, 0.0)
        """
        rotation = self.get_metadata_value(12, (0.0, 0.0, 0.0))
        if isinstance(rotation, (list, tuple)) and len(rotation) >= 3:
            return float(rotation[0]), float(rotation[1]), float(rotation[2])
        return 0.0, 0.0, 0.0

    @property
    def body_rotation(self) -> Optional[tuple[float, float, float]]:
        """
        Body rotation from metadata index 13.

        Returns
        -------
        Optional[tuple[float, float, float]]
            (x, y, z) rotation values, default (0.0, 0.0, 0.0)
        """
        rotation = self.get_metadata_value(13, (0.0, 0.0, 0.0))
        if isinstance(rotation, (list, tuple)) and len(rotation) >= 3:
            return float(rotation[0]), float(rotation[1]), float(rotation[2])
        return 0.0, 0.0, 0.0

    @property
    def left_arm_rotation(self) -> Optional[tuple[float, float, float]]:
        """
        Left arm rotation from metadata index 14.

        Returns
        -------
        Optional[tuple[float, float, float]]
            (x, y, z) rotation values, default (-10.0, 0.0, -10.0)
        """
        rotation = self.get_metadata_value(14, (-10.0, 0.0, -10.0))
        if isinstance(rotation, (list, tuple)) and len(rotation) >= 3:
            return float(rotation[0]), float(rotation[1]), float(rotation[2])
        return -10.0, 0.0, -10.0

    @property
    def right_arm_rotation(self) -> Optional[tuple[float, float, float]]:
        """
        Right arm rotation from metadata index 15.

        Returns
        -------
        Optional[tuple[float, float, float]]
            (x, y, z) rotation values, default (-15.0, 0.0, 10.0)
        """
        rotation = self.get_metadata_value(15, (-15.0, 0.0, 10.0))
        if isinstance(rotation, (list, tuple)) and len(rotation) >= 3:
            return float(rotation[0]), float(rotation[1]), float(rotation[2])
        return -15.0, 0.0, 10.0

    @property
    def left_leg_rotation(self) -> Optional[tuple[float, float, float]]:
        """
        Left leg rotation from metadata index 16.

        Returns
        -------
        Optional[tuple[float, float, float]]
            (x, y, z) rotation values, default (-1.0, 0.0, -1.0)
        """
        rotation = self.get_metadata_value(16, (-1.0, 0.0, -1.0))
        if isinstance(rotation, (list, tuple)) and len(rotation) >= 3:
            return float(rotation[0]), float(rotation[1]), float(rotation[2])
        return -1.0, 0.0, -1.0

    @property
    def right_leg_rotation(self) -> Optional[tuple[float, float, float]]:
        """
        Right leg rotation from metadata index 17.

        Returns
        -------
        Optional[tuple[float, float, float]]
            (x, y, z) rotation values, default (1.0, 0.0, 1.0)
        """
        rotation = self.get_metadata_value(17, (1.0, 0.0, 1.0))
        if isinstance(rotation, (list, tuple)) and len(rotation) >= 3:
            return float(rotation[0]), float(rotation[1]), float(rotation[2])
        return 1.0, 0.0, 1.0


class FallingBlock(Entity):
    """Falling block entity (FallingSand)."""

    __slots__ = ()
    ENTITY_TYPE = "minecraft:falling_block"

    @property
    def spawn_position(self) -> Optional[tuple[int, int, int]]:
        """
        Original spawn position from metadata index 6.

        Returns
        -------
        Optional[tuple[int, int, int]]
            (x, y, z) spawn coordinates, default (0, 0, 0)
        """
        pos = self.get_metadata_value(6, (0, 0, 0))
        if isinstance(pos, (list, tuple)) and len(pos) >= 3:
            return int(pos[0]), int(pos[1]), int(pos[2])
        return 0, 0, 0


class FireworksRocket(Entity):
    """Fireworks rocket entity."""

    __slots__ = ()
    ENTITY_TYPE = "minecraft:fireworks_rocket"

    @property
    def firework_info(self) -> Optional[Dict[str, Any]]:
        """
        Firework item stack info from metadata index 6.

        Returns
        -------
        Optional[Dict[str, Any]]
            Firework item data or None if empty
        """
        item = self.get_metadata_value(6)
        return item if item is not None else None

    @property
    def boosted_entity_id(self) -> int:
        """
        Entity ID that used firework for elytra boosting from metadata index 7.

        Returns
        -------
        int
            Entity ID of boosted entity, default 0
        """
        return int(self.get_metadata_value(7, 0))

    @property
    def is_elytra_boost(self) -> bool:
        """
        Whether this firework is being used for elytra boosting.

        Returns
        -------
        bool
            True if used for elytra boosting
        """
        return self.boosted_entity_id != 0


class TNTPrimed(Entity):
    """Primed TNT entity."""

    __slots__ = ()
    ENTITY_TYPE = "minecraft:tnt"

    @property
    def fuse_time(self) -> int:
        """
        Remaining fuse time in ticks from metadata index 6.

        Returns
        -------
        int
            Fuse time remaining, default 80 ticks
        """
        return int(self.get_metadata_value(6, 80))

    @property
    def will_explode_soon(self) -> bool:
        """
        Whether TNT will explode within 1 second.

        Returns
        -------
        bool
            True if fuse time <= 20 ticks (1 second)
        """
        return self.fuse_time <= 20


class LeashKnot(Entity):
    """Leash-knot entity attached to fences."""

    __slots__ = ()
    ENTITY_TYPE = "minecraft:leash_knot"


class EvocationFangs(Entity):
    """Evocation fangs entity created by Evoker spells."""

    __slots__ = ()
    ENTITY_TYPE = "minecraft:evocation_fangs"


class FishingHook(Entity):
    """Fishing hook/bobber entity."""

    __slots__ = ()
    ENTITY_TYPE = "minecraft:fishing_bobber"

    @property
    def hooked_entity_id(self) -> int:
        """
        ID of hooked entity from metadata index 6.

        Returns
        -------
        int
            Hooked entity ID + 1, or 0 if no entity hooked
        """
        return int(self.get_metadata_value(6, 0))

    @property
    def has_hooked_entity(self) -> bool:
        """
        Whether the fishing hook has caught an entity.

        Returns
        -------
        bool
            True if an entity is hooked
        """
        return self.hooked_entity_id > 0

    @property
    def actual_hooked_entity_id(self) -> Optional[int]:
        """
        Actual entity ID of hooked entity (subtracts 1 from stored value).

        Returns
        -------
        Optional[int]
            Real entity ID or None if no entity hooked
        """
        hook_id = self.hooked_entity_id
        return hook_id - 1 if hook_id > 0 else None


class EnderCrystal(Entity):
    """End crystal entity."""

    __slots__ = ()
    ENTITY_TYPE = "minecraft:end_crystal"

    @property
    def beam_target(self) -> Optional[tuple[int, int, int]]:
        """
        Beam target position from metadata index 6.

        Returns
        -------
        Optional[tuple[int, int, int]]
            (x, y, z) target coordinates or None if no target
        """
        target = self.get_metadata_value(6)
        if target is not None and isinstance(target, (list, tuple)) and len(target) >= 3:
            return int(target[0]), int(target[1]), int(target[2])
        return None

    @property
    def show_bottom(self) -> bool:
        """
        Whether to show crystal bottom from metadata index 7.

        Returns
        -------
        bool
            True if bottom should be shown, default True
        """
        return bool(self.get_metadata_value(7, True))

    @property
    def has_beam_target(self) -> bool:
        """
        Whether the crystal has a beam target.

        Returns
        -------
        bool
            True if beam target is set
        """
        return self.beam_target is not None