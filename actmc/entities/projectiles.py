"""
The MIT License (MIT)

Copyright (c) 2025-present Snifo

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Dict, Any
from .entity import Entity

if TYPE_CHECKING:
    from typing import ClassVar, Tuple

__all__ = (
    'Projectile', 'Arrow', 'TippedArrow', 'SpectralArrow', 'Snowball', 'Egg', 'Potion', 
    'ExpBottle', 'Enderpearl', 'EyeOfEnderSignal', 'Fireball', 'SmallFireball',
    'DragonFireball', 'WitherSkull', 'ShulkerBullet', 'LlamaSpit', 'FireworksRocket'
)


class Projectile(Entity):
    """Base projectile entity class."""

    __slots__ = ()


class Arrow(Projectile):
    """
    Arrow projectile entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for arrows.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the arrow.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:arrow'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.5, 0.5)

    @property
    def shooter_entity_id(self) -> int:
        """
        Returns the entity ID of the shooter who fired the arrow.

        Returns
        -------
        int
            The actual entity ID of the shooter.
        """
        raw_id = self.get_metadata_value(-1, 0)
        return raw_id - 1

    @property
    def is_critical(self) -> bool:
        """
        Whether the arrow is critical (deals extra damage).

        Returns
        -------
        bool
            True if arrow is critical, False otherwise.
        """
        arrow_flags = int(self.get_metadata_value(6, 0))
        return bool(arrow_flags & 0x01)


class TippedArrow(Arrow):
    """
    Tipped arrow projectile entity with potion effects.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for tipped arrows.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the tipped arrow.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:arrow'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.5, 0.5)

    @property
    def color(self) -> int:
        """
        Particle color for tipped arrows.

        Returns
        -------
        int
            Color value (-1 for no particles, regular arrows).
        """
        return int(self.get_metadata_value(7, -1))

    @property
    def is_tipped(self) -> bool:
        """
        Whether this is a tipped arrow with potion effects.

        Returns
        -------
        bool
            True if arrow has potion effects, False for regular arrows.
        """
        return self.color != -1


class SpectralArrow(Projectile):
    """
    Spectral arrow projectile entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for spectral arrows.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the spectral arrow.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:spectral_arrow'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.5, 0.5)


class Snowball(Projectile):
    """
    Snowball projectile entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for snowballs.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the snowball.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:snowball'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.25, 0.25)


class Egg(Projectile):
    """
    Thrown egg projectile entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for eggs.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the egg.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:egg'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.25, 0.25)


class Potion(Projectile):
    """
    Thrown potion projectile entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for potions.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the potion.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:potion'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.25, 0.25)

    @property
    def potion_item(self) -> Optional[Dict[str, Any]]:
        """
        The potion item being thrown.

        Returns
        -------
        Optional[Dict[str, Any]]
            Slot data for the potion item, None if empty.
        """
        item_data = self.get_metadata_value(6)
        return item_data if item_data else None


class ExpBottle(Projectile):
    """
    Thrown experience bottle projectile entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for experience bottles.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the experience bottle.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:xp_bottle'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.25, 0.25)


class Enderpearl(Projectile):
    """
    Thrown ender pearl projectile entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for ender pearls.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the ender pearl.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:ender_pearl'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.25, 0.25)


class EyeOfEnderSignal(Projectile):
    """
    Eye of Ender signal projectile entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for eye of ender signals.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the eye of ender signal.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:eye_of_ender_signal'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.25, 0.25)


class Fireball(Projectile):
    """
    Large fireball projectile entity (ghast).

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for fireballs.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the fireball.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:fireball'
    BOUNDING: ClassVar[Tuple[float, float]] = (1.0, 1.0)


class SmallFireball(Projectile):
    """
    Small fireball projectile entity (blaze).

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for small fireballs.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the small fireball.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:small_fireball'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.3125, 0.3125)


class DragonFireball(Projectile):
    """
    Dragon fireball projectile entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for dragon fireballs.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the dragon fireball.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:dragon_fireball'
    BOUNDING: ClassVar[Tuple[float, float]] = (1.0, 1.0)


class WitherSkull(Projectile):
    """
    Wither skull projectile entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for wither skulls.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the wither skull.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:wither_skull'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.3125, 0.3125)

    @property
    def is_invulnerable(self) -> bool:
        """
        Whether the wither skull is invulnerable to damage.

        Returns
        -------
        bool
            True if the wither skull is invulnerable, False otherwise.
        """
        return bool(self.get_metadata_value(6, False))


class ShulkerBullet(Projectile):
    """
    Shulker bullet projectile entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for shulker bullets.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the shulker bullet.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:shulker_bullet'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.3125, 0.3125)


class LlamaSpit(Projectile):
    """
    Llama spit projectile entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for llama spit.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the llama spit.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:llama_spit'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.25, 0.25)


class FireworksRocket(Projectile):
    """
    Fireworks rocket projectile entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for fireworks rockets.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the fireworks rocket.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:fireworks_rocket'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.25, 0.25)