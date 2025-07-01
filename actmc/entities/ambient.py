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

__all__ = ('Bat',)

class Bat(Insentient):
    """
    Bat entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for bats.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the bat.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:bat'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.5, 0.9)

    @property
    def is_hanging(self) -> bool:
        """
        Whether the bat is currently hanging upside down.

        Returns
        -------
        bool
            True if the bat is hanging, False otherwise.
        """
        return bool(self.get_metadata_value(12, 0) & 0x01)