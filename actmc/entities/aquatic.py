from __future__ import annotations

from .entity import Insentient

__all__ = ('Squid',)

class Squid(Insentient):
    """Squid entity extending WaterMob."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:squid"
