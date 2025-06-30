from __future__ import annotations

from .entity import Monster

__all__ = ('AbstractSkeleton', 'Skeleton', 'WitherSkeleton', 'Stray')

class AbstractSkeleton(Monster):
    """AbstractSkeleton entity extending Monster."""
    __slots__ = ()

    @property
    def is_swinging_arms(self) -> bool:
        """Whether skeleton is swinging arms from metadata index 12."""
        return bool(self.get_metadata_value(12, False))

class Skeleton(AbstractSkeleton):
    """Skeleton entity extending AbstractSkeleton."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:skeleton"

class WitherSkeleton(AbstractSkeleton):
    """Wither Skeleton entity extending AbstractSkeleton."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:wither_skeleton"

class Stray(AbstractSkeleton):
    """Stray entity extending AbstractSkeleton."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:stray"