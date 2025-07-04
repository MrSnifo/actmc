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

from .entity import Entity, Living

if TYPE_CHECKING:
    from typing import ClassVar, Tuple, Optional, Dict, Any
    from ..types.entities import ItemData

__all__ = ('DroppedItem', 'Item', 'XPOrb', 'LightningBolt', 'AreaEffectCloud', 'ArmorStand', 'FallingBlock',
           'FireworksRocket', 'TNTPrimed', 'LeashKnot', 'EvocationFangs', 'FishingHook', 'EnderCrystal')


class Item:
    """Represents a Minecraft item."""

    __slots__ = ('id', 'count', 'damage', 'nbt')

    def __init__(self, item_id: int, count: int = 1, item_damage: int = 0,
                 nbt: Optional[Dict[str, Any]] = None) -> None:
        self.id: int = item_id
        self.count: int = count
        self.damage: int = item_damage
        self.nbt: Optional[Dict[str, Any]] = nbt


    @property
    def has_nbt(self) -> bool:
        """
        Check if this item has NBT data.

        Returns
        -------
        bool
            True if NBT data is present
        """
        return self.nbt is not None and self.nbt != {}

    @property
    def is_damaged(self) -> bool:
        """
        Check if this item has damage (for tools/armor).

        Returns
        -------
        bool
            True if damage > 0
        """
        return self.damage > 0

    @property
    def is_enchanted(self) -> bool:
        """
        Check if this item has enchantments.

        Returns
        -------
        bool
            True if item has enchantment NBT data
        """
        if not self.has_nbt:
            return False

        # Check for both possible enchantment tags
        return ('Enchantments' in self.nbt or
                'StoredEnchantments' in self.nbt or
                'ench' in self.nbt)  # Legacy format

    def get_enchantments(self) -> list[Dict[str, int]]:
        """
        Get enchantments from NBT data.

        Returns
        -------
        list[Dict[str, int]]
            List of enchantment dictionaries with 'id' and 'lvl' keys
        """
        if not self.has_nbt:
            return []

        enchants = []
        for key in ['Enchantments', 'StoredEnchantments', 'ench']:
            if key in self.nbt and isinstance(self.nbt[key], list):
                for ench in self.nbt[key]:
                    if isinstance(ench, dict) and 'id' in ench and 'lvl' in ench:
                        enchants.append({
                            'id': ench['id'],
                            'lvl': ench['lvl']
                        })

        return enchants

    def to_dict(self) -> ItemData:
        """
        Convert the item to ItemData format.

        Returns
        -------
        ItemData
            Dictionary containing item data
        """
        return {
            'item_id': self.id,
            'item_damage': self.damage,
            'item_count': self.count,
            'nbt': self.nbt
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, count={self.count}>"

    def __eq__(self, other: object) -> bool:
        """Check equality with another Item."""
        if not isinstance(other, Item):
            return False

        return self.id == other.id and self.damage == other.damage and self.nbt == other.nbt


class DroppedItem(Entity):
    """
    Item entity representing a dropped item in the world.

    The entity does not include the item data when initially created.
    The item it holds must be received through a metadata update packet.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for items.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the item.
    """

    __slots__ = ()


    ENTITY_TYPE: ClassVar[str] = 'minecraft:item'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.25, 0.25)

    @property
    def _item_stack_data(self) -> Optional[Dict[str, Any]]:
        """
        Raw item stack data from metadata.

        Returns
        -------
        Optional[Dict[str, Any]]
            Raw item stack information or None if empty.
        """
        item = self.get_metadata_value(6)
        return item if item is not None else None

    @property
    def item(self) -> Optional[Item]:
        """
        Item instance representing the dropped item.

        Returns
        -------
        Optional[Item]
            Item instance or None if no item data available.
        """
        data = self._item_stack_data

        if data:
            return Item(data.get('item_id', 0), data.get('item_count', 0), data.get('item_damage', 0),
                        data.get('nbt', None))
        return None

    @property
    def has_item(self) -> bool:
        """
        Whether the item entity contains an item stack.

        Returns
        -------
        bool
            True if item stack is present.
        """
        return self._item_stack_data is not None


