from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Any, Optional

if TYPE_CHECKING:
    from ..math import Vector3D, Rotation

from .entity import Entity

__all__ = ('Hanging', 'ItemFrame', 'Painting')

class Hanging(Entity):
    """Represents a hanging entity."""

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
    """Item frame hanging entity."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:item_frame"

    @property
    def item(self) -> Optional[Dict[str, Any]]:
        """
        The item currently displayed in the frame.

        Returns
        -------
        Optional[Dict[str, Any]]
            Slot data for the displayed item, None if frame is empty
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
            Rotation value (0-7, representing 45-degree increments)
        """
        return int(self.get_metadata_value(7, 0))

    @property
    def has_item(self) -> bool:
        """
        Whether the item frame contains an item.

        Returns
        -------
        bool
            True if frame has an item, False if empty
        """
        return self.item is not None

    @property
    def rotation_degrees(self) -> float:
        """
        Rotation of the item in degrees.

        Returns
        -------
        float
            Rotation in degrees (0-315 in 45-degree increments)
        """
        return self.rotation_value * 45.0

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}, has_item={self.has_item}>"

class Painting(Hanging):
    """Painting hanging entity."""

    __slots__ = ('_painting_type',)
    ENTITY_TYPE = "minecraft:painting"

    PAINTING_TYPES = {
        "Kebab": {"width": 1, "height": 1},
        "Aztec": {"width": 1, "height": 1},
        "Alban": {"width": 1, "height": 1},
        "Aztec2": {"width": 1, "height": 1},
        "Bomb": {"width": 1, "height": 1},
        "Plant": {"width": 1, "height": 1},
        "Wasteland": {"width": 1, "height": 1},
        "Pool": {"width": 2, "height": 1},
        "Courbet": {"width": 2, "height": 1},
        "Sea": {"width": 2, "height": 1},
        "Sunset": {"width": 2, "height": 1},
        "Creebet": {"width": 2, "height": 1},
        "Wanderer": {"width": 1, "height": 2},
        "Graham": {"width": 1, "height": 2},
        "Match": {"width": 2, "height": 2},
        "Bust": {"width": 2, "height": 2},
        "Stage": {"width": 2, "height": 2},
        "Void": {"width": 2, "height": 2},
        "SkullAndRoses": {"width": 2, "height": 2},
        "Wither": {"width": 2, "height": 2},
        "Fighters": {"width": 4, "height": 2},
        "Pointer": {"width": 4, "height": 4},
        "Pigscene": {"width": 4, "height": 4},
        "BurningSkull": {"width": 4, "height": 4},
        "Skeleton": {"width": 4, "height": 3},
        "DonkeyKong": {"width": 4, "height": 3},
    }

    def __init__(self, entity_id: int, uuid: str, position: Vector3D[float], rotation: Rotation,
                 metadata: Dict[int, Any]):
        super().__init__(entity_id, uuid, position, rotation, metadata)
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

    @property
    def painting_width(self) -> int:
        """
        Get the width of the painting in blocks.

        Returns
        -------
        int
            Width of the painting in blocks. Defaults to 1 if unknown.
        """
        if self._painting_type and self._painting_type in self.PAINTING_TYPES:
            return self.PAINTING_TYPES[self._painting_type]["width"]
        return 1

    @property
    def painting_height(self) -> int:
        """
        Get the height of the painting in blocks.

        Returns
        -------
        int
            Height of the painting in blocks. Defaults to 1 if unknown.
        """
        if self._painting_type and self._painting_type in self.PAINTING_TYPES:
            return self.PAINTING_TYPES[self._painting_type]["height"]
        return 1

    @property
    def is_large_painting(self) -> bool:
        """
        Determine if the painting is larger than 1x1 blocks.

        Returns
        -------
        bool
            True if either width or height is greater than 1 block.
        """
        return self.painting_width > 1 or self.painting_height > 1

    def set_painting_type(self, painting_name: str) -> None:
        """
        Set the painting type by name.

        Parameters
        ----------
        painting_name : str
            Name of the painting type to set.

        Raises
        ------
        ValueError
            If the painting_name is not a valid painting.
        """
        if painting_name not in self.PAINTING_TYPES:
            raise ValueError(f"Invalid painting name: {painting_name}")
        self._painting_type = painting_name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}, painting_type={self.painting_type}>"

