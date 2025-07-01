from __future__ import annotations

from .entity import BaseEntity
from ..types.entities import block
from ..math import Vector3D
from typing import TYPE_CHECKING
from ..ui.chat import Message

__all__ = ('Banner', 'Beacon', 'Sign', 'MobSpawner', 'Skull', 'StructureBlock', 'EndGateway', 'ShulkerBox', 'Bed',
           'FlowerPot')

if TYPE_CHECKING:
    from typing import List, Optional, Dict, Any, Literal, ClassVar


class Banner(BaseEntity[str]):
    """
    Represents a banner block entity in Minecraft.

    A banner is a decorative block that can display custom patterns and colors.
    Base colors correspond to dye colors (0-15).
    """
    __slots__ = ('_raw_data',)

    # Color mappings for reference
    COLOR_NAMES: ClassVar[Dict[int, str]] = {
        0: 'white', 1: 'orange', 2: 'magenta', 3: 'light_blue',
        4: 'yellow', 5: 'lime', 6: 'pink', 7: 'gray',
        8: 'light_gray', 9: 'cyan', 10: 'purple', 11: 'blue',
        12: 'brown', 13: 'green', 14: 'red', 15: 'black'
    }

    def __init__(self, entity_id: str, data: block.Banner) -> None:
        super().__init__(entity_id)
        self._raw_data = data

    @property
    def base_color_id(self) -> int:
        """The base color of the banner (0-15 corresponding to dye colors)."""
        return self._raw_data['Base']

    @property
    def patterns(self) -> List[block.BannerPattern]:
        """List of patterns applied to the banner."""
        return self._raw_data.get('Patterns', [])

    @property
    def custom_name(self) -> Optional[str]:
        """Custom name for the banner, if any."""
        return self._raw_data.get('CustomName', None)

    @property
    def has_patterns(self) -> bool:
        """Check if banner has any patterns applied."""
        return len(self.patterns) > 0

    @property
    def base_color_name(self) -> str:
        """Get the color name for the base color."""
        return self.COLOR_NAMES.get(self.base_color_id, 'unknown')

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, base={self.base_color_id}>"


class Beacon(BaseEntity[str]):
    """
    Represents a beacon block entity in Minecraft.

    A beacon provides status effects to nearby players and requires a pyramid
    structure underneath to function. The number of levels determines the
    available effects and range.
    """
    __slots__ = ('_raw_data',)

    # Effect mappings
    EFFECT_NAMES: ClassVar[Dict[int, str]] = {1: 'speed', 3: 'haste', 5: 'strength', 8: 'jump_boost',
                                              10: 'regeneration', 11: 'resistance'}

    def __init__(self, entity_id: str, data: block.Beacon) -> None:
        super().__init__(entity_id)
        self._raw_data = data

    @property
    def primary_effect_id(self) -> int:
        """Primary effect ID provided by the beacon."""
        return self._raw_data['Primary']

    @property
    def secondary_effect_id(self) -> int:
        """Secondary effect ID provided by the beacon."""
        return self._raw_data['Secondary']

    @property
    def pyramid_levels(self) -> int:
        """Pyramid levels beneath the beacon (1-4)."""
        return self._raw_data['Levels']

    @property
    def lock_string(self) -> Optional[str]:
        """Lock string for the beacon, if any."""
        return self._raw_data['Lock'] or None

    @property
    def custom_name(self) -> Optional[str]:
        """Custom name for the beacon, if any."""
        return self._raw_data.get('CustomName', None)

    @property
    def is_fully_powered(self) -> bool:
        """Check if beacon has maximum power (4 levels)."""
        return self.pyramid_levels == 4

    @property
    def has_lock(self) -> bool:
        """Check if beacon is locked."""
        return self.lock_string is not None

    @property
    def primary_effect_name(self) -> str:
        """Get the name of the primary effect."""
        return self.EFFECT_NAMES.get(self.primary_effect_id, 'unknown')

    @property
    def secondary_effect_name(self) -> str:
        """Get the name of the secondary effect."""
        return self.EFFECT_NAMES.get(self.secondary_effect_id, 'unknown')

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, levels={self.pyramid_levels}>"