class XPOrb(Entity):
    """
    Experience orb entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for experience orbs.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the experience orb.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:xp_orb'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.5, 0.5)

    @property
    def count(self) -> float:
        """
        The amount of experience this orb will reward once collected.

        Returns
        -------
        float
            Experience amount.
        """
        return float(self.get_metadata_value(-1, 0.0))

class LightningBolt(Entity):
    """
    Lightning bolt entity.

    This entity is not stored in the entity registry, as it is ephemeral.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for lightning bolts.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the lightning bolt.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:lightning_bolt'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.0, 0.0)  # Lightning has no collision

    @property
    def type(self) -> int:
        """
        The global entity type, currently always 1 for thunderbolt.

        Returns
        -------
        int
            Global entity type.
        """
        return int(self.get_metadata_value(-1, 1))

class AreaEffectCloud(Entity):
    """
    Area effect cloud entity for potion effects and particles.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for area effect clouds.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the area effect cloud.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:area_effect_cloud'
    BOUNDING: ClassVar[Tuple[float, float]] = (2.0, 0.5)  # 2.0 * Radius

    @property
    def radius(self) -> float:
        """
        Effect cloud radius.

        Returns
        -------
        float
            Cloud radius in blocks.5.
        """
        return float(self.get_metadata_value(6, 0.5))

    @property
    def color(self) -> int:
        """
        Effect cloud color.

        Returns
        -------
        int
            Color value for mob spell particle.
        """
        return int(self.get_metadata_value(7, 0))

    @property
    def ignore_radius(self) -> bool:
        """
        Whether to ignore radius and show as single point.

        Returns
        -------
        bool
            True if should show as single point.
        """
        return bool(self.get_metadata_value(8, False))

    @property
    def particle_id(self) -> int:
        """
        Particle type ID.

        Returns
        -------
        int
            Particle ID, default 15 (mobSpell).
        """
        return int(self.get_metadata_value(9, 15))

    @property
    def particle_param1(self) -> int:
        """
        First particle parameter.

        Returns
        -------
        int
            Particle parameter 1.
        """
        return int(self.get_metadata_value(10, 0))

    @property
    def particle_param2(self) -> int:
        """
        Second particle parameter.

        Returns
        -------
        int
            Particle parameter 2.
        """
        return int(self.get_metadata_value(11, 0))

class ArmorStand(Living):
    """
    Armor stand entity extending Living.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for armor stands.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the armor stand.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:armor_stand'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.5, 1.975)  # Normal size

    @property
    def _armor_stand_bit_mask(self) -> int:
        """
        Armor stand bit mask.

        Returns
        -------
        int
            Bit mask flags.
        """
        return int(self.get_metadata_value(11, 0))

    @property
    def is_small(self) -> bool:
        """
        Whether armor stand is small size (bit 0).

        Returns
        -------
        bool
            True if small size.
        """
        return bool(self._armor_stand_bit_mask & 0x01)

    @property
    def has_arms(self) -> bool:
        """
        Whether armor stand has arms (bit 2).

        Returns
        -------
        bool
            True if has arms.
        """
        return bool(self._armor_stand_bit_mask & 0x04)

    @property
    def has_base_plate(self) -> bool:
        """
        Whether armor stand has baseplate (bit 3 inverted).

        Returns
        -------
        bool
            True if it has baseplate.
        """
        return not bool(self._armor_stand_bit_mask & 0x08)

    @property
    def is_marker(self) -> bool:
        """
        Whether armor stand is marker (bit 4).

        Returns
        -------
        bool
            True if is marker.
        """
        return bool(self._armor_stand_bit_mask & 0x10)

    @property
    def head_rotation(self) -> tuple[float, float, float]:
        """
        Head rotation.

        Returns
        -------
        tuple[float, float, float]
            (x, y, z) rotation values, default (0.0, 0.0, 0.0).
        """
        rotation = self.get_metadata_value(12, (0.0, 0.0, 0.0))
        if isinstance(rotation, (list, tuple)) and len(rotation) >= 3:
            return float(rotation[0]), float(rotation[1]), float(rotation[2])
        return 0.0, 0.0, 0.0

    @property
    def body_rotation(self) -> tuple[float, float, float]:
        """
        Body rotation.

        Returns
        -------
        tuple[float, float, float]
            (x, y, z) rotation values, default (0.0, 0.0, 0.0).
        """
        rotation = self.get_metadata_value(13, (0.0, 0.0, 0.0))
        if isinstance(rotation, (list, tuple)) and len(rotation) >= 3:
            return float(rotation[0]), float(rotation[1]), float(rotation[2])
        return 0.0, 0.0, 0.0

    @property
    def left_arm_rotation(self) -> tuple[float, float, float]:
        """
        Left arm rotation.

        Returns
        -------
        tuple[float, float, float]
            (x, y, z) rotation values, default (-10.0, 0.0, -10.0).
        """
        rotation = self.get_metadata_value(14, (-10.0, 0.0, -10.0))
        if isinstance(rotation, (list, tuple)) and len(rotation) >= 3:
            return float(rotation[0]), float(rotation[1]), float(rotation[2])
        return -10.0, 0.0, -10.0

    @property
    def right_arm_rotation(self) -> tuple[float, float, float]:
        """
        Right arm rotation.

        Returns
        -------
        tuple[float, float, float]
            (x, y, z) rotation values, default (-15.0, 0.0, 10.0).
        """
        rotation = self.get_metadata_value(15, (-15.0, 0.0, 10.0))
        if isinstance(rotation, (list, tuple)) and len(rotation) >= 3:
            return float(rotation[0]), float(rotation[1]), float(rotation[2])
        return -15.0, 0.0, 10.0

    @property
    def left_leg_rotation(self) -> tuple[float, float, float]:
        """
        Left leg rotation.

        Returns
        -------
        tuple[float, float, float]
            (x, y, z) rotation values, default (-1.0, 0.0, -1.0).
        """
        rotation = self.get_metadata_value(16, (-1.0, 0.0, -1.0))
        if isinstance(rotation, (list, tuple)) and len(rotation) >= 3:
            return float(rotation[0]), float(rotation[1]), float(rotation[2])
        return -1.0, 0.0, -1.0

    @property
    def right_leg_rotation(self) -> tuple[float, float, float]:
        """
        Right leg rotation.

        Returns
        -------
        tuple[float, float, float]
            (x, y, z) rotation values, default (1.0, 0.0, 1.0).
        """
        rotation = self.get_metadata_value(17, (1.0, 0.0, 1.0))
        if isinstance(rotation, (list, tuple)) and len(rotation) >= 3:
            return float(rotation[0]), float(rotation[1]), float(rotation[2])
        return 1.0, 0.0, 1.0

