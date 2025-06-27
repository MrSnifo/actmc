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

from .entity import BaseEntity, ObjectEntity
from ..types.entities import block, entity
from ..math import Vector3D, Rotation
from typing import TYPE_CHECKING
from ..ui.chat import Message

if TYPE_CHECKING:
    from typing import List, Optional, Dict, Any, Literal, ClassVar


class Banner(BaseEntity[str]):
    """
    Represents a banner block entity in Minecraft.

    A banner is a decorative block that can display custom patterns and colors.
    Base colors correspond to dye colors (0-15).

    Attributes
    ----------
    base: int
        The base color of the banner (0-15 corresponding to dye colors).
    patterns: List[block.BannerPattern]
        List of patterns applied to the banner.
    custom_name: Optional[str]
        Custom name for the banner, if any.
    """
    __slots__ = ('base', 'patterns', 'custom_name')

    # Color mappings for reference
    COLOR_NAMES: ClassVar[Dict[int, str]] = {
        0: 'white', 1: 'orange', 2: 'magenta', 3: 'light_blue',
        4: 'yellow', 5: 'lime', 6: 'pink', 7: 'gray',
        8: 'light_gray', 9: 'cyan', 10: 'purple', 11: 'blue',
        12: 'brown', 13: 'green', 14: 'red', 15: 'black'
    }

    def __init__(self, entity_id: str, data: block.Banner) -> None:
        super().__init__(entity_id)
        self.base: int = data['Base']
        self.patterns: List[block.BannerPattern] = data.get('Patterns', [])
        self.custom_name: Optional[str] = data.get('CustomName', None)

    def __repr__(self) -> str:
        return f"<Banner id={self.id}, base={self.base}>"

    @property
    def has_patterns(self) -> bool:
        """Check if banner has any patterns applied."""
        return len(self.patterns) > 0

    @property
    def color_name(self) -> str:
        """Get the color name for the base color."""
        return self.COLOR_NAMES.get(self.base, 'unknown')


class Beacon(BaseEntity[str]):
    """
    Represents a beacon block entity in Minecraft.

    A beacon provides status effects to nearby players and requires a pyramid
    structure underneath to function. The number of levels determines the
    available effects and range.

    Attributes
    ----------
    primary: int
        Primary effect ID provided by the beacon.
    secondary: int
        Secondary effect ID provided by the beacon.
    levels: int
        Pyramid levels beneath the beacon (1-4).
    lock: Optional[str]
        Lock string for the beacon, if any.
    custom_name: Optional[str]
        Custom name for the beacon, if any.
    """
    __slots__ = ('primary', 'secondary', 'levels', 'lock', 'custom_name')

    # Effect mappings
    EFFECT_NAMES: ClassVar[Dict[int, str]] = {1: 'speed', 3: 'haste', 5: 'strength', 8: 'jump_boost',
                                              10: 'regeneration', 11: 'resistance'}
    MAX_LEVELS: ClassVar[int] = 4
    MIN_LEVELS: ClassVar[int] = 1

    def __init__(self, entity_id: str, data: block.Beacon) -> None:
        super().__init__(entity_id)
        self.primary: int = data['Primary']
        self.secondary: int = data['Secondary']
        self.levels: int = data['Levels']
        self.lock: Optional[str] = data['Lock'] or None
        self.custom_name: Optional[str] = data.get('CustomName', None)

    def __repr__(self) -> str:
        return f"<Beacon id={self.id}, primary={self.primary}, secondary={self.secondary}, levels={self.levels}>"

    @property
    def is_fully_powered(self) -> bool:
        """Check if beacon has maximum power (4 levels)."""
        return self.levels == self.MAX_LEVELS

    @property
    def has_lock(self) -> bool:
        """Check if beacon is locked."""
        return self.lock is not None

    @property
    def primary_effect_name(self) -> str:
        """Get the name of the primary effect."""
        return self.EFFECT_NAMES.get(self.primary, 'unknown')

    @property
    def secondary_effect_name(self) -> str:
        """Get the name of the secondary effect."""
        return self.EFFECT_NAMES.get(self.secondary, 'unknown')


