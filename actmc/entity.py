from __future__ import annotations


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict, Any
    from . import math

class Entity:
    """Represents a generic entity in the Minecraft world (player, mob, item, etc.)."""

    __slots__ = ('id', 'type')

    def __init__(self, entity_id: int, entity_type: str = 'unknown') -> None:
        self.id: int = entity_id
        self.type: str = entity_type

    def __repr__(self) -> str:
        return f"<Entity id={self.id}, type={self.type}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Entity) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class ObjectData(Entity):
    """Represents an object entity with parsed data"""

    __slots__ = ('data', 'velocity', 'object_type', 'raw_data', 'object_uuid')

    OBJECT_TYPES = {
        2: 'item', 10: 'minecart', 60: 'arrow', 63: 'fireball', 64: 'small_fireball',
        66: 'wither_skull', 67: 'shulker_bullet', 68: 'llama_spit', 70: 'falling_block',
        71: 'item_frame', 73: 'potion', 75: 'exp_bottle', 90: 'fishing_float',
        91: 'spectral_arrow', 93: 'dragon_fireball'
    }

    if TYPE_CHECKING:
        data: Dict[str, Any]

    def __init__(self, entity_id: int, object_uuid: str, object_type: int,
                 object_data: int, velocity: math.Vector3D) -> None:
        type_name = self.OBJECT_TYPES.get(object_type, f'unknown_{object_type}')
        super().__init__(entity_id, type_name)

        self.object_uuid = object_uuid
        self.object_type = object_type
        self.raw_data = object_data
        self.velocity = velocity
        self.data = self._parse_data(self.type, self.raw_data)

    @staticmethod
    def _parse_data(object_type: str, raw_data: int) -> Dict[str, Any]:
        """Parse object data based on type"""
        if object_type == 'item':
            return {'velocity_present': raw_data == 1}

        elif object_type == 'minecart':
            types = {0: 'empty', 1: 'chest', 2: 'furnace', 3: 'tnt',
                     4: 'spawner', 5: 'hopper', 6: 'command_block'}
            return {'type': types.get(raw_data, 'unknown')}

        elif object_type == 'item_frame':
            directions = {0: 'south', 1: 'west', 2: 'north', 3: 'east'}
            return {'direction': directions.get(raw_data, 'unknown')}

        elif object_type == 'falling_block':
            return {
                'block_type': raw_data & 0xFFF,
                'metadata': (raw_data >> 12) & 0xF
            }

        elif object_type in ('arrow', 'spectral_arrow'):
            return {'shooter_id': raw_data - 1 if raw_data > 0 else None}

        elif object_type in ('fireball', 'small_fireball', 'dragon_fireball', 'wither_skull'):
            return {'shooter_id': raw_data if raw_data != 0 else None}

        elif object_type == 'fishing_float':
            return {'owner_id': raw_data}

        else:
            return {'raw_data': raw_data}

    def __repr__(self) -> str:
        if self.type == 'minecart':
            desc = f"{self.data.get('type', 'unknown')} minecart"
        elif self.type == 'item_frame':
            desc = f"item frame ({self.data.get('direction', 'unknown')})"
        else:
            desc = self.type

        # Only show velocity if the object is moving
        has_velocity = (self.velocity.x != 0.0 or self.velocity.y != 0.0 or self.velocity.z != 0.0)

        if has_velocity:
            return f"ObjectData(id={self.id}, type={desc}, velocity={self.velocity})"
        else:
            return f"ObjectData(id={self.id}, type={desc})"

class Player(Entity):
    """Represents the player's client instance."""

    __slots__ = ('username', 'uid', 'gamemode', 'health', 'food', 'food_saturation',
                 'experience_bar', 'level', 'total_experience', 'selected_slot',
                 'position', 'rotation')

    if TYPE_CHECKING:
        # Health
        health: float
        food: int
        food_saturation: float
        # Experience
        experience_bar: float
        level: int
        total_experience: int
        # Held item
        selected_slot: int
        # Position, rotation
        position: math.Vector3D
        rotation: math.Rotation

    def __init__(self, uid: str, username: str) -> None:
        super().__init__(0, 'player')
        self.uid: str = uid
        self.username: str = username

    @property
    def is_dead(self) -> bool:
        return self.health <= 0

    def __repr__(self) -> str:
        return f"<Player username={self.username} uid={self.uid}>"
