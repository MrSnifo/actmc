from __future__ import annotations
from .entity import Insentient

__all__ = ('Bat',)

class Bat(Insentient):
    """Bat entity."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:bat"

    @property
    def is_hanging(self) -> bool:
        """Whether bat is hanging from metadata index 12 (bit 0)."""
        return bool(self.get_metadata_value(12, 0) & 0x01)