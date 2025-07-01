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

from typing import TYPE_CHECKING
from .entity import Creature

if TYPE_CHECKING:
    from typing import ClassVar, Optional, Tuple

__all__ = (
    'Monster', 'Creeper', 'Spider', 'CaveSpider', 'Zombie', 'ZombieVillager', 'PigZombie', 'Husk', 'Giant', 'Slime',
    'LavaSlime', 'Blaze', 'Enderman', 'Endermite', 'Silverfish', 'Witch', 'Guardian', 'ElderGuardian', 'Shulker',
    'WitherBoss', 'Vex', 'AbstractSkeleton', 'Skeleton', 'WitherSkeleton', 'Stray'
)


class Monster(Creature):
    """Base monster entity extending Creature."""

    __slots__ = ()


class Creeper(Monster):
    """
    Creeper entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for creepers.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the creeper.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:creeper'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.6, 1.7)

    @property
    def state(self) -> int:
        """
        Creeper state.

        Returns
        -------
        int
            The creeper's current state (-1 = idle, 1 = fuse).
        """
        return int(self.get_metadata_value(12, -1))

    @property
    def is_charged(self) -> bool:
        """
        Whether creeper is charged.

        Returns
        -------
        bool
            True if the creeper is charged, False otherwise.
        """
        return bool(self.get_metadata_value(13, False))

    @property
    def is_ignited(self) -> bool:
        """
        Whether creeper is ignited.

        Returns
        -------
        bool
            True if the creeper is ignited, False otherwise.
        """
        return bool(self.get_metadata_value(14, False))

    @property
    def is_fusing(self) -> bool:
        """
        Whether creeper is in fuse state.

        Returns
        -------
        bool
            True if the creeper is currently fusing (about to explode), False otherwise.
        """
        return self.state == 1


class Spider(Monster):
    """
    Spider entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for spiders.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the spider.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:spider'
    BOUNDING: ClassVar[Tuple[float, float]] = (1.4, 0.9)

    @property
    def _spider_bit_mask(self) -> int:
        """Spider-specific bit mask."""
        return int(self.get_metadata_value(12, 0))

    @property
    def is_climbing(self) -> bool:
        """
        Whether spider is climbing (bit 0).

        Returns
        -------
        bool
            True if the spider is climbing, False otherwise.
        """
        return bool(self._spider_bit_mask & 0x01)


class CaveSpider(Spider):
    """
    Cave Spider entity extending Spider.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for cave spiders.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the cave spider.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:cave_spider'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.7, 0.5)


class Zombie(Monster):
    """
    Zombie entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for zombies.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the zombie.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:zombie'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.6, 1.95)

    @property
    def is_baby(self) -> bool:
        """
        Whether zombie is a baby.

        Returns
        -------
        bool
            True if the zombie is a baby, False otherwise.
        """
        return bool(self.get_metadata_value(12, False))

    @property
    def unused_type(self) -> int:
        """
        Unused type field.

        Returns
        -------
        int
            The unused type value.
        """
        return int(self.get_metadata_value(13, 0))

    @property
    def are_hands_held_up(self) -> bool:
        """
        Whether zombie has hands held up.

        Returns
        -------
        bool
            True if the zombie has hands held up, False otherwise.
        """
        return bool(self.get_metadata_value(14, False))


class ZombieVillager(Zombie):
    """
    Zombie Villager entity extending Zombie.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for zombie villagers.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the zombie villager.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:zombie_villager'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.6, 1.95)

    @property
    def is_converting(self) -> bool:
        """
        Whether zombie villager is converting.

        Returns
        -------
        bool
            True if the zombie villager is converting, False otherwise.
        """
        return bool(self.get_metadata_value(15, False))

    @property
    def profession(self) -> int:
        """
        Zombie villager profession.

        Returns
        -------
        int
            The profession ID of the zombie villager.
        """
        return int(self.get_metadata_value(16, 0))


class PigZombie(Monster):
    """
    Pig Zombie (Zombified Piglin) entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for pig zombies.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the pig zombie.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:zombie_pigman'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.6, 1.95)


class Husk(Zombie):
    """
    Husk entity extending Zombie.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for husks.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the husk.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:husk'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.6, 1.95)


class Giant(Monster):
    """
    Giant Zombie entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for giants.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the giant.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:giant'
    BOUNDING: ClassVar[Tuple[float, float]] = (3.6, 10.8)


class Slime(Monster):
    """
    Slime entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for slimes.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the slime.
        Note: Actual size is 0.51000005 * size for both dimensions.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:slime'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.51000005, 0.51000005)  # * size

    @property
    def size(self) -> int:
        """
        Slime size.

        Returns
        -------
        int
            The size of the slime (affects bounding box and health).
        """
        return int(self.get_metadata_value(12, 1))


class LavaSlime(Slime):
    """
    Lava Slime (Magma Cube).

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for magma cubes.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the magma cube.
        Note: Actual size is 0.51000005 * size for both dimensions.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:magma_cube'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.51000005, 0.51000005)  # * size


class Blaze(Monster):
    """
    Blaze entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for blazes.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the blaze.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:blaze'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.6, 1.8)

    @property
    def _blaze_bit_mask(self) -> int:
        """Blaze-specific bit mask."""
        return int(self.get_metadata_value(12, 0))

    @property
    def is_on_fire(self) -> bool:
        """
        Whether blaze is on fire (bit 0).

        Returns
        -------
        bool
            True if the blaze is on fire, False otherwise.
        """
        return bool(self._blaze_bit_mask & 0x01)


class Enderman(Monster):
    """
    Enderman entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for endermen.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the enderman.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:enderman'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.6, 2.9)

    @property
    def carried_block(self) -> Optional[int]:
        """
        Carried block ID.

        Returns
        -------
        Optional[int]
            The block ID being carried by the enderman, or None if no block.
        """
        block_data = self.get_metadata_value(12)
        return int(block_data) if block_data is not None else None

    @property
    def is_screaming(self) -> bool:
        """
        Whether enderman is screaming.

        Returns
        -------
        bool
            True if the enderman is screaming, False otherwise.
        """
        return bool(self.get_metadata_value(13, False))