class Sign(BaseEntity[str]):
    """
    Represents a sign block entity in Minecraft.

    A sign displays up to 4 lines of text, each potentially containing
    formatted text with colors and styles.
    """
    __slots__ = ('_raw_data', '_text_cache')

    def __init__(self, entity_id: str, data: block.Sign) -> None:
        super().__init__(entity_id)
        self._raw_data = data
        self._text_cache = {}

    @property
    def text_1(self) -> Message:
        """First line of text on the sign."""
        if 'text_1' not in self._text_cache:
            self._text_cache['text_1'] = Message(self._raw_data['Text1'], to_json=True)
        return self._text_cache['text_1']

    @property
    def text_2(self) -> Message:
        """Second line of text on the sign."""
        if 'text_2' not in self._text_cache:
            self._text_cache['text_2'] = Message(self._raw_data['Text2'], to_json=True)
        return self._text_cache['text_2']

    @property
    def text_3(self) -> Message:
        """Third line of text on the sign."""
        if 'text_3' not in self._text_cache:
            self._text_cache['text_3'] = Message(self._raw_data['Text3'], to_json=True)
        return self._text_cache['text_3']

    @property
    def text_4(self) -> Message:
        """Fourth line of text on the sign."""
        if 'text_4' not in self._text_cache:
            self._text_cache['text_4'] = Message(self._raw_data['Text4'], to_json=True)
        return self._text_cache['text_4']

    @property
    def all_text_lines(self) -> List[Message]:
        """Get all text lines as a list."""
        return [self.text_1, self.text_2, self.text_3, self.text_4]

    @property
    def is_empty(self) -> bool:
        """Check if all text lines are empty."""
        return all(not str(line).strip() for line in self.all_text_lines)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"


class MobSpawner(BaseEntity[str]):
    """
    Represents a mob spawner block entity in Minecraft.

    A mob spawner generates entities at regular intervals based on various
    conditions and parameters.
    """
    __slots__ = ('_raw_data',)

    def __init__(self, entity_id: str, data: block.MobSpawner) -> None:
        super().__init__(entity_id)
        self._raw_data = data

    @property
    def delay(self) -> int:
        """Current delay until next spawn attempt (ticks)."""
        return self._raw_data.get('Delay', 20)

    @property
    def min_spawn_delay(self) -> int:
        """Minimum delay between spawns (ticks)."""
        return self._raw_data.get('MinSpawnDelay', 20)

    @property
    def max_spawn_delay(self) -> int:
        """Maximum delay between spawns (ticks)."""
        return self._raw_data.get('MaxSpawnDelay', 800)

    @property
    def spawn_count(self) -> int:
        """Number of entities to spawn per attempt."""
        return self._raw_data.get('SpawnCount', 4)

    @property
    def max_nearby_entities(self) -> int:
        """Maximum entities that can exist nearby."""
        return self._raw_data.get('MaxNearbyEntities', 6)

    @property
    def required_player_range(self) -> int:
        """Player must be within this range for spawning."""
        return self._raw_data.get('RequiredPlayerRange', 16)

    @property
    def spawn_range(self) -> int:
        """Range in which entities can spawn."""
        return self._raw_data.get('SpawnRange', 4)

    @property
    def spawn_data(self) -> Optional[block.MobSpawnerEntityData]:
        """Data for the entity to spawn."""
        return self._raw_data.get('SpawnData')

    @property
    def spawn_potentials(self) -> Optional[List[block.MobSpawnerSpawnPotentialEntry]]:
        """List of potential entities to spawn with weights."""
        return self._raw_data.get('SpawnPotentials')

    @property
    def custom_spawn_rules(self) -> Optional[Dict[str, Any]]:
        """Custom rules for spawning behavior."""
        return self._raw_data.get('custom_spawn_rules')

    @property
    def has_spawn_data(self) -> bool:
        """Check if spawner has spawn data configured."""
        return self.spawn_data is not None

    @property
    def has_spawn_potentials(self) -> bool:
        """Check if spawner has multiple spawn potentials."""
        return self.spawn_potentials is not None and len(self.spawn_potentials) > 0

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} delay={self.delay}, spawn_count={self.spawn_count}>"


