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
from .entity import Entity

if TYPE_CHECKING:
    from typing import ClassVar, Tuple, Optional, Dict, Any

__all__ = ('Hanging', 'ItemFrame', 'Painting')

class Hanging(Entity):
    """Base class for hanging entities."""

    __slots__ = ()

    @property
    def orientation(self) -> str:
        """
        Gets the orientation/direction the hanging entity is facing.

        Returns
        -------
        str
            The direction as a string ('south', 'west', 'north', or 'east').
        """
        direction_map = {0: 'south', 1: 'west', 2: 'north', 3: 'east'}
        value = self.get_metadata_value(-1)
        return direction_map[value]


class ItemFrame(Hanging):
    """
    Item frame hanging entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for item frames.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the item frame.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:item_frame'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.75, 0.75)

    @property
    def item(self) -> Optional[Dict[str, Any]]:
        """
        The item currently displayed in the frame.

        Returns
        -------
        Optional[Dict[str, Any]]
            Slot data for the displayed item, None if frame is empty.
        """
        item_data = self.get_metadata_value(6)
        return item_data if item_data else None

    @property
    def rotation_value(self) -> int:
        """
        Rotation of the item in the frame.

        Returns
        -------
        int
            Rotation value (0-7, representing 45-degree increments).
        """
        return int(self.get_metadata_value(7, 0))

    @property
    def has_item(self) -> bool:
        """
        Whether the item frame contains an item.

        Returns
        -------
        bool
            True if frame has an item, False if empty.
        """
        return self.item is not None

    @property
    def rotation_degrees(self) -> float:
        """
        Rotation of the item in degrees.

        Returns
        -------
        float
            Rotation in degrees (0-315 in 45-degree increments).
        """
        return self.rotation_value * 45.0


class Painting(Hanging):
    """
    Painting hanging entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for paintings.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the painting.
    PAINTING_TYPES: ClassVar[Dict[str, Dict[str, int]]]
        Dictionary mapping painting names to their dimensions.
    """

    __slots__ = ('_painting_type',)

    ENTITY_TYPE: ClassVar[str] = 'minecraft:painting'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.0625, 1.0)  # Dynamic based on type

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._painting_type: Optional[str] = None

    @property
    def painting_type(self) -> Optional[str]:
        """
        Get the painting type name.

        Returns
        -------
        Optional[str]
            The name of the painting (e.g., 'Kebab', 'Match'), or None if not set.
        """
        return self._painting_type

    def set_painting_type(self, painting_name: str) -> None:
        """
        Set the painting type by name.

        Parameters
        ----------
        painting_name : str
            Name of the painting type to set.
        """
        self._painting_type = painting_name