class Sign(BaseEntity[str]):
    """
    Represents a sign block entity in Minecraft.

    A sign displays up to 4 lines of text, each potentially containing
    formatted text with colors and styles.

    Attributes
    ----------
    text_1: Message
        First line of text on the sign.
    text_2: Message
        Second line of text on the sign.
    text_3: Message
        Third line of text on the sign.
    text_4: Message
        Fourth line of text on the sign.
    """
    __slots__ = ('text_1', 'text_2', 'text_3', 'text_4')

    def __init__(self, entity_id: str, data: block.Sign) -> None:
        super().__init__(entity_id)
        self.text_1: Message = Message(data['Text1'], to_json=True)
        self.text_2: Message = Message(data['Text2'], to_json=True)
        self.text_3: Message = Message(data['Text3'], to_json=True)
        self.text_4: Message = Message(data['Text4'], to_json=True)

    def __repr__(self) -> str:
        return f"<Sign id={self.id}>"

    @property
    def all_text_lines(self) -> List[Message]:
        """Get all text lines as a list."""
        return [self.text_1, self.text_2, self.text_3, self.text_4]

    @property
    def is_empty(self) -> bool:
        """Check if all text lines are empty."""
        return all(not str(line).strip() for line in self.all_text_lines)


class MobSpawner(BaseEntity[str]):
    """
    Represents a mob spawner block entity in Minecraft.

    A mob spawner generates entities at regular intervals based on various
    conditions and parameters.

    Attributes
    ----------
    delay: int
        Current delay until next spawn attempt (ticks).
    min_spawn_delay: int
        Minimum delay between spawns (ticks).
    max_spawn_delay: int
        Maximum delay between spawns (ticks).
    spawn_count: int
        Number of entities to spawn per attempt.
    max_nearby_entities: int
        Maximum entities that can exist nearby.
    required_player_range: int
        Player must be within this range for spawning.
    spawn_range: int
        Range in which entities can spawn.
    spawn_data: Optional[block.MobSpawnerEntityData]
        Data for the entity to spawn.
    spawn_potentials: Optional[List[block.MobSpawnerSpawnPotentialEntry]]
        List of potential entities to spawn with weights.
    custom_spawn_rules: Optional[Dict[str, Any]]
        Custom rules for spawning behavior.
    """
    __slots__ = (
        'delay', 'min_spawn_delay', 'max_spawn_delay', 'spawn_count',
        'max_nearby_entities', 'required_player_range', 'spawn_range',
        'spawn_data', 'spawn_potentials', 'custom_spawn_rules',
    )

    # Default values as class constants
    DEFAULT_DELAY: ClassVar[int] = 20
    DEFAULT_MIN_SPAWN_DELAY: ClassVar[int] = 200
    DEFAULT_MAX_SPAWN_DELAY: ClassVar[int] = 800
    DEFAULT_SPAWN_COUNT: ClassVar[int] = 4
    DEFAULT_MAX_NEARBY_ENTITIES: ClassVar[int] = 6
    DEFAULT_REQUIRED_PLAYER_RANGE: ClassVar[int] = 16
    DEFAULT_SPAWN_RANGE: ClassVar[int] = 4

    def __init__(self, entity_id: str, data: block.MobSpawner) -> None:
        super().__init__(entity_id)
        self.delay: int = data.get('Delay', self.DEFAULT_DELAY)
        self.min_spawn_delay: int = data.get('MinSpawnDelay', self.DEFAULT_MIN_SPAWN_DELAY)
        self.max_spawn_delay: int = data.get('MaxSpawnDelay', self.DEFAULT_MAX_SPAWN_DELAY)
        self.spawn_count: int = data.get('SpawnCount', self.DEFAULT_SPAWN_COUNT)
        self.max_nearby_entities: int = data.get('MaxNearbyEntities', self.DEFAULT_MAX_NEARBY_ENTITIES)
        self.required_player_range: int = data.get('RequiredPlayerRange', self.DEFAULT_REQUIRED_PLAYER_RANGE)
        self.spawn_range: int = data.get('SpawnRange', self.DEFAULT_SPAWN_RANGE)
        self.spawn_data: Optional[block.MobSpawnerEntityData] = data.get('SpawnData')
        self.spawn_potentials: Optional[List[block.MobSpawnerSpawnPotentialEntry]] = data.get('SpawnPotentials')
        self.custom_spawn_rules: Optional[Dict[str, Any]] = data.get('custom_spawn_rules')

    def __repr__(self) -> str:
        return f"<MobSpawner id={self.id} delay={self.delay}, spawn_count={self.spawn_count}>"

    @property
    def has_spawn_data(self) -> bool:
        """Check if spawner has spawn data configured."""
        return self.spawn_data is not None

    @property
    def has_spawn_potentials(self) -> bool:
        """Check if spawner has multiple spawn potentials."""
        return self.spawn_potentials is not None and len(self.spawn_potentials) > 0