class FallingBlock(Entity):
    """
    Falling block entity (FallingSand).

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for falling blocks.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the falling block.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:falling_block'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.98, 0.98)

    @property
    def _block_type_raw(self) -> int:
        """
        Returns the raw block type integer from metadata.

        Returns
        -------
        int
            The raw encoded block type.
        """
        return self.get_metadata_value(-1, 0)

    @property
    def block_id(self) -> int:
        """
        Extracts the block ID from the raw block type integer.

        Returns
        -------
        int
            The block ID.
        """
        return self._block_type_raw & 0xFFF

    @property
    def block_metadata(self) -> int:
        """
        Extracts the block metadata from the raw block type integer.

        Returns
        -------
        int
            The block metadata.
        """
        return self._block_type_raw >> 12

    @property
    def spawn_position(self) -> tuple[int, int, int]:
        """
        Original spawn position.

        Returns
        -------
        tuple[int, int, int]
            (x, y, z) spawn coordinates, default (0, 0, 0).
        """
        pos = self.get_metadata_value(6, (0, 0, 0))
        if isinstance(pos, (list, tuple)) and len(pos) >= 3:
            return int(pos[0]), int(pos[1]), int(pos[2])
        return 0, 0, 0

class FireworksRocket(Entity):
    """
    Fireworks rocket entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for fireworks rockets.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the fireworks rocket.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:fireworks_rocket'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.25, 0.25)

    @property
    def firework_info(self) -> Optional[Dict[str, Any]]:
        """
        Firework item stack info.

        Returns
        -------
        Optional[Dict[str, Any]]
            Firework item data or None if empty.
        """
        item = self.get_metadata_value(6)
        return item if item is not None else None

    @property
    def boosted_entity_id(self) -> int:
        """
        Entity ID that used firework for elytra boosting.

        Returns
        -------
        int
            Entity ID of boosted entity.
        """
        return int(self.get_metadata_value(7, 0))

    @property
    def is_elytra_boost(self) -> bool:
        """
        Whether this firework is being used for elytra boosting.

        Returns
        -------
        bool
            True if used for elytra boosting.
        """
        return self.boosted_entity_id != 0

