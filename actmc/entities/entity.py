from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Any, Union, TypeVar, Generic, Optional

if TYPE_CHECKING:
    from ..math import Vector3D, Rotation

__all__ = ('BaseEntity', 'Entity', 'Living', 'Insentient', 'Creature')

T = TypeVar('T', int, str, default=int)

class BaseEntity(Generic[T]):
    """
    Base entity class with generic ID type.

    Parameters
    ----------
    entity_id: T
        Unique identifier for the entity
    """
    __slots__ = ('id',)

    def __init__(self, entity_id: T) -> None:
        self.id: T = entity_id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"

class Entity(BaseEntity[int]):
    """
    Base Entity class with common metadata fields and attributes.

    Parameters
    ----------
    entity_id: int
        Unique entity ID
    uuid: str
        Entity UUID string
    position: Vector3D[float]
        3D position coordinates
    rotation: Rotation
        Entity rotation data
    metadata: Dict[int, Any]
        Raw metadata dictionary from server
    """
    __slots__ = ('uuid', 'position', 'rotation', 'raw_metadata', 'properties')
    ENTITY_TYPE = None

    def __init__(self, entity_id: int, uuid: str, position: Vector3D[float], rotation: Rotation,
                 metadata: Dict[int, Any]) -> None:
        super().__init__(entity_id)
        self.uuid: str = uuid
        self.position: Vector3D[float] = position
        self.rotation: Rotation = rotation
        self.raw_metadata: Dict[int, Any] = metadata
        self.properties: Dict[str, Dict[str, Any]] = {}

    @property
    def _bit_mask(self) -> int:
        """Entity bit mask flags from metadata index 0."""
        return int(self.get_metadata_value(0, 0))

    @property
    def air(self) -> int:
        """Remaining air ticks, default 300."""
        return int(self.get_metadata_value(1, 300))

    @property
    def custom_name(self) -> Optional[str]:
        """Custom name text component or None."""
        name = self.get_metadata_value(2)
        return str(name) if name is not None else None

    @property
    def is_custom_name_visible(self) -> bool:
        """Whether custom name is visible above entity."""
        return bool(self.get_metadata_value(3, False))

    @property
    def is_silent(self) -> bool:
        """Whether entity makes sounds."""
        return bool(self.get_metadata_value(4, False))

    @property
    def no_gravity(self) -> bool:
        """Whether entity is affected by gravity."""
        return bool(self.get_metadata_value(5, False))

    def update_metadata(self, metadata: Dict[int, Any]) -> None:
        """Update entity metadata from metadata packet."""
        self.raw_metadata.update(metadata)

    def update_properties(self, properties: Dict[str, Dict[str, Any]]) -> None:
        """Update entity attributes from properties packet."""
        for key, prop_data in properties.items():
            if not isinstance(prop_data, dict) or 'value' not in prop_data:
                continue

            base_value = float(prop_data['value'])
            modifiers = prop_data.get('modifiers', {})

            if not isinstance(modifiers, dict):
                modifiers = {}

            final_value = self._calculate_final_value(base_value, modifiers)

            self.properties[key] = {
                'base': base_value,
                'final': final_value,
                'modifiers': modifiers
            }

    @staticmethod
    def _calculate_final_value(base_value: float, modifiers: Dict[str, Dict[str, Union[int, float]]]) -> float:
        """Calculate final attribute value with modifiers."""
        if not modifiers:
            return base_value

        value = base_value
        mod_list = list(modifiers.values())

        for mod in mod_list:
            if isinstance(mod, dict) and mod.get('operation') == 0:
                amount = mod.get('amount', 0)
                if isinstance(amount, (int, float)):
                    value += float(amount)

        multiply_base = 0.0
        for mod in mod_list:
            if isinstance(mod, dict) and mod.get('operation') == 1:
                amount = mod.get('amount', 0)
                if isinstance(amount, (int, float)):
                    multiply_base += float(amount)

        if multiply_base:
            value += base_value * multiply_base

        for mod in mod_list:
            if isinstance(mod, dict) and mod.get('operation') == 2:
                amount = mod.get('amount', 0)
                if isinstance(amount, (int, float)):
                    value *= (1 + float(amount))
        return value

    def get_attribute(self, key: str, default: float = 0.0) -> float:
        """
        Get final attribute value.

        Parameters
        ----------
        key: str
            Attribute key name
        default: float
            Default value if attribute not found

        Returns
        -------
        float
            Final attribute value
        """
        if key in self.properties:
            final_value = self.properties[key].get('final')
            if isinstance(final_value, (int, float)):
                return float(final_value)
        return default

    def get_metadata_value(self, index: int, default: Any = None) -> Any:
        """Get metadata value by index with default fallback"""
        if index in self.raw_metadata:
            return self.raw_metadata[index]['value']
        return default

    @property
    def max_health(self) -> float:
        """Maximum health attribute value."""
        return self.get_attribute('generic.maxHealth', 20.0)

    @property
    def movement_speed(self) -> float:
        """Movement speed attribute value."""
        return self.get_attribute('generic.movementSpeed', 0.1)

    @property
    def armor(self) -> float:
        """Armor attribute value."""
        return self.get_attribute('generic.armor', 0.0)

    @property
    def attack_speed(self) -> float:
        """Attack speed attribute value."""
        return self.get_attribute('generic.attackSpeed', 4.0)

    @property
    def on_fire(self) -> bool:
        """Whether entity is on fire (bit 0)."""
        return bool(self._bit_mask & 0x01)

    @property
    def crouched(self) -> bool:
        """Whether entity is crouching (bit 1)."""
        return bool(self._bit_mask & 0x02)

    @property
    def sprinting(self) -> bool:
        """Whether entity is sprinting (bit 3)."""
        return bool(self._bit_mask & 0x08)

    @property
    def invisible(self) -> bool:
        """Whether entity is invisible (bit 5)."""
        return bool(self._bit_mask & 0x20)

    @property
    def glowing(self) -> bool:
        """Whether entity is glowing (bit 6)."""
        return bool(self._bit_mask & 0x40)

    @property
    def flying_with_elytra(self) -> bool:
        """Whether entity is flying with elytra (bit 7)."""
        return bool(self._bit_mask & 0x80)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"