class Skull(BaseEntity[str]):
    """
    Represents a skull block entity in Minecraft.

    A skull can be of different types (skeleton, wither skeleton, zombie, etc.)
    and can have custom player heads with specific owners.

    Attributes
    ----------
    rotation: int
        Rotation of the skull (0-15).
    skull_type: int
        Type of skull (0=skeleton, 1=wither skeleton, 2=zombie, 3=player, 4=creeper, 5=dragon).
    owner: Optional[block.SkullOwner]
        Owner information for player heads.
    """
    __slots__ = ('rotation', 'skull_type', 'owner')

    # Valid skull types
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
        self.rotation: int = data['Rot']
        self.skull_type: int = data['SkullType']
        self.owner: Optional[block.SkullOwner] = data.get('Owner')

    @property
    def has_owner(self) -> bool:
        """
        Check if skull has an owner.

        Returns
        -------
        bool
            True if skull has owner information, False otherwise.
        """
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
        return f"<Skull id={self.id} type={self.skull_type} rotation={self.rotation}>"


class StructureBlock(BaseEntity[str]):
    """
    Represents a structure block entity in Minecraft.

    Structure blocks are used to save, load, and manipulate structures
    in creative mode and with commands.

    Attributes
    ----------
    metadata: str
        Additional metadata for the structure block.
    mirror: Literal['NONE', 'LEFT_RIGHT', 'FRONT_BACK']
        Mirror setting for structure placement.
    ignoreEntities: int
        Whether to ignore entities when saving/loading.
    powered: int
        Whether the structure block is powered.
    seed: int
        Random seed for structure generation.
    author: str
        Author of the structure.
    rotation: Literal['NONE', 'CLOCKWISE_90', 'CLOCKWISE_180', 'COUNTERCLOCKWISE_90']
        Rotation setting for structure placement.
    mode: Literal['SAVE', 'LOAD', 'CORNER', 'DATA']
        Current mode of the structure block.
    position: Vector3D[int]
        Position offset for the structure.
    integrity: float
        Structural integrity percentage (0.0-1.0).
    showair: int
        Whether to show air blocks in the structure.
    name: str
        Name of the structure.
    size: Vector3D[int]
        Size of the structure in blocks.
    showboundingbox: int
        Whether to show the bounding box.
    """
    __slots__ = (
        'metadata', 'mirror', 'ignoreEntities', 'powered', 'seed', 'author',
        'rotation', 'mode', 'position', 'integrity', 'showair', 'name',
        'size', 'showboundingbox'
    )

    def __init__(self, entity_id: str, data: block.StructureBlock) -> None:
        super().__init__(entity_id)
        self.metadata: str = data['metadata']
        self.mirror: Literal['NONE', 'LEFT_RIGHT', 'FRONT_BACK'] = data['mirror']
        self.ignoreEntities: int = data['ignoreEntities']
        self.powered: int = data['powered']
        self.seed: int = data['seed']
        self.author: str = data['author']
        self.rotation: Literal['NONE', 'CLOCKWISE_90', 'CLOCKWISE_180', 'COUNTERCLOCKWISE_90'] = data['rotation']
        self.mode: Literal['SAVE', 'LOAD', 'CORNER', 'DATA'] = data['mode']
        self.position: Vector3D[int] = Vector3D(data['posX'], data['posY'], data['posZ'])
        self.integrity: float = data['integrity']
        self.showair: int = data['showair']
        self.name: str = data['name']
        self.size: Vector3D[int] = Vector3D(data['sizeX'], data['sizeY'], data['sizeZ'])
        self.showboundingbox: int = data['showboundingbox']

    def __repr__(self) -> str:
        return (
            f"<StructureBlock mode={self.mode} name={self.name!r} position={self.position} size={self.size} "
            f"rotation={self.rotation} mirror={self.mirror}>"
        )

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


class EndGateway(BaseEntity[str]):
    """
    Represents an end gateway block entity in Minecraft.

    End gateways are portal blocks found in the End dimension that
    teleport players to different locations.

    Attributes
    ----------
    age: int
        Age of the end gateway in ticks.
    exit_portal: Optional[Vector3D[float]]
        Coordinates of the exit portal, if set.
    """
    __slots__ = ('age', 'exit_portal')

    def __init__(self, entity_id: str, data: block.EndGateway) -> None:
        super().__init__(entity_id)
        self.age: int = data['Age']
        self.exit_portal: Optional[Vector3D[float]] = Vector3D(data['ExitPortal']['X'],
                                                             data['ExitPortal']['Y'],
                                                             data['ExitPortal']['Z']
                                                        ) if data.get('ExitPortal') else None

    def __repr__(self) -> str:
        return f"<EndGateway id={self.id} exit_portal={self.exit_portal}>"

    @property
    def has_exit_portal(self) -> bool:
        """Check if end gateway has an exit portal set."""
        return self.exit_portal is not None


