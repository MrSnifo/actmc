from __future__ import annotations

from typing import Any, Optional

from .entity import (Entity, Monster, Ageable,Golem, Insentient)


class AbstractIllager(Monster):
    """Abstract Illager entity extending Monster."""
    __slots__ = ()

    @property
    def illager_bit_mask(self) -> int:
        """Illager-specific bit mask from metadata index 12."""
        return int(self.get_metadata_value(12, 0))

    @property
    def has_target(self) -> bool:
        """Whether illager has a target (bit 0)."""
        return bool(self.illager_bit_mask & 0x01)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class AbstractSkeleton(Monster):
    """Abstract Skeleton entity extending Monster."""
    __slots__ = ()

    @property
    def is_swinging_arms(self) -> bool:
        """Whether skeleton is swinging arms from metadata index 12."""
        return bool(self.get_metadata_value(12, False))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Blaze(Monster):
    """Blaze entity extending Monster"""

    @property
    def blaze_bit_mask(self) -> int:
        """Blaze bit mask from metadata index 12"""
        return int(self.get_metadata_value(12, 0))

    @property
    def is_on_fire(self) -> bool:
        return bool(self.blaze_bit_mask & 0x01)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Creeper(Monster):
    """Creeper entity extending Monster"""

    @property
    def state(self) -> int:
        """Creeper state from metadata index 12"""
        return int(self.get_metadata_value(12, -1))

    @property
    def is_charged(self) -> bool:
        """Whether creeper is charged from metadata index 13"""
        return bool(self.get_metadata_value(13, False))

    @property
    def is_ignited(self) -> bool:
        """Whether creeper is ignited from metadata index 14"""
        return bool(self.get_metadata_value(14, False))

    @property
    def is_idle(self) -> bool:
        return self.state == -1

    @property
    def is_fusing(self) -> bool:
        return self.state == 1

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Endermite(Monster):
    """Endermite entity extending Monster"""

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class GiantZombie(Monster):
    """Giant Zombie entity extending Monster"""

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Guardian(Monster):
    """Guardian entity extending Monster"""

    @property
    def is_retracting_spikes(self) -> bool:
        """Whether guardian is retracting spikes from metadata index 12"""
        return bool(self.get_metadata_value(12, False))

    @property
    def target_eid(self) -> int:
        """Target entity ID from metadata index 13"""
        return int(self.get_metadata_value(13, 0))

    @property
    def has_target(self) -> bool:
        return self.target_eid != 0

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class ElderGuardian(Guardian):
    """Elder Guardian entity extending Guardian"""

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Silverfish(Monster):
    """Silverfish entity extending Monster"""

    def __repr__(self) -> str:
        return f"<Silverfish id={self.id}, position={self.position}>"


class VindicationIllager(AbstractIllager):
    """Vindication Illager entity extending Abstract Illager"""

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class SpellcasterIllager(AbstractIllager):
    """Spellcaster Illager entity extending Abstract Illager"""

    @property
    def spell(self) -> int:
        """Current spell from metadata index 13"""
        return int(self.get_metadata_value(13, 0))

    @property
    def spell_name(self) -> str:
        spell_names = {
            0: "none",
            1: "summon vex",
            2: "attack",
            3: "wololo"
        }
        return spell_names.get(self.spell, "unknown")

    @property
    def is_casting(self) -> bool:
        return self.spell != 0

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class EvocationIllager(SpellcasterIllager):
    """Evocation Illager entity extending Spellcaster Illager"""

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class IllusionIllager(SpellcasterIllager):
    """Illusion Illager entity extending Spellcaster Illager"""

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Vex(Monster):
    """Vex entity extending Monster"""

    @property
    def vex_bit_mask(self) -> int:
        """Vex bit mask from metadata index 12"""
        return int(self.get_metadata_value(12, 0))

    @property
    def is_in_attack_mode(self) -> bool:
        return bool(self.vex_bit_mask & 0x01)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class EvocationFangs(Entity):
    """Evocation Fangs entity extending Entity directly"""

    def __repr__(self) -> str:
        return f"<EvocationFangs id={self.id}, position={self.position}>"


