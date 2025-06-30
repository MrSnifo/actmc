from __future__ import annotations
from .entity import Creature

__all__ = ('Villager',)

class Ageable(Creature):
    """Ageable mob entity extending Creature."""
    __slots__ = ()

    @property
    def is_baby(self) -> bool:
        """Whether entity is a baby from metadata index 12."""
        return bool(self.get_metadata_value(12, False))

class Villager(Ageable):
    """Villager entity."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:villager"

    @property
    def profession(self) -> int:
        """Villager profession from metadata index 13.

        Returns:
            0: Farmer
            1: Librarian
            2: Priest
            3: Blacksmith
            4: Butcher
            5: Nitwit
        """
        return int(self.get_metadata_value(13, 0))