class ShulkerBox(BaseEntity[str]):
    """
    Represents a shulker box block entity in Minecraft.

    Shulker boxes are portable storage containers that retain their
    contents when broken.

    Attributes
    ----------
    raw_data: Optional[Dict[str, Any]]
        Raw data for the shulker box, if any.
    """
    __slots__ = ('raw_data',)

    def __init__(self, entity_id: str, data: Dict[str, Any]) -> None:
        super().__init__(entity_id)
        self.raw_data: Optional[Dict[str, Any]] = data or None

    def __repr__(self) -> str:
        return f"<ShulkerBox id={self.id}>"

    @property
    def has_data(self) -> bool:
        """Check if shulker box has any data."""
        return self.raw_data is not None


class Bed(BaseEntity[str]):
    """
    Represents a bed block entity in Minecraft.

    Attributes
    ----------
    color: int
        Color of the bed (0-15 corresponding to dye colors).
    """
    __slots__ = ('color',)

    # Color mappings same as Banner
    COLOR_NAMES: ClassVar[Dict[int, str]] = {
        0: 'white', 1: 'orange', 2: 'magenta', 3: 'light_blue',
        4: 'yellow', 5: 'lime', 6: 'pink', 7: 'gray',
        8: 'light_gray', 9: 'cyan', 10: 'purple', 11: 'blue',
        12: 'brown', 13: 'green', 14: 'red', 15: 'black'
    }

    def __init__(self, entity_id: str, data: block.Bed) -> None:
        super().__init__(entity_id)
        self.color: str = self.COLOR_NAMES.get(data['color'], 'unknown')

    def __repr__(self) -> str:
        return f"<Bed id={self.id} color={self.color}>"


class FlowerPot(BaseEntity[str]):
    """
    Represents a flower pot block entity in Minecraft.

    Flower pots can contain various plants and flowers for decoration.

    Attributes
    ----------
    item: str
        Item contained in the flower pot.
    data: int
        Metadata/damage value for the item.
    """
    __slots__ = ('item', 'data')

    EMPTY_ITEM: ClassVar[str] = 'minecraft:air'

    def __init__(self, entity_id: str, data: block.FlowerPot) -> None:
        super().__init__(entity_id)
        self.item: str = data['Item']
        self.data: int = data['Data']

    @property
    def is_empty(self) -> bool:
        """
        Check if flower pot is empty.

        Returns
        -------
        bool
            True if flower pot contains air (is empty), False otherwise.
        """
        return self.item == self.EMPTY_ITEM

    def __repr__(self) -> str:
        return f"<FlowerPot item={self.item}, data={self.data}>"


class FallingBlock(ObjectEntity):
    """
    Represents a falling block entity in Minecraft.

    Falling blocks are temporary entities created when gravity-affected
    blocks (like sand or gravel) lose their support.

    Attributes
    ----------
    block_id: int
        ID of the falling block type.
    rotation: Rotation
        of the falling block.
    metadata: int
        Metadata value for the block.
    """
    __slots__ = ('block_id', 'rotation', 'metadata')

    # Bit masks for data extraction
    BLOCK_ID_MASK: ClassVar[int] = 0xFFF
    METADATA_MASK: ClassVar[int] = 0xF
    METADATA_SHIFT: ClassVar[int] = 12

    def __init__(self, data: entity.SpawnObject) -> None:
        super().__init__(data['entity_id'], data['type'], data['uuid'], Vector3D(data['x'], data['y'], data['z']))
        self.rotation: Rotation = Rotation(data['pitch'], data['yaw'])
        self.block_id: int = data['data'] & self.BLOCK_ID_MASK
        self.metadata: int = (data['data'] >> self.METADATA_SHIFT) & self.METADATA_MASK

    def __repr__(self) -> str:
        return f"<FallingBlock id={self.id}, block_id={self.block_id}, position={self.position}>"

    @property
    def has_metadata(self) -> bool:
        """Check if falling block has metadata."""
        return self.metadata > 0