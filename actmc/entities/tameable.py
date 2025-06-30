from __future__ import annotations

from typing import Optional
from .entity import Creature

__all__ = ('TameableAnimal', 'Wolf', 'Ocelot', 'Parrot')

class TameableAnimal(Creature):
    """Tameable animal entity extending Animal."""
    __slots__ = ()

    @property
    def _tameable_bit_mask(self) -> int:
        """Tameable-specific bit mask from metadata index 13."""
        return int(self.get_metadata_value(13, 0))

    @property
    def owner_uuid(self) -> Optional[str]:
        """Owner UUID from metadata index 14."""
        owner = self.get_metadata_value(14)
        return str(owner) if owner is not None else None

    @property
    def is_sitting(self) -> bool:
        """Whether animal is sitting (bit 0)."""
        return bool(self._tameable_bit_mask & 0x01)

    @property
    def is_angry(self) -> bool:
        """Whether animal is angry (bit 1)."""
        return bool(self._tameable_bit_mask & 0x02)

    @property
    def is_tamed(self) -> bool:
        """Whether animal is tamed (bit 2)."""
        return bool(self._tameable_bit_mask & 0x04)

    @property
    def has_owner(self) -> bool:
        """Whether animal has an owner."""
        return self.owner_uuid is not None

class Wolf(TameableAnimal):
    """Wolf entity extending TameableAnimal."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:wolf"

    @property
    def damage_taken(self) -> float:
        """Damage taken (used for tail rotation) from metadata index 15."""
        return float(self.get_metadata_value(15, self.health))

    @property
    def is_begging(self) -> bool:
        """Whether wolf is begging from metadata index 16."""
        return bool(self.get_metadata_value(16, False))

    @property
    def collar_color(self) -> int:
        """Collar color (dye values) from metadata index 17."""
        return int(self.get_metadata_value(17, 14))  # Default: Red (14)

class Ocelot(TameableAnimal):
    """Ocelot entity extending TameableAnimal."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:ocelot"

    @property
    def ocelot_type(self) -> int:
        """Ocelot type from metadata index 15 (0: untamed, 1: tuxedo, 2: tabby, 3: siamese)."""
        return int(self.get_metadata_value(15, 0))

class Parrot(TameableAnimal):
    """Parrot entity extending TameableAnimal."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:parrot"

    @property
    def variant(self) -> int:
        """Parrot variant from metadata index 15 (0: red/blue, 1: blue, 2: green, 3: yellow/blue, 4: silver)."""
        return int(self.get_metadata_value(15, 0))
