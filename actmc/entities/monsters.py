from __future__ import annotations

from .entity import Creature

__all__ = (
    'Monster', 'Creeper', 'Spider', 'CaveSpider', 'Zombie', 'ZombieVillager', 'PigZombie', 'Husk', 'Giant', 'Slime',
    'LavaSlime', 'Blaze', 'Enderman', 'Endermite', 'Silverfish', 'Witch', 'Guardian', 'ElderGuardian', 'Shulker',
    'WitherBoss', 'Vex', 'AbstractSkeleton', 'Skeleton', 'WitherSkeleton', 'Stray')

class Monster(Creature):
    """Monster entity extending Creature."""
    __slots__ = ()

class Creeper(Monster):
    """Creeper entity extending Monster."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:creeper"

    @property
    def state(self) -> int:
        """Creeper state (-1 = idle, 1 = fuse) from metadata index 12."""
        return int(self.get_metadata_value(12, -1))

    @property
    def is_charged(self) -> bool:
        """Whether creeper is charged from metadata index 13."""
        return bool(self.get_metadata_value(13, False))

    @property
    def is_ignited(self) -> bool:
        """Whether creeper is ignited from metadata index 14."""
        return bool(self.get_metadata_value(14, False))

    @property
    def is_fusing(self) -> bool:
        """Whether creeper is in fuse state."""
        return self.state == 1

class Spider(Monster):
    """Spider entity extending Monster."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:spider"

    @property
    def _spider_bit_mask(self) -> int:
        """Spider-specific bit mask from metadata index 12."""
        return int(self.get_metadata_value(12, 0))

    @property
    def is_climbing(self) -> bool:
        """Whether spider is climbing (bit 0)."""
        return bool(self._spider_bit_mask & 0x01)

class CaveSpider(Spider):
    """Cave Spider entity extending Spider."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:cave_spider"

class Zombie(Monster):
    """Zombie entity extending Monster."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:zombie"

    @property
    def is_baby(self) -> bool:
        """Whether zombie is a baby from metadata index 12."""
        return bool(self.get_metadata_value(12, False))

    @property
    def unused_type(self) -> int:
        """Unused type field from metadata index 13."""
        return int(self.get_metadata_value(13, 0))

    @property
    def are_hands_held_up(self) -> bool:
        """Whether zombie has hands held up from metadata index 14."""
        return bool(self.get_metadata_value(14, False))

class ZombieVillager(Zombie):
    """Zombie Villager entity extending Zombie."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:zombie_villager"

    @property
    def is_converting(self) -> bool:
        """Whether zombie villager is converting from metadata index 15."""
        return bool(self.get_metadata_value(15, False))

    @property
    def profession(self) -> int:
        """Zombie villager profession from metadata index 16."""
        return int(self.get_metadata_value(16, 0))

class PigZombie(Monster):
    """Pig Zombie (Zombified Piglin) entity extending Monster."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:zombie_pigman"

class Husk(Zombie):
    """Husk entity extending Zombie."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:husk"

class Giant(Monster):
    """Giant Zombie entity extending Monster."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:giant"

class Slime(Monster):
    """Slime entity extending Monster."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:slime"

    @property
    def size(self) -> int:
        """Slime size from metadata index 12."""
        return int(self.get_metadata_value(12, 1))

class LavaSlime(Slime):
    """Lava Slime (Magma Cube) entity extending Slime."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:magma_cube"

class Blaze(Monster):
    """Blaze entity extending Monster."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:blaze"

    @property
    def _blaze_bit_mask(self) -> int:
        """Blaze-specific bit mask from metadata index 12."""
        return int(self.get_metadata_value(12, 0))

    @property
    def is_on_fire(self) -> bool:
        """Whether blaze is on fire (bit 0)."""
        return bool(self._blaze_bit_mask & 0x01)

class Enderman(Monster):
    """Enderman entity extending Monster."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:enderman"

    @property
    def carried_block(self) -> int | None:
        """Carried block ID from metadata index 12, or None if no block."""
        block_data = self.get_metadata_value(12)
        return int(block_data) if block_data is not None else None

    @property
    def is_screaming(self) -> bool:
        """Whether enderman is screaming from metadata index 13."""
        return bool(self.get_metadata_value(13, False))

class Endermite(Monster):
    """Endermite entity extending Monster."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:endermite"

class Silverfish(Monster):
    """Silverfish entity extending Monster."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:silverfish"

class Witch(Monster):
    """Witch entity extending Monster."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:witch"

    @property
    def is_drinking_potion(self) -> bool:
        """Whether witch is drinking potion from metadata index 12."""
        return bool(self.get_metadata_value(12, False))

class Guardian(Monster):
    """Guardian entity extending Monster."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:guardian"

    @property
    def is_retracting_spikes(self) -> bool:
        """Whether guardian is retracting spikes from metadata index 12."""
        return bool(self.get_metadata_value(12, False))

    @property
    def target_eid(self) -> int:
        """Target entity ID from metadata index 13."""
        return int(self.get_metadata_value(13, 0))

class ElderGuardian(Guardian):
    """Elder Guardian entity extending Guardian."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:elder_guardian"

class Shulker(Monster):
    """Shulker entity extending Monster."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:shulker"

    @property
    def facing_direction(self) -> int:
        """Facing direction from metadata index 12 (Down=0, Up=1, North=2, South=3, West=4, East=5)."""
        return int(self.get_metadata_value(12, 0))

    @property
    def attachment_position(self) -> tuple[int, int, int] | None:
        """Attachment position from metadata index 13, or None if absent."""
        pos_data = self.get_metadata_value(13)
        if pos_data is not None:
            # Position data would need to be parsed based on the position format
            return pos_data
        return None

    @property
    def shield_height(self) -> int:
        """Shield height from metadata index 14."""
        return int(self.get_metadata_value(14, 0))

    @property
    def color(self) -> int:
        """Dye color from metadata index 15."""
        return int(self.get_metadata_value(15, 10))  # Default purple

class WitherBoss(Monster):
    """Wither Boss entity extending Monster."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:wither"

    @property
    def center_head_target(self) -> int:
        """Center head's target entity ID from metadata index 12."""
        return int(self.get_metadata_value(12, 0))

    @property
    def left_head_target(self) -> int:
        """Left head's target entity ID from metadata index 13."""
        return int(self.get_metadata_value(13, 0))

    @property
    def right_head_target(self) -> int:
        """Right head's target entity ID from metadata index 14."""
        return int(self.get_metadata_value(14, 0))

    @property
    def invulnerable_time(self) -> int:
        """Invulnerable time from metadata index 15."""
        return int(self.get_metadata_value(15, 0))

class Vex(Monster):
    """Vex entity extending Monster."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:vex"

    @property
    def _vex_bit_mask(self) -> int:
        """Vex-specific bit mask from metadata index 12."""
        return int(self.get_metadata_value(12, 0))

    @property
    def is_in_attack_mode(self) -> bool:
        """Whether vex is in attack mode (bit 0)."""
        return bool(self._vex_bit_mask & 0x01)

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