class Skull(BaseEntity[str]):
    """
    Represents a skull block entity in Minecraft.

    A skull can be of different types (skeleton, wither skeleton, zombie, etc.)
    and can have custom player heads with specific owners.
    """
    __slots__ = ('_raw_data',)

    SKULL_TYPES: ClassVar[Dict[int, str]] = {
        0: 'skeleton',
        1: 'wither_skeleton',
        2: 'zombie',
        3: 'player',
        4: 'creeper',
        5: 'dragon'
    }

    def __init__(self, entity_id: str, data: block.Skull) -> None:
        super().__init__(entity_id)
        self._raw_data = data

    @property
    def rotation(self) -> int:
        """Rotation of the skull (0-15)."""
        return self._raw_data['Rot']

    @property
    def skull_type(self) -> int:
        """Type of skull (0=skeleton, 1=wither skeleton, 2=zombie, 3=player, 4=creeper, 5=dragon)."""
        return self._raw_data['SkullType']

    @property
    def owner(self) -> Optional[block.SkullOwner]:
        """Owner information for player heads."""
        return self._raw_data.get('Owner')

    @property
    def has_owner(self) -> bool:
        """Check if skull has an owner."""
        return self.owner is not None

    @property
    def skull_type_name(self) -> str:
        """Get the name of the skull type."""
        return self.SKULL_TYPES.get(self.skull_type, 'unknown')

    @property
    def is_player_head(self) -> bool:
        """Check if this is a player head."""
        return self.skull_type == 3

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} type={self.skull_type} rotation={self.rotation}>"


class StructureBlock(BaseEntity[str]):
    """
    Represents a structure block entity in Minecraft.

    Structure blocks are used to save, load, and manipulate structures
    in creative mode and with commands.
    """
    __slots__ = ('_raw_data', '_position_cache', '_size_cache')

    def __init__(self, entity_id: str, data: block.StructureBlock) -> None:
        super().__init__(entity_id)
        self._raw_data = data
        self._position_cache = None
        self._size_cache = None

    @property
    def metadata(self) -> str:
        """Additional metadata for the structure block."""
        return self._raw_data['metadata']

    @property
    def mirror(self) -> Literal['NONE', 'LEFT_RIGHT', 'FRONT_BACK']:
        """Mirror setting for structure placement."""
        return self._raw_data['mirror']

    @property
    def ignore_entities(self) -> int:
        """Whether to ignore entities when saving/loading."""
        return self._raw_data['ignoreEntities']

    @property
    def is_powered(self) -> bool:
        """Whether the structure block is powered."""
        return bool(self._raw_data['powered'])

    @property
    def seed(self) -> int:
        """Random seed for structure generation."""
        return self._raw_data['seed']

    @property
    def author(self) -> str:
        """Author of the structure."""
        return self._raw_data['author']

    @property
    def rotation(self) -> Literal['NONE', 'CLOCKWISE_90', 'CLOCKWISE_180', 'COUNTERCLOCKWISE_90']:
        """Rotation setting for structure placement."""
        return self._raw_data['rotation']

    @property
    def mode(self) -> Literal['SAVE', 'LOAD', 'CORNER', 'DATA']:
        """Current mode of the structure block."""
        return self._raw_data['mode']

    @property
    def position(self) -> Vector3D[int]:
        """Position offset for the structure."""
        if self._position_cache is None:
            self._position_cache = Vector3D(
                self._raw_data['posX'],
                self._raw_data['posY'],
                self._raw_data['posZ']
            )
        return self._position_cache

    @property
    def integrity(self) -> float:
        """Structural integrity percentage (0.0-1.0)."""
        return self._raw_data['integrity']

    @property
    def show_air_blocks(self) -> bool:
        """Whether to show air blocks in the structure."""
        return bool(self._raw_data['showair'])

    @property
    def name(self) -> str:
        """Name of the structure."""
        return self._raw_data['name']

    @property
    def size(self) -> Vector3D[int]:
        """Size of the structure in blocks."""
        if self._size_cache is None:
            self._size_cache = Vector3D(
                self._raw_data['sizeX'],
                self._raw_data['sizeY'],
                self._raw_data['sizeZ']
            )
        return self._size_cache

    @property
    def show_bounding_box(self) -> bool:
        """Whether to show the bounding box."""
        return bool(self._raw_data['showboundingbox'])

    @property
    def is_save_mode(self) -> bool:
        """Check if structure block is in save-mode."""
        return self.mode == 'SAVE'

    @property
    def is_load_mode(self) -> bool:
        """Check if structure block is in load mode."""
        return self.mode == 'LOAD'

    @property
    def volume(self) -> int:
        """Calculate the volume of the structure."""
        return self.size.x * self.size.y * self.size.z

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} mode={self.mode} position={self.position}>"


