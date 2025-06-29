from __future__ import annotations

from typing import Any, Optional
from .entity import Entity, Projectile


class Snowball(Projectile):
    """Snowball projectile entity extending Projectile."""
    __slots__ = ()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Egg(Projectile):
    """Egg projectile entity extending Projectile."""
    __slots__ = ()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Potion(Projectile):
    """Thrown potion projectile entity extending Projectile."""
    __slots__ = ()

    @property
    def potion_item(self) -> Optional[Any]:
        """Potion item data from metadata index 6."""
        return self.get_metadata_value(6)

    @property
    def has_potion(self) -> bool:
        """Whether the potion has an item equipped."""
        return self.potion_item is not None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Arrow(Entity):
    """Arrow entity extending Entity (abstract base for TippedArrow and Spectral Arrow)."""
    __slots__ = ()

    @property
    def arrow_bit_mask(self) -> int:
        """Arrow bit mask flags from metadata index 6."""
        return int(self.get_metadata_value(6, 0))

    @property
    def is_critical(self) -> bool:
        """Whether arrow is critical (bit 0)."""
        return bool(self.arrow_bit_mask & 0x01)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class TippedArrow(Arrow):
    """Tipped arrow entity extending Arrow (used for both tipped and regular arrows)."""
    __slots__ = ()

    @property
    def color(self) -> int:
        """Tipped arrow color from metadata index 7."""
        return int(self.get_metadata_value(7, -1))

    @property
    def is_tipped(self) -> bool:
        """Whether arrow is tipped (has particles)."""
        return self.color != -1

    @property
    def has_particles(self) -> bool:
        """Whether arrow shows tipped arrow particles."""
        return self.is_tipped

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Fireball(Entity):
    """Fireball entity extending Entity (ghast fireball)."""
    __slots__ = ()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class WitherSkull(Fireball):
    """Wither skull projectile entity extending Fireball."""
    __slots__ = ()

    @property
    def invulnerable(self) -> bool:
        """Whether wither skull is invulnerable from metadata index 6."""
        return bool(self.get_metadata_value(6, False))

    @property
    def is_invulnerable(self) -> bool:
        """Whether wither skull is invulnerable."""
        return self.invulnerable

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Fireworks(Entity):
    """Fireworks rocket entity extending Entity."""
    __slots__ = ()

    @property
    def firework_info(self) -> Optional[Any]:
        """Firework item data from metadata index 6."""
        return self.get_metadata_value(6)

    @property
    def booster_entity_id(self) -> int:
        """Booster entity ID from metadata index 7."""
        return int(self.get_metadata_value(7, 0))

    @property
    def has_firework_data(self) -> bool:
        """Whether firework has data."""
        return self.firework_info is not None

    @property
    def is_elytra_boost(self) -> bool:
        """Whether firework is used for elytra boosting."""
        return self.booster_entity_id != 0

    @property
    def boosted_entity_id(self) -> int:
        """Entity ID that used this firework for elytra boosting."""
        return self.booster_entity_id

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class LlamaSpit(Entity):
    """Llama spit projectile entity extending Entity."""
    __slots__ = ()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"