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

__all__ = ('Golem', 'IronGolem', 'Snowman')


class Golem(Creature):
    """
    Base golem entity extending Creature.

    This is the base class for all golem-type entities in Minecraft,
    providing common functionality for constructed entities.
    """

    __slots__ = ()


class IronGolem(Golem):
    """
    Iron golem entity (VillagerGolem).

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for iron golems.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the iron golem.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = "minecraft:villager_golem"
    BOUNDING: ClassVar[Tuple[float, float]] = (1.4, 2.7)

    @property
    def is_player_created(self) -> bool:
        """
        Whether iron golem is player-created.

        Returns
        -------
        bool
            True if the iron golem was created by a player, False if spawned naturally.
        """
        return bool(self.get_metadata_value(12, 0) & 0x01)


class Snowman(Golem):
    """
    Snow golem entity (SnowGolem).

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for snow golems.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the snow golem.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = "minecraft:snowman"
    BOUNDING: ClassVar[Tuple[float, float]] = (0.7, 1.9)

    @property
    def has_pumpkin_hat(self) -> bool:
        """
        Whether snowman has pumpkin hat.

        Returns
        -------
        bool
            True if the snowman is wearing a pumpkin hat, False otherwise.
        """
        return bool(self.get_metadata_value(12, 0x10) & 0x10)