class EndGateway(BaseEntity[str]):
    """
    Represents an end gateway block entity in Minecraft.

    End gateways are portal blocks found in the End dimension that
    teleport players to different locations.
    """
    __slots__ = ('_raw_data', '_exit_portal_cache')

    def __init__(self, entity_id: str, data: block.EndGateway) -> None:
        super().__init__(entity_id)
        self._raw_data = data
        self._exit_portal_cache = None

    @property
    def age(self) -> int:
        """Age of the end gateway in ticks."""
        return self._raw_data['Age']

    @property
    def exit_portal(self) -> Optional[Vector3D[float]]:
        """Coordinates of the exit portal, if set."""
        if self._exit_portal_cache is None and self._raw_data.get('ExitPortal'):
            exit_data = self._raw_data['ExitPortal']
            self._exit_portal_cache = Vector3D(
                exit_data['X'],
                exit_data['Y'],
                exit_data['Z']
            )
        return self._exit_portal_cache

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} exit_portal={self.exit_portal}>"

    @property
    def has_exit_portal(self) -> bool:
        """Check if end gateway has an exit portal set."""
        return self.exit_portal is not None


class ShulkerBox(BaseEntity[str]):
    """
    Represents a shulker box block entity in Minecraft.

    Shulker boxes are portable storage containers that retain their
    contents when broken.
    """
    __slots__ = ('_raw_data',)

    def __init__(self, entity_id: str, data: Dict[str, Any]) -> None:
        super().__init__(entity_id)
        self._raw_data = data or None

    @property
    def raw_data(self) -> Optional[Dict[str, Any]]:
        """Raw data for the shulker box, if any."""
        return self._raw_data

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"

    @property
    def has_data(self) -> bool:
        """Check if shulker box has any data."""
        return self._raw_data is not None


class Bed(BaseEntity[str]):
    """
    Represents a bed block entity in Minecraft.
    """
    __slots__ = ('_raw_data',)

    # Color mappings same as Banner
    COLOR_NAMES: ClassVar[Dict[int, str]] = {
        0: 'white', 1: 'orange', 2: 'magenta', 3: 'light_blue',
        4: 'yellow', 5: 'lime', 6: 'pink', 7: 'gray',
        8: 'light_gray', 9: 'cyan', 10: 'purple', 11: 'blue',
        12: 'brown', 13: 'green', 14: 'red', 15: 'black'
    }

    def __init__(self, entity_id: str, data: block.Bed) -> None:
        super().__init__(entity_id)
        self._raw_data = data

    @property
    def color(self) -> str:
        """Color of the bed."""
        return self.COLOR_NAMES.get(self._raw_data['color'], 'unknown')

    def __repr__(self) -> str:
        return f"<Bed id={self.id} color={self.color}>"


class FlowerPot(BaseEntity[str]):
    """
    Represents a flower pot block entity in Minecraft.

    Flower pots can contain various plants and flowers for decoration.
    """
    __slots__ = ('_raw_data',)

    EMPTY_ITEM: ClassVar[str] = 'minecraft:air'

    def __init__(self, entity_id: str, data: block.FlowerPot) -> None:
        super().__init__(entity_id)
        self._raw_data = data

    @property
    def item(self) -> str:
        """Item contained in the flower pot."""
        return self._raw_data['Item']

    @property
    def item_data(self) -> int:
        """Metadata/damage value for the item."""
        return self._raw_data['Data']

    @property
    def is_empty(self) -> bool:
        """Check if flower pot is empty."""
        return self.item == self.EMPTY_ITEM

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} item={self.item}, data={self.item_data}>"