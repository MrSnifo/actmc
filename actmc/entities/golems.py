from __future__ import annotations

from .entity import Creature

__all__ = ('Golem', 'IronGolem', 'Snowman')

class Golem(Creature):
    """Golem entity extending Creature."""
    __slots__ = ()

class IronGolem(Golem):
    """Iron golem entity (VillagerGolem)."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:villager_golem"

    @property
    def is_player_created(self) -> bool:
        """Whether iron golem is player-created from metadata index 12 (bit 0)."""
        return bool(self.get_metadata_value(12, 0) & 0x01)

class Snowman(Golem):
    """Snow golem entity (SnowGolem)."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:snowman"

    @property
    def has_pumpkin_hat(self) -> bool:
        """Whether snowman has pumpkin hat from metadata index 12 (bit 4)."""
        return bool(self.get_metadata_value(12, 0x10) & 0x10)