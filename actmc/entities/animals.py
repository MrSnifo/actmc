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
from .entity import Creature

if TYPE_CHECKING:
    from typing import Dict, Any, Optional, Tuple
    from typing import ClassVar

__all__ = ('Ageable', 'AbstractHorse', 'ChestedHorse', 'Pig', 'Sheep', 'Cow', 'Chicken', 'Rabbit', 'PolarBear',
           'MushroomCow', 'Horse', 'ZombieHorse', 'SkeletonHorse', 'Donkey', 'Llama', 'Mule')

class Ageable(Creature):
    """Base class for ageable mob entities."""

    __slots__ = ()

    @property
    def is_baby(self) -> bool:
        """
        Whether the entity is currently in baby form.

        Returns
        -------
        bool
            True if the entity is a baby, False if adult.
        """
        return bool(self.get_metadata_value(12, False))


class AbstractHorse(Ageable):
    """Abstract base class for horse-type entities."""

    __slots__ = ()

    @property
    def _horse_bit_mask(self) -> int:
        """Internal bit mask containing horse-specific flags."""
        return int(self.get_metadata_value(13, 0))

    @property
    def owner_uuid(self) -> Optional[str]:
        """
        UUID of the player who owns this horse.

        Returns
        -------
        Optional[str]
            Owner's UUID string if tamed, None if wild.
        """
        owner = self.get_metadata_value(14)
        return str(owner) if owner is not None else None

    @property
    def is_tame(self) -> bool:
        """
        Whether the horse has been tamed by a player.

        Returns
        -------
        bool
            True if tamed, False if wild.
        """
        return bool(self._horse_bit_mask & 0x02)

    @property
    def is_saddled(self) -> bool:
        """
        Whether the horse is currently equipped with a saddle.

        Returns
        -------
        bool
            True if saddled, False otherwise.
        """
        return bool(self._horse_bit_mask & 0x04)

    @property
    def has_bred(self) -> bool:
        """
        Whether the horse has been bred at least once.

        Returns
        -------
        bool
            True if has bred, False otherwise.
        """
        return bool(self._horse_bit_mask & 0x08)

    @property
    def is_eating(self) -> bool:
        """
        Whether the horse is currently eating.

        Returns
        -------
        bool
            True if eating, False otherwise.
        """
        return bool(self._horse_bit_mask & 0x10)

    @property
    def is_rearing(self) -> bool:
        """
        Whether the horse is rearing up on its hind legs.

        Returns
        -------
        bool
            True if rearing, False otherwise.
        """
        return bool(self._horse_bit_mask & 0x20)

    @property
    def is_mouth_open(self) -> bool:
        """
        Whether the horse's mouth is currently open.

        Returns
        -------
        bool
            True if mouth open, False otherwise.
        """
        return bool(self._horse_bit_mask & 0x40)


class ChestedHorse(AbstractHorse):
    """Base class for horse entities that can carry chests."""

    __slots__ = ()

    @property
    def has_chest(self) -> bool:
        """
        Whether the horse is currently equipped with a chest.

        Returns
        -------
        bool
            True if carrying a chest, False otherwise.
        """
        return bool(self.get_metadata_value(15, False))


class Pig(Ageable):
    """
    Pig entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for pigs.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the pig.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = "minecraft:pig"
    BOUNDING: ClassVar[Tuple[float, float]] = (0.9, 0.9)

    @property
    def has_saddle(self) -> bool:
        """
        Whether the pig is equipped with a saddle for riding.

        Returns
        -------
        bool
            True if saddled, False otherwise.
        """
        return bool(self.get_metadata_value(13, False))

    @property
    def boost_time(self) -> int:
        """
        Total time remaining for carrot on stick boost effect.

        Returns
        -------
        int
            Boost time in ticks, 0 if not boosting.
        """
        return int(self.get_metadata_value(14, 0))


class Sheep(Ageable):
    """
    Sheep entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for sheep.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the sheep.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = "minecraft:sheep"
    BOUNDING: ClassVar[Tuple[float, float]] = (0.9, 1.3)

    @property
    def _sheep_bit_mask(self) -> int:
        """Internal bit mask containing sheep-specific flags and color data."""
        return int(self.get_metadata_value(13, 0))

    @property
    def color(self) -> int:
        """
        The wool color of the sheep.

        Returns
        -------
        int
            Color ID matching dye damage values (0-15).
        """
        return self._sheep_bit_mask & 0x0F

    @property
    def is_sheared(self) -> bool:
        """
        Whether the sheep has been sheared and is growing wool back.

        Returns
        -------
        bool
            True if recently sheared, False if wool has grown back.
        """
        return bool(self._sheep_bit_mask & 0x10)


