from __future__ import annotations

from typing import Dict, Any, Optional
from .entity import Creature

__all__ = ('Ageable', 'AbstractHorse', 'ChestedHorse', 'Pig', 'Sheep', 'Cow', 'Chicken', 'Rabbit', 'PolarBear',
           'MushroomCow', 'Horse', 'ZombieHorse', 'SkeletonHorse', 'Donkey', 'Llama', 'Mule')

class Ageable(Creature):
    """Ageable mob entity extending Creature."""
    __slots__ = ()

    @property
    def is_baby(self) -> bool:
        """Whether entity is a baby from metadata index 12."""
        return bool(self.get_metadata_value(12, False))

class AbstractHorse(Ageable):
    """AbstractHorse entity extending Animal."""
    __slots__ = ()

    @property
    def _horse_bit_mask(self) -> int:
        """Horse-specific bit mask from metadata index 13."""
        return int(self.get_metadata_value(13, 0))

    @property
    def owner_uuid(self) -> Optional[str]:
        """Owner UUID from metadata index 14."""
        owner = self.get_metadata_value(14)
        return str(owner) if owner is not None else None

    @property
    def is_tame(self) -> bool:
        """Whether horse is tame (bit 1)."""
        return bool(self._horse_bit_mask & 0x02)

    @property
    def is_saddled(self) -> bool:
        """Whether horse is saddled (bit 2)."""
        return bool(self._horse_bit_mask & 0x04)

    @property
    def has_bred(self) -> bool:
        """Whether horse has bred (bit 3)."""
        return bool(self._horse_bit_mask & 0x08)

    @property
    def is_eating(self) -> bool:
        """Whether horse is eating (bit 4)."""
        return bool(self._horse_bit_mask & 0x10)

    @property
    def is_rearing(self) -> bool:
        """Whether horse is rearing (bit 5)."""
        return bool(self._horse_bit_mask & 0x20)

    @property
    def is_mouth_open(self) -> bool:
        """Whether horse's mouth is open (bit 6)."""
        return bool(self._horse_bit_mask & 0x40)

class ChestedHorse(AbstractHorse):
    """ChestedHorse entity extending AbstractHorse."""
    __slots__ = ()

    @property
    def has_chest(self) -> bool:
        """Whether horse has chest from metadata index 15."""
        return bool(self.get_metadata_value(15, False))

class Pig(Ageable):
    """Pig entity extending Animal."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:pig"

    @property
    def has_saddle(self) -> bool:
        """Whether pig has saddle from metadata index 13."""
        return bool(self.get_metadata_value(13, False))

    @property
    def boost_time(self) -> int:
        """Total time to boost with carrot on a stick from metadata index 14."""
        return int(self.get_metadata_value(14, 0))

class Sheep(Ageable):
    """Sheep entity extending Animal."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:sheep"

    @property
    def _sheep_bit_mask(self) -> int:
        """Sheep-specific bit mask from metadata index 13."""
        return int(self.get_metadata_value(13, 0))

    @property
    def color(self) -> int:
        """Wool color (matches dye damage values) from bits 0-3."""
        return self._sheep_bit_mask & 0x0F

    @property
    def is_sheared(self) -> bool:
        """Whether sheep is sheared from bit 4."""
        return bool(self._sheep_bit_mask & 0x10)

class Cow(Ageable):
    """Cow entity extending Animal."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:cow"

    # Cow has no additional metadata beyond Animal

class Chicken(Ageable):
    """Chicken entity extending Animal."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:chicken"

    # Chicken has no additional metadata beyond Animal

class Rabbit(Ageable):
    """Rabbit entity extending Animal."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:rabbit"

    @property
    def rabbit_type(self) -> int:
        """Rabbit type from metadata index 13."""
        return int(self.get_metadata_value(13, 0))

class PolarBear(Ageable):
    """Polar Bear entity extending Animal."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:polar_bear"

    @property
    def is_standing_up(self) -> bool:
        """Whether polar bear is standing up from metadata index 13."""
        return bool(self.get_metadata_value(13, False))

class MushroomCow(Ageable):
    """Mooshroom entity extending Animal."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:mooshroom"

class Horse(AbstractHorse):
    """Horse entity extending AbstractHorse."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:horse"

    @property
    def variant(self) -> int:
        """Horse variant (color & style) from metadata index 15."""
        return int(self.get_metadata_value(15, 0))

    @property
    def armor_type(self) -> int:
        """Horse armor type from metadata index 16 (0: none, 1: iron, 2: gold, 3: diamond)."""
        return int(self.get_metadata_value(16, 0))

    @property
    def armor_item(self) -> Optional[Dict[str, Any]]:
        """Armor item slot from metadata index 17 (Forge only)."""
        return self.get_metadata_value(17)

class ZombieHorse(AbstractHorse):
    """Zombie Horse entity extending AbstractHorse."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:zombie_horse"

class SkeletonHorse(AbstractHorse):
    """Skeleton Horse entity extending AbstractHorse."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:skeleton_horse"

class Donkey(ChestedHorse):
    """Donkey entity extending ChestedHorse."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:donkey"

class Llama(ChestedHorse):
    """Llama entity extending ChestedHorse."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:llama"

    @property
    def strength(self) -> int:
        """Number of columns of 3 slots in inventory once chest is equipped from metadata index 16."""
        return int(self.get_metadata_value(16, 0))

    @property
    def carpet_color(self) -> int:
        """Carpet color (dye color, or -1 if no carpet) from metadata index 17."""
        return int(self.get_metadata_value(17, -1))

    @property
    def variant(self) -> int:
        """Llama variant from metadata index 18 (0: creamy, 1: white, 2: brown, 3: gray)."""
        return int(self.get_metadata_value(18, 0))

class Mule(ChestedHorse):
    """Mule entity extending ChestedHorse."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:mule"
