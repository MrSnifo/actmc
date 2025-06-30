from __future__ import annotations

from .entity import Monster


__all__ = ('AbstractIllager', 'SpellcasterIllager', 'VindicationIllager', 'EvocationIllager', 'IllusionIllager')

class AbstractIllager(Monster):
    """Abstract Illager entity extending Monster."""
    __slots__ = ()

    @property
    def has_target(self) -> bool:
        """Whether illager has target (aggressive state) (bit 0)."""
        return bool(self.get_metadata_value(12, 0) & 0x01)

class SpellcasterIllager(AbstractIllager):
    """Spellcaster Illager entity extending Abstract Illager."""
    __slots__ = ()

    @property
    def spell(self) -> int:
        """Current spell from metadata index 13 (0: none, 1: summon vex, 2: attack, 3: wololo)."""
        return int(self.get_metadata_value(13, 0))

class VindicationIllager(AbstractIllager):
    """Vindicator illager entity."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:vindication_illager"


class EvocationIllager(SpellcasterIllager):
    """Evoker illager entity."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:evocation_illager"


class IllusionIllager(SpellcasterIllager):
    """Illusioner illager entity."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:illusion_illager"