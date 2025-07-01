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
from .entity import Insentient

if TYPE_CHECKING:
    from typing import ClassVar, Tuple

__all__ = ('EnderDragon',)

class EnderDragon(Insentient):
    """
    Ender dragon entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for ender dragons.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the ender dragon.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = "minecraft:ender_dragon"
    BOUNDING: ClassVar[Tuple[float, float]] = (16.0, 8.0)

    @property
    def dragon_phase(self) -> int:
        """
        Dragon phase.

        Returns
        -------
        int
            Dragon phase value, where:
            - 0: circling

            - 1: strafing (preparing to shoot fireball)

            - 2: flying to portal to land

            - 3: landing on portal

            - 4: taking off from portal

            - 5: landed, performing breath attack

            - 6: landed, looking for player for breath attack

            - 7: landed, roar before beginning breath attack

            - 8: charging player

            - 9: flying to portal to die

            - 10: hovering with no AI (default)
        """
        return int(self.get_metadata_value(12, 10))