class Cow(Ageable):
    """
    Cow entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for cows.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the cow.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = "minecraft:cow"
    BOUNDING: ClassVar[Tuple[float, float]] = (0.9, 1.4)


class Chicken(Ageable):
    """
    Chicken entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for chickens.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the chicken.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = "minecraft:chicken"
    BOUNDING: ClassVar[Tuple[float, float]] = (0.4, 0.7)


class Rabbit(Ageable):
    """
    Rabbit entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for rabbits.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the rabbit.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = "minecraft:rabbit"
    BOUNDING: ClassVar[Tuple[float, float]] = (0.4, 0.5)

    @property
    def rabbit_type(self) -> int:
        """
        The visual variant type of the rabbit.

        Returns
        -------
        int
            Rabbit type ID determining appearance and behavior.
        """
        return int(self.get_metadata_value(13, 0))


class PolarBear(Ageable):
    """
    Polar Bear entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for polar bears.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the polar bear.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = "minecraft:polar_bear"
    BOUNDING: ClassVar[Tuple[float, float]] = (1.3, 1.4)

    @property
    def is_standing_up(self) -> bool:
        """
        Whether the polar bear is standing on its hind legs.

        Returns
        -------
        bool
            True if standing up, False if on all fours.
        """
        return bool(self.get_metadata_value(13, False))


class MushroomCow(Ageable):
    """
    Mooshroom entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for mooshrooms.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the mooshroom.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = "minecraft:mooshroom"
    BOUNDING: ClassVar[Tuple[float, float]] = (0.9, 1.4)


class Horse(AbstractHorse):
    """
    Horse entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for horses.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the horse.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = "minecraft:horse"
    BOUNDING: ClassVar[Tuple[float, float]] = (1.3964844, 1.6)

    @property
    def variant(self) -> int:
        """
        The visual variant combining color and markings.

        Returns
        -------
        int
            Variant ID determining the horse's appearance.
        """
        return int(self.get_metadata_value(15, 0))

    @property
    def armor_type(self) -> int:
        """
        The type of armor currently equipped on the horse.

        Returns
        -------
        int
            Armor type (0: none, 1: iron, 2: gold, 3: diamond).
        """
        return int(self.get_metadata_value(16, 0))

    @property
    def armor_item(self) -> Optional[Dict[str, Any]]:
        """
        The armor item data currently equipped.

        Returns
        -------
        Optional[Dict[str, Any]]
            Armor item data if equipped, None otherwise. (Forge only)
        """
        return self.get_metadata_value(17)


class ZombieHorse(AbstractHorse):
    """
    Zombie Horse entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for zombie horses.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the zombie horse.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = "minecraft:zombie_horse"
    BOUNDING: ClassVar[Tuple[float, float]] = (1.3964844, 1.6)


class SkeletonHorse(AbstractHorse):
    """
    Skeleton Horse entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for skeleton horses.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the skeleton horse.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = "minecraft:skeleton_horse"
    BOUNDING: ClassVar[Tuple[float, float]] = (1.3964844, 1.6)


class Donkey(ChestedHorse):
    """
    Donkey entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for donkeys.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the donkey.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = "minecraft:donkey"
    BOUNDING: ClassVar[Tuple[float, float]] = (1.3964844, 1.6)


class Llama(ChestedHorse):
    """
    Llama entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for llamas.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the llama.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = "minecraft:llama"
    BOUNDING: ClassVar[Tuple[float, float]] = (0.9, 1.87)

    @property
    def strength(self) -> int:
        """
        Number of columns of inventory slots when chest is equipped.

        Returns
        -------
        int
            Inventory strength (columns of 3 slots each).
        """
        return int(self.get_metadata_value(16, 0))

    @property
    def carpet_color(self) -> int:
        """
        The color of carpet decoration on the llama.

        Returns
        -------
        int
            Carpet color ID matching dye colors, or -1 if no carpet.
        """
        return int(self.get_metadata_value(17, -1))

    @property
    def variant(self) -> int:
        """
        The visual variant of the llama.

        Returns
        -------
        int
            Variant ID (0: creamy, 1: white, 2: brown, 3: gray).
        """
        return int(self.get_metadata_value(18, 0))


class Mule(ChestedHorse):
    """
    Mule entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for mules.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the mule.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = "minecraft:mule"
    BOUNDING: ClassVar[Tuple[float, float]] = (1.3964844, 1.6)