class TNTPrimed(Entity):
    """
    Primed TNT entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for primed TNT.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the primed TNT.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:tnt'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.98, 0.98)

    @property
    def fuse_time(self) -> int:
        """
        Remaining fuse time in ticks.

        Returns
        -------
        int
            Fuse time remaining.
        """
        return int(self.get_metadata_value(6, 80))

    @property
    def will_explode_soon(self) -> bool:
        """
        Whether TNT will explode within 1 second.

        Returns
        -------
        bool
            True if fuse time <= 20 ticks (1 second).
        """
        return self.fuse_time <= 20

class LeashKnot(Entity):
    """
    Leash-knot entity attached to fences.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for leash knots.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the leash knot.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:leash_knot'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.375, 0.5)

class EvocationFangs(Entity):
    """
    Evocation fangs entity created by Evoker spells.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for evocation fangs.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the evocation fangs.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:evocation_fangs'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.5, 0.8)

class FishingHook(Entity):
    """
    Fishing hook/bobber entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for fishing hooks.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the fishing hook.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:fishing_bobber'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.25, 0.25)  # Estimated

    @property
    def owner_id(self) -> int:
        """
        Returns the entity ID of the owner who cast the fishing hook.

        Returns
        -------
        int
            The entity ID of the owner.
        """
        return self.get_metadata_value(-1, 0)

    @property
    def hooked_entity_id(self) -> int:
        """
        ID of hooked entity.

        Returns
        -------
        int
            Hooked entity ID + 1, or 0 if no entity hooked.
        """
        return int(self.get_metadata_value(6, 0))

    @property
    def has_hooked_entity(self) -> bool:
        """
        Whether the fishing hook has caught an entity.

        Returns
        -------
        bool
            True if an entity is hooked.
        """
        return self.hooked_entity_id > 0

    @property
    def actual_hooked_entity_id(self) -> Optional[int]:
        """
        Actual entity ID of hooked entity (subtracts 1 from stored value).

        Returns
        -------
        Optional[int]
            Real entity ID or None if no entity hooked.
        """
        hook_id = self.hooked_entity_id
        return hook_id - 1 if hook_id > 0 else None

class EnderCrystal(Entity):
    """
    End crystal entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for end crystals.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the end crystal.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:end_crystal'
    BOUNDING: ClassVar[Tuple[float, float]] = (2.0, 2.0)

    @property
    def beam_target(self) -> Optional[tuple[int, int, int]]:
        """
        Beam target position.

        Returns
        -------
        Optional[tuple[int, int, int]]
            (x, y, z) target coordinates or None if no target.
        """
        target = self.get_metadata_value(6)
        if target is not None and isinstance(target, (list, tuple)) and len(target) >= 3:
            return int(target[0]), int(target[1]), int(target[2])
        return None

    @property
    def show_bottom(self) -> bool:
        """
        Whether to show crystal bottom.

        Returns
        -------
        bool
            True if bottom should be shown.
        """
        return bool(self.get_metadata_value(7, True))

    @property
    def has_beam_target(self) -> bool:
        """
        Whether the crystal has a beam target.

        Returns
        -------
        bool
            True if beam target is set.
        """
        return self.beam_target is not None