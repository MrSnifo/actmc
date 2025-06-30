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

class Painting(Hanging):
    """Painting hanging entity."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:painting"

    def __init__(self, entity_id: int, uuid: str, position: Vector3D[float], rotation: Rotation,
                 metadata: Dict[int, Any]):
        super().__init__(entity_id, uuid, position, rotation, metadata)
        self._painting_type: Optional[int] = None

    # Painting type definitions with their dimensions
    PAINTING_TYPES = {
        0: {"name": "Kebab", "width": 1, "height": 1},
        1: {"name": "Aztec", "width": 1, "height": 1},
        2: {"name": "Alban", "width": 1, "height": 1},
        3: {"name": "Aztec2", "width": 1, "height": 1},
        4: {"name": "Bomb", "width": 1, "height": 1},
        5: {"name": "Plant", "width": 1, "height": 1},
        6: {"name": "Wasteland", "width": 1, "height": 1},
        7: {"name": "Pool", "width": 2, "height": 1},
        8: {"name": "Courbet", "width": 2, "height": 1},
        9: {"name": "Sea", "width": 2, "height": 1},
        10: {"name": "Sunset", "width": 2, "height": 1},
        11: {"name": "Creebet", "width": 2, "height": 1},
        12: {"name": "Wanderer", "width": 1, "height": 2},
        13: {"name": "Graham", "width": 1, "height": 2},
        14: {"name": "Match", "width": 2, "height": 2},
        15: {"name": "Bust", "width": 2, "height": 2},
        16: {"name": "Stage", "width": 2, "height": 2},
        17: {"name": "Void", "width": 2, "height": 2},
        18: {"name": "SkullAndRoses", "width": 2, "height": 2},
        19: {"name": "Wither", "width": 2, "height": 2},
        20: {"name": "Fighters", "width": 4, "height": 2},
        21: {"name": "Pointer", "width": 4, "height": 4},
        22: {"name": "Pigscene", "width": 4, "height": 4},
        23: {"name": "BurningSkull", "width": 4, "height": 4},
        24: {"name": "Skeleton", "width": 4, "height": 3},
        25: {"name": "DonkeyKong", "width": 4, "height": 3},
    }

    @property
    def painting_type(self) -> int:
        """
        Type ID of the painting.

        Returns
        -------
        int
            Painting type identifier
        """
        # Painting type is typically stored in NBT data or determined by size
        # This would need to be set during entity creation
        return getattr(self, '_painting_type', 0)

    @property
    def painting_name(self) -> str:
        """
        Name of the painting artwork.

        Returns
        -------
        str
            Name of the painting
        """
        painting_info = self.PAINTING_TYPES.get(self.painting_type, {"name": "Unknown"})
        return painting_info["name"]

    @property
    def painting_width(self) -> int:
        """
        Width of the painting in blocks.

        Returns
        -------
        int
            Width in blocks
        """
        painting_info = self.PAINTING_TYPES.get(self.painting_type, {"width": 1})
        return painting_info["width"]

    @property
    def painting_height(self) -> int:
        """
        Height of the painting in blocks.

        Returns
        -------
        int
            Height in blocks
        """
        painting_info = self.PAINTING_TYPES.get(self.painting_type, {"height": 1})
        return painting_info["height"]

    @property
    def is_large_painting(self) -> bool:
        """
        Whether this is a large painting (larger than 1x1).

        Returns
        -------
        bool
            True if painting is larger than 1x1 blocks
        """
        return self.painting_width > 1 or self.painting_height > 1

    def set_painting_type(self, painting_type: int) -> None:
        """
        Set the painting type.

        Parameters
        ----------
        painting_type : int
            The painting type ID to set

        Raises
        ------
        ValueError
            If painting_type is not a valid painting type
        """
        if painting_type not in self.PAINTING_TYPES:
            raise ValueError(f"Invalid painting type: {painting_type}")
        self._painting_type = painting_type
