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
    from typing import ClassVar, Tuple

__all__ = ('AbstractIllager', 'SpellcasterIllager', 'VindicationIllager', 'EvocationIllager', 'IllusionIllager')

class AbstractIllager(Creature):
    """Abstract Illager entity extending Creature."""

    __slots__ = ()

    @property
    def has_target(self) -> bool:
        """
        Whether illager has target (aggressive state).

        Returns
        -------
        bool
            True if illager has a target (bit 0), False otherwise.
        """
        return bool(self.get_metadata_value(12, 0) & 0x01)

class SpellcasterIllager(AbstractIllager):
    """Spellcaster Illager entity extending Abstract Illager."""

    __slots__ = ()

    @property
    def spell(self) -> int:
        """
        Current spell.

        Returns
        -------
        int
            Current spell (0: none, 1: summon vex, 2: attack, 3: wololo).
        """
        return int(self.get_metadata_value(13, 0))

class VindicationIllager(AbstractIllager):
    """
    Vindicator illager entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for vindicators.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the vindicator.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:vindication_illager'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.6, 1.95)

class EvocationIllager(SpellcasterIllager):
    """
    Evoker illager entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for evokers.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the evoker.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:evocation_illager'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.6, 1.95)

class IllusionIllager(SpellcasterIllager):
    """
    Illusioner illager entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for illusioners.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the illusioner.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:illusion_illager'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.6, 1.95)