from __future__ import annotations

from typing import Dict, Any, Optional
from ..math import Vector3D, Rotation
from .entity import Ambient, Animal, TameableAnimal, Insentient

class Bat(Ambient):
    """Bat entity extending Ambient."""
    __slots__ = ()

    @property
    def bat_bit_mask(self) -> int:
        """Bat-specific bit mask from metadata index 12."""
        return int(self.get_metadata_value(12, 0))

    @property
    def is_hanging(self) -> bool:
        """Whether bat is hanging (bit 0)."""
        return bool(self.bat_bit_mask & 0x01)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}, is_hanging={self.is_hanging}>"


class WaterMob(Insentient):
    """Water mob entity extending Insentient."""
    __slots__ = ()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Squid(WaterMob):
    """Squid entity extending WaterMob."""
    __slots__ = ()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class AbstractHorse(Animal):
    """Abstract horse entity extending Animal."""
    __slots__ = ()

    def __init__(self,
        entity_id: int,
        uuid: str,
        position: Vector3D[float],
        rotation: Rotation,
        metadata: Dict[int, Any],
    ) -> None:
        super().__init__(entity_id, uuid, position, rotation, metadata)

    @property
    def horse_bit_mask(self) -> int:
        """Horse-specific bit mask from metadata index 13."""
        return int(self.get_metadata_value(13, 0))

    @property
    def owner_uuid(self) -> Optional[str]:
        """Owner UUID from metadata index 14."""
        owner = self.get_metadata_value(14)
        return str(owner) if owner is not None else None

    @property
    def is_tame(self) -> bool:
        """Whether horse is tamed (bit 1)."""
        return bool(self.horse_bit_mask & 0x02)

    @property
    def is_saddled(self) -> bool:
        """Whether horse has saddle (bit 2)."""
        return bool(self.horse_bit_mask & 0x04)

    @property
    def has_bred(self) -> bool:
        """Whether horse has bred (bit 3)."""
        return bool(self.horse_bit_mask & 0x08)

    @property
    def is_eating(self) -> bool:
        """Whether horse is eating (bit 4)."""
        return bool(self.horse_bit_mask & 0x10)

    @property
    def is_rearing(self) -> bool:
        """Whether horse is on hind legs (bit 5)."""
        return bool(self.horse_bit_mask & 0x20)

    @property
    def is_mouth_open(self) -> bool:
        """Whether horse's mouth is open (bit 6)."""
        return bool(self.horse_bit_mask & 0x40)

    @property
    def has_owner(self) -> bool:
        """Whether horse has an owner."""
        return self.owner_uuid is not None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}, is_tame={self.is_tame}>"


class Horse(AbstractHorse):
    """Horse entity extending AbstractHorse."""
    __slots__ = ()

    @property
    def variant(self) -> int:
        """Horse variant (color & style) from metadata index 15."""
        return int(self.get_metadata_value(15, 0))

    @property
    def armor_type(self) -> int:
        """Armor type from metadata index 16. 0: none, 1: iron, 2: gold, 3: diamond."""
        return int(self.get_metadata_value(16, 0))

    @property
    def armor_item(self) -> Optional[Any]:
        """Armor item from metadata index 17 (Forge only)."""
        return self.get_metadata_value(17)

    @property
    def armor_name(self) -> str:
        """Human-readable armor type name."""
        armor_names = {0: "none", 1: "iron", 2: "gold", 3: "diamond"}
        return armor_names.get(self.armor_type, "unknown")

    def __repr__(self) -> str:
        tamed_str = " (tamed)" if self.is_tame else ""
        armor_str = f" (armor: {self.armor_name})" if self.armor_type > 0 else ""
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}{tamed_str}{armor_str}>"


class ZombieHorse(AbstractHorse):
    """Zombie horse entity extending AbstractHorse."""
    __slots__ = ()

    def __repr__(self) -> str:
        tamed_str = " (tamed)" if self.is_tame else ""
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}{tamed_str}>"


class SkeletonHorse(AbstractHorse):
    """Skeleton horse entity extending AbstractHorse."""
    __slots__ = ()

    def __repr__(self) -> str:
        tamed_str = " (tamed)" if self.is_tame else ""
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}{tamed_str}>"


class ChestedHorse(AbstractHorse):
    """Chested horse entity extending AbstractHorse."""
    __slots__ = ()

    @property
    def has_chest(self) -> bool:
        """Whether horse has chest from metadata index 15."""
        return bool(self.get_metadata_value(15, False))

    def __repr__(self) -> str:
        tamed_str = " (tamed)" if self.is_tame else ""
        chest_str = " (chest)" if self.has_chest else ""
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}{tamed_str}{chest_str}>"


class Donkey(ChestedHorse):
    """Donkey entity extending ChestedHorse."""
    __slots__ = ()

    def __repr__(self) -> str:
        tamed_str = " (tamed)" if self.is_tame else ""
        chest_str = " (chest)" if self.has_chest else ""
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}{tamed_str}{chest_str}>"