class Living(Entity):
    """Living entity extending Entity."""
    __slots__ = ()

    @property
    def hand_states(self) -> int:
        """Hand state bit mask from metadata index 6."""
        return int(self.get_metadata_value(6, 0))

    @property
    def health(self) -> float:
        """Current health value from metadata index 7."""
        return float(self.get_metadata_value(7, 1.0))

    @property
    def potion_effect_color(self) -> int:
        """Potion effect particle color from metadata index 8."""
        return int(self.get_metadata_value(8, 0))

    @property
    def is_potion_effect_ambient(self) -> bool:
        """Whether potion effect is ambient from metadata index 9."""
        return bool(self.get_metadata_value(9, False))

    @property
    def arrows_in_entity(self) -> int:
        """Number of arrows stuck in entity from metadata index 10."""
        return int(self.get_metadata_value(10, 0))

    @property
    def is_hand_active(self) -> bool:
        """Whether hand is active (using item)."""
        return bool(self.hand_states & 0x01)

    @property
    def active_hand(self) -> int:
        """Which hand is active (0=main, 1=off)."""
        return (self.hand_states & 0x02) >> 1

class Insentient(Living):
    """Insentient entity extending Living (base for mobs with AI)."""
    __slots__ = ()

    @property
    def _insentient_bit_mask(self) -> int:
        """Insentient-specific bit mask from metadata index 11."""
        return int(self.get_metadata_value(11, 0))

    @property
    def no_ai(self) -> bool:
        """Whether AI is disabled (bit 0)."""
        return bool(self._insentient_bit_mask & 0x01)

    @property
    def left_handed(self) -> bool:
        """Whether entity is left-handed (bit 1)."""
        return bool(self._insentient_bit_mask & 0x02)

class Creature(Insentient):
    """Creature entity extending Insentient."""
    __slots__ = ()
