from __future__ import annotations

from typing import Dict, Any, Optional
from .entity import Entity

__all__ = ('Projectile', 'Arrow', 'TippedArrow', 'SpectralArrow', 'Snowball', 'Egg', 'Potion', 'ThrownExpBottle',
           'ThrownEnderpearl', 'EyeOfEnderSignal', 'Fireball', 'SmallFireball', 'DragonFireball', 'WitherSkull',
           'ShulkerBullet', 'LlamaSpit')

class Projectile(Entity):
    """Projectile entity extending Entity."""
    __slots__ = ()

class Arrow(Projectile):
    """Abstract base class for arrow projectiles."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:arrow"

    @property
    def is_critical(self) -> bool:
        """
        Whether the arrow is critical (deals extra damage).

        Returns
        -------
        bool
            True if arrow is critical, False otherwise
        """
        arrow_flags = int(self.get_metadata_value(6, 0))
        return bool(arrow_flags & 0x01)

class TippedArrow(Arrow):
    """Tipped arrow projectile entity. """
    __slots__ = ()
    ENTITY_TYPE = "minecraft:arrow"

    @property
    def color(self) -> int:
        """
        Particle color for tipped arrows.

        Returns
        -------
        int
            Color value (-1 for no particles, regular arrows)
        """
        return int(self.get_metadata_value(7, -1))

    @property
    def is_tipped(self) -> bool:
        """
        Whether this is a tipped arrow with potion effects.

        Returns
        -------
        bool
            True if arrow has potion effects, False for regular arrows
        """
        return self.color != -1

class SpectralArrow(Arrow):
    """
    Spectral arrow projectile entity."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:spectral_arrow"

class Snowball(Projectile):
    """Snowball projectile entity."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:snowball"

class Egg(Projectile):
    """Thrown egg projectile entity."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:egg"

class Potion(Projectile):
    """Thrown potion projectile entity."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:potion"

    @property
    def potion_item(self) -> Optional[Dict[str, Any]]:
        """
        The potion item being thrown.

        Returns
        -------
        Optional[Dict[str, Any]]
            Slot data for the potion item, None if empty
        """
        item_data = self.get_metadata_value(6)
        return item_data if item_data else None

class ThrownExpBottle(Projectile):
    """Thrown experience bottle projectile entity."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:xp_bottle"

class ThrownEnderpearl(Projectile):
    """Thrown ender pearl projectile entity."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:ender_pearl"

class EyeOfEnderSignal(Projectile):
    """Eye of Ender signal projectile entity."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:eye_of_ender_signal"

class Fireball(Projectile):
    """Base fireball projectile entity. """
    __slots__ = ()
    ENTITY_TYPE = "minecraft:fireball"

class SmallFireball(Fireball):
    """ Small fireball projectile entity."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:small_fireball"

class DragonFireball(Projectile):
    """Dragon fireball projectile entity."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:dragon_fireball"

class WitherSkull(Fireball):
    """Wither skull projectile entity."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:wither_skull"

    @property
    def is_invulnerable(self) -> bool:
        """Whether the wither skull is invulnerable to damage."""
        return bool(self.get_metadata_value(6, False))

class ShulkerBullet(Projectile):
    """Shulker bullet projectile entity."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:shulker_bullet"

class LlamaSpit(Projectile):
    """Llama spit projectile entity."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:llama_spit"