class Llama(ChestedHorse):
    """Llama entity extending ChestedHorse."""
    __slots__ = ()

    @property
    def strength(self) -> int:
        """Number of columns of 3 slots from metadata index 16."""
        return int(self.get_metadata_value(16, 0))

    @property
    def carpet_color(self) -> int:
        """Dye color from metadata index 17, or -1 if no carpet."""
        return int(self.get_metadata_value(17, -1))

    @property
    def variant(self) -> int:
        """Llama variant from metadata index 18. 0: creamy, 1: white, 2: brown, 3: gray."""
        return int(self.get_metadata_value(18, 0))

    @property
    def variant_name(self) -> str:
        """Human-readable variant name."""
        variants = {0: "creamy", 1: "white", 2: "brown", 3: "gray"}
        return variants.get(self.variant, "unknown")

    @property
    def has_carpet(self) -> bool:
        """Whether llama has carpet."""
        return self.carpet_color != -1

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Mule(ChestedHorse):
    """Mule entity extending ChestedHorse."""
    __slots__ = ()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Pig(Animal):
    """Pig entity extending Animal."""
    __slots__ = ()

    @property
    def has_saddle(self) -> bool:
        """Whether pig has saddle from metadata index 13."""
        return bool(self.get_metadata_value(13, False))

    @property
    def boost_time(self) -> int:
        """Boost time from metadata index 14."""
        return int(self.get_metadata_value(14, 0))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Rabbit(Animal):
    """Rabbit entity extending Animal."""
    __slots__ = ()

    @property
    def rabbit_type(self) -> int:
        """Rabbit type from metadata index 13."""
        return int(self.get_metadata_value(13, 0))

    @property
    def type_name(self) -> str:
        """Human-readable rabbit type name."""
        types = {
            0: "brown", 1: "white", 2: "black", 3: "black_and_white",
            4: "gold", 5: "salt_and_pepper", 99: "killer_bunny"
        }
        return types.get(self.rabbit_type, "unknown")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class PolarBear(Animal):
    """Polar bear entity extending Animal."""
    __slots__ = ()

    @property
    def is_standing_up(self) -> bool:
        """Whether polar bear is standing up from metadata index 13."""
        return bool(self.get_metadata_value(13, False))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Sheep(Animal):
    """Sheep entity extending Animal."""
    __slots__ = ()

    @property
    def sheep_bit_mask(self) -> int:
        """Sheep-specific bit mask from metadata index 13."""
        return int(self.get_metadata_value(13, 0))

    @property
    def color(self) -> int:
        """Sheep color (matches dye damage values)."""
        return self.sheep_bit_mask & 0x0F

    @property
    def is_sheared(self) -> bool:
        """Whether sheep is sheared (bit 4)."""
        return bool(self.sheep_bit_mask & 0x10)

    @property
    def color_name(self) -> str:
        """Human-readable color name."""
        colors = {
            0: "white", 1: "orange", 2: "magenta", 3: "light_blue",
            4: "yellow", 5: "lime", 6: "pink", 7: "gray",
            8: "light_gray", 9: "cyan", 10: "purple", 11: "blue",
            12: "brown", 13: "green", 14: "red", 15: "black"
        }
        return colors.get(self.color, "unknown")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Ocelot(TameableAnimal):
    """Ocelot entity extending TameableAnimal."""
    __slots__ = ()

    @property
    def ocelot_type(self) -> int:
        """Ocelot type from metadata index 15."""
        return int(self.get_metadata_value(15, 0))

    @property
    def type_name(self) -> str:
        """Human-readable ocelot type name."""
        types = {0: "untamed", 1: "tuxedo", 2: "tabby", 3: "siamese"}
        return types.get(self.ocelot_type, "unknown")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Wolf(TameableAnimal):
    """Wolf entity extending TameableAnimal."""
    __slots__ = ()

    @property
    def damage_taken(self) -> float:
        """Damage taken from metadata index 15."""
        return float(self.get_metadata_value(15, self.health))

    @property
    def is_begging(self) -> bool:
        """Whether wolf is begging from metadata index 16."""
        return bool(self.get_metadata_value(16, False))

    @property
    def collar_color(self) -> int:
        """Collar color from metadata index 17 (red by default)."""
        return int(self.get_metadata_value(17, 14))

    @property
    def collar_color_name(self) -> str:
        """Human-readable collar color name."""
        colors = {
            0: "white", 1: "orange", 2: "magenta", 3: "light_blue",
            4: "yellow", 5: "lime", 6: "pink", 7: "gray",
            8: "light_gray", 9: "cyan", 10: "purple", 11: "blue",
            12: "brown", 13: "green", 14: "red", 15: "black"
        }
        return colors.get(self.collar_color, "unknown")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Parrot(TameableAnimal):
    """Parrot entity extending TameableAnimal."""
    __slots__ = ()

    @property
    def variant(self) -> int:
        """Parrot variant from metadata index 15."""
        return int(self.get_metadata_value(15, 0))

    @property
    def variant_name(self) -> str:
        """Human-readable parrot variant name."""
        variants = {
            0: 'red_blue', 1: 'blue', 2: 'green',
            3: 'yellow_blue', 4: 'silver'
        }
        return variants.get(self.variant, "unknown")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"