class Endermite(Monster):
    """
    Endermite entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for endermites.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the endermite.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:endermite'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.4, 0.3)


class Silverfish(Monster):
    """
    Silverfish entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for silverfish.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the silverfish.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:silverfish'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.4, 0.3)


class Witch(Monster):
    """
    Witch entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for witches.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the witch.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:witch'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.6, 1.95)

    @property
    def is_drinking_potion(self) -> bool:
        """
        Whether witch is drinking potion.

        Returns
        -------
        bool
            True if the witch is drinking a potion, False otherwise.
        """
        return bool(self.get_metadata_value(12, False))


class Guardian(Monster):
    """
    Guardian entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for guardians.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the guardian.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:guardian'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.85, 0.85)

    @property
    def is_retracting_spikes(self) -> bool:
        """
        Whether guardian is retracting spikes.

        Returns
        -------
        bool
            True if the guardian is retracting spikes, False otherwise.
        """
        return bool(self.get_metadata_value(12, False))

    @property
    def target_eid(self) -> int:
        """
        Target entity ID.

        Returns
        -------
        int
            The entity ID of the guardian's target.
        """
        return int(self.get_metadata_value(13, 0))


class ElderGuardian(Guardian):
    """
    Elder Guardian entity extending Guardian.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for elder guardians.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the elder guardian.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:elder_guardian'
    BOUNDING: ClassVar[Tuple[float, float]] = (1.9975, 1.9975)  # 2.35 * guardian


class Shulker(Monster):
    """
    Shulker entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for shulkers.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the shulker.
        Note: Height varies from 1.0 to 2.0 depending on peek state.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:shulker'
    BOUNDING: ClassVar[Tuple[float, float]] = (1.0, 1.0)  # Height: 1.0-2.0 depending on peek

    @property
    def facing_direction(self) -> int:
        """
        Facing direction.

        Returns
        -------
        int
            The facing direction (Down=0, Up=1, North=2, South=3, West=4, East=5).
        """
        return int(self.get_metadata_value(12, 0))

    @property
    def attachment_position(self) -> Optional[Tuple[int, int, int]]:
        """
        Attachment position.

        Returns
        -------
        Optional[Tuple[int, int, int]]
            The attachment position coordinates, or None if absent.
        """
        pos_data = self.get_metadata_value(13)
        if pos_data is not None:
            # Position data would need to be parsed based on the position format
            return pos_data
        return None

    @property
    def shield_height(self) -> int:
        """
        Shield height.

        Returns
        -------
        int
            The height of the shulker's shield.
        """
        return int(self.get_metadata_value(14, 0))

    @property
    def color(self) -> int:
        """
        Dye color.

        Returns
        -------
        int
            The dye color ID (default purple = 10).
        """
        return int(self.get_metadata_value(15, 10))  # Default purple


class WitherBoss(Monster):
    """
    Wither Boss entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for the wither boss.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the wither boss.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:wither'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.9, 3.5)

    @property
    def center_head_target(self) -> int:
        """
        Center head's target entity ID.

        Returns
        -------
        int
            The entity ID of the center head's target.
        """
        return int(self.get_metadata_value(12, 0))

    @property
    def left_head_target(self) -> int:
        """
        Left head's target entity ID.

        Returns
        -------
        int
            The entity ID of the left head's target.
        """
        return int(self.get_metadata_value(13, 0))

    @property
    def right_head_target(self) -> int:
        """
        Right head's target entity ID.

        Returns
        -------
        int
            The entity ID of the right head's target.
        """
        return int(self.get_metadata_value(14, 0))

    @property
    def invulnerable_time(self) -> int:
        """
        Invulnerable time.

        Returns
        -------
        int
            The remaining invulnerable time in ticks.
        """
        return int(self.get_metadata_value(15, 0))


class Vex(Monster):
    """
    Vex entity.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for vexes.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the vex.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:vex'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.4, 0.8)

    @property
    def _vex_bit_mask(self) -> int:
        """Vex-specific bit mask."""
        return int(self.get_metadata_value(12, 0))

    @property
    def is_in_attack_mode(self) -> bool:
        """
        Whether vex is in attack mode (bit 0).

        Returns
        -------
        bool
            True if the vex is in attack mode, False otherwise.
        """
        return bool(self._vex_bit_mask & 0x01)


class AbstractSkeleton(Monster):
    """
    AbstractSkeleton entity base class.

    This is the base class for all skeleton-type entities.
    """

    __slots__ = ()

    @property
    def is_swinging_arms(self) -> bool:
        """
        Whether skeleton is swinging arms.

        Returns
        -------
        bool
            True if the skeleton is swinging arms, False otherwise.
        """
        return bool(self.get_metadata_value(12, False))


class Skeleton(AbstractSkeleton):
    """
    Skeleton entity extending AbstractSkeleton.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for skeletons.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the skeleton.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:skeleton'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.6, 1.99)


class WitherSkeleton(AbstractSkeleton):
    """
    Wither Skeleton entity extending AbstractSkeleton.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for wither skeletons.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the wither skeleton.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:wither_skeleton'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.7, 2.4)


class Stray(AbstractSkeleton):
    """
    Stray entity extending AbstractSkeleton.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for strays.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the stray.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:stray'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.6, 1.99)