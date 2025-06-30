from __future__ import annotations
from .entity import Insentient

__all__ = ('Ghast',)

class Ghast(Insentient):
    """Ghast entity."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:ghast"

    @property
    def is_attacking(self) -> bool:
        """Whether ghast is attacking from metadata index 12."""
        return bool(self.get_metadata_value(12, False))