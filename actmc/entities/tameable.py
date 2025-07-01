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

from typing import TYPE_CHECKING, Optional
from .entity import Creature

if TYPE_CHECKING:
    from typing import ClassVar, Tuple

__all__ = ('TameableAnimal', 'Wolf', 'Ocelot', 'Parrot')


class TameableAnimal(Creature):
    """Base tameable animal entity class."""

    __slots__ = ()

    @property
    def _tameable_bit_mask(self) -> int:
        """Tameable-specific bit mask."""
        return int(self.get_metadata_value(13, 0))

    @property
    def owner_uuid(self) -> Optional[str]:
        """
        Owner UUID.

        Returns
        -------
        Optional[str]
            The UUID of the owner, None if not owned.
        """
        owner = self.get_metadata_value(14)
        return str(owner) if owner is not None else None

    @property
    def is_sitting(self) -> bool:
        """
        Whether animal is sitting (bit 0).

        Returns
        -------
        bool
            True if the animal is sitting, False otherwise.
        """
        return bool(self._tameable_bit_mask & 0x01)

    @property
    def is_angry(self) -> bool:
        """
        Whether animal is angry (bit 1).

        Returns
        -------
        bool
            True if the animal is angry, False otherwise.
        """
        return bool(self._tameable_bit_mask & 0x02)

    @property
    def is_tamed(self) -> bool:
        """
        Whether animal is tamed (bit 2).

        Returns
        -------
        bool
            True if the animal is tamed, False otherwise.
        """
        return bool(self._tameable_bit_mask & 0x04)

    @property
    def has_owner(self) -> bool:
        """
        Whether animal has an owner.

        Returns
        -------
        bool
            True if the animal has an owner, False otherwise.
        """
        return self.owner_uuid is not None


class Wolf(TameableAnimal):
    """
    Wolf entity extending TameableAnimal.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for wolves.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the wolf.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:wolf'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.6, 0.85)

    @property
    def damage_taken(self) -> float:
        """
        Damage taken (used for tail rotation).

        Returns
        -------
        float
            The amount of damage taken, defaults to current health.
        """
        return float(self.get_metadata_value(15, self.health))

    @property
    def is_begging(self) -> bool:
        """
        Whether wolf is begging.

        Returns
        -------
        bool
            True if the wolf is begging, False otherwise.
        """
        return bool(self.get_metadata_value(16, False))

    @property
    def collar_color(self) -> int:
        """
        Collar color (dye values).

        Returns
        -------
        int
            The collar color ID (default: 14 for red).
        """
        return int(self.get_metadata_value(17, 14))  # Default: Red (14)


class Ocelot(TameableAnimal):
    """
    Ocelot entity extending TameableAnimal.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for ocelots.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the ocelot.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:ocelot'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.6, 0.7)

    @property
    def ocelot_type(self) -> int:
        """
        Ocelot type.

        Returns
        -------
        int
            The ocelot type (0: untamed, 1: tuxedo, 2: tabby, 3: siamese).
        """
        return int(self.get_metadata_value(15, 0))


class Parrot(TameableAnimal):
    """
    Parrot entity extending TameableAnimal.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for parrots.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the parrot.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:parrot'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.5, 0.9)

    @property
    def variant(self) -> int:
        """
        Parrot variant.

        Returns
        -------
        int
            The parrot variant (0: red/blue, 1: blue, 2: green, 3: yellow/blue, 4: silver).
        """
        return int(self.get_metadata_value(15, 0))