class Skeleton(AbstractSkeleton):
    """Skeleton entity extending Abstract Skeleton"""

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class WitherSkeleton(AbstractSkeleton):
    """Wither Skeleton entity extending Abstract Skeleton"""

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Stray(AbstractSkeleton):
    """Stray entity extending Abstract Skeleton"""

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Spider(Monster):
    """Spider entity extending Monster"""

    @property
    def spider_bit_mask(self) -> int:
        """Spider bit mask from metadata index 12"""
        return int(self.get_metadata_value(12, 0))

    @property
    def is_climbing(self) -> bool:
        return bool(self.spider_bit_mask & 0x01)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Witch(Monster):
    """Witch entity extending Monster"""

    @property
    def is_drinking_potion(self) -> bool:
        """Whether witch is drinking potion from metadata index 12"""
        return bool(self.get_metadata_value(12, False))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}"


class Zombie(Monster):
    """Zombie entity extending Monster"""

    @property
    def is_baby(self) -> bool:
        """Whether zombie is baby from metadata index 12"""
        return bool(self.get_metadata_value(12, False))

    @property
    def unused_type(self) -> int:
        """Unused type field from metadata index 13"""
        return int(self.get_metadata_value(13, 0))

    @property
    def are_hands_held_up(self) -> bool:
        """Whether hands are held up from metadata index 14"""
        return bool(self.get_metadata_value(14, False))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class ZombieVillager(Zombie):
    """Zombie Villager entity extending Zombie"""

    @property
    def is_converting(self) -> bool:
        """Whether zombie villager is converting from metadata index 15"""
        return bool(self.get_metadata_value(15, False))

    @property
    def profession(self) -> int:
        """Profession ID from metadata index 16"""
        return int(self.get_metadata_value(16, 0))

    @property
    def profession_name(self) -> str:
        professions = {
            0: "Farmer",
            1: "Librarian",
            2: "Priest",
            3: "Blacksmith",
            4: "Butcher",
            5: "Nitwit"
        }
        return professions.get(self.profession, "Unknown")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Husk(Zombie):
    """Husk entity extending Zombie"""

    def __repr__(self) -> str:
        baby_str = " (baby)" if self.is_baby else ""
        hands_str = " (hands up)" if self.are_hands_held_up else ""
        return f"<Husk id={self.id}, position={self.position}{baby_str}{hands_str}>"


class Enderman(Monster):
    """Enderman entity extending Monster"""

    @property
    def carried_block(self) -> Optional[int]:
        """Carried block ID from metadata index 12"""
        block = self.get_metadata_value(12)
        return int(block) if block is not None else None

    @property
    def is_screaming(self) -> bool:
        """Whether enderman is screaming from metadata index 13"""
        return bool(self.get_metadata_value(13, False))

    @property
    def is_carrying_block(self) -> bool:
        return self.carried_block is not None and self.carried_block != 0

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Villager(Ageable):
    """Villager entity extending Ageable"""

    @property
    def profession(self) -> int:
        """Profession ID from metadata index 13"""
        return int(self.get_metadata_value(13, 0))

    @property
    def profession_name(self) -> str:
        professions = {
            0: "farmer", 1: "librarian", 2: "priest",
            3: "blacksmith", 4: "butcher", 5: "nitwit"
        }
        return professions.get(self.profession, "unknown")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Shulker(Golem):
    """Shulker entity extending Golem"""

    # Direction mapping for facing direction
    DIRECTIONS = {
        0: "down",
        1: "up",
        2: "north",
        3: "south",
        4: "west",
        5: "east"
    }

    @property
    def facing_direction(self) -> int:
        """Facing direction from metadata index 12"""
        return int(self.get_metadata_value(12, 0))

    @property
    def attachment_position(self) -> Optional[Any]:
        """Attachment position from metadata index 13"""
        return self.get_metadata_value(13)

    @property
    def shield_height(self) -> int:
        """Shield height from metadata index 14"""
        return int(self.get_metadata_value(14, 0))

    @property
    def color(self) -> int:
        """Shulker color from metadata index 15"""
        return int(self.get_metadata_value(15, 10))

    @property
    def facing_direction_name(self) -> str:
        """Get the name of the facing direction"""
        return self.DIRECTIONS.get(self.facing_direction, "unknown")

    @property
    def is_attached(self) -> bool:
        """Check if shulker is attached to a block"""
        return self.attachment_position is not None

    @property
    def is_peeking(self) -> bool:
        """Check if shulker is peeking (shield height > 0)"""
        return self.shield_height > 0

    @property
    def peek_percentage(self) -> float:
        """Get peek percentage (0.0 to 1.0)"""
        return min(self.shield_height / 100.0, 1.0)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Slime(Monster):
    """Slime entity"""

    @property
    def size(self) -> int:
        """Slime size."""
        return int(self.get_metadata_value(12, 1))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}, size={self.size}>"

