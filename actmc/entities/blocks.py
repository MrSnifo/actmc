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

from ..types import entities
from typing import TYPE_CHECKING
from .entity import BaseEntity
from ..ui.chat import Message
from ..math import Vector3D

if TYPE_CHECKING:
    from typing import List, Optional, Dict, Any, Literal, ClassVar

__all__ = ('Banner', 'Beacon', 'Sign', 'MobSpawner', 'Skull', 'StructureBlock', 'EndGateway', 'ShulkerBox', 'Bed',
           'FlowerPot')

class Banner(BaseEntity[str]):
    """Represents a banner block entity."""

    __slots__ = ('_raw_data',)

    # Color mappings for reference
    COLOR_NAMES: ClassVar[Dict[int, str]] = {
        0: 'white', 1: 'orange', 2: 'magenta', 3: 'light_blue',
        4: 'yellow', 5: 'lime', 6: 'pink', 7: 'gray',
        8: 'light_gray', 9: 'cyan', 10: 'purple', 11: 'blue',
        12: 'brown', 13: 'green', 14: 'red', 15: 'black'
    }

    def __init__(self, entity_id: str, data: entities.Banner) -> None:
        super().__init__(entity_id)
        self._raw_data = data

    @property
    def base_color_id(self) -> int:
        """
        The base color of the banner.

        Returns
        -------
        int
            Base color ID (0-15) corresponding to dye colors.
        """
        return self._raw_data['Base']

    @property
    def patterns(self) -> List[entities.BannerPattern]:
        """
        List of patterns applied to the banner.

        Returns
        -------
        List[entities.BannerPattern]
            Collection of banner patterns with their configurations.
        """
        return self._raw_data.get('Patterns', [])

    @property
    def custom_name(self) -> Optional[str]:
        """
        Custom name for the banner.

        Returns
        -------
        Optional[str]
            Custom display name if set, None otherwise.
        """
        return self._raw_data.get('CustomName', None)

    @property
    def has_patterns(self) -> bool:
        """
        Check if banner has any patterns applied.

        Returns
        -------
        bool
            True if banner has one or more patterns, False otherwise.
        """
        return len(self.patterns) > 0

    @property
    def base_color_name(self) -> str:
        """
        Get the color name for the base color.

        Returns
        -------
        str
            Human-readable color name corresponding to the base color ID.
        """
        return self.COLOR_NAMES.get(self.base_color_id, 'unknown')

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, base={self.base_color_id}>"


class Beacon(BaseEntity[str]):
    """Represents a beacon block entity. """

    __slots__ = ('_raw_data',)

    # Effect mappings.
    EFFECT_NAMES: ClassVar[Dict[int, str]] = {1: 'speed', 3: 'haste', 5: 'strength', 8: 'jump_boost',
                                              10: 'regeneration', 11: 'resistance'}

    def __init__(self, entity_id: str, data: entities.Beacon) -> None:
        super().__init__(entity_id)
        self._raw_data = data

    @property
    def primary_effect_id(self) -> int:
        """
        Primary effect ID provided by the beacon.

        Returns
        -------
        int
            Numeric identifier for the primary status effect.
        """
        return self._raw_data['Primary']

    @property
    def secondary_effect_id(self) -> int:
        """
        Secondary effect ID provided by the beacon.

        Returns
        -------
        int
            Numeric identifier for the secondary status effect.
        """
        return self._raw_data['Secondary']

    @property
    def pyramid_levels(self) -> int:
        """
        Pyramid levels beneath the beacon.

        Returns
        -------
        int
            Number of pyramid levels (1-4) supporting the beacon.
        """
        return self._raw_data['Levels']

    @property
    def lock_string(self) -> Optional[str]:
        """
        Lock string for the beacon.

        Returns
        -------
        Optional[str]
            Lock string if beacon is locked, None otherwise.
        """
        return self._raw_data['Lock'] or None

    @property
    def custom_name(self) -> Optional[str]:
        """
        Custom name for the beacon.

        Returns
        -------
        Optional[str]
            Custom display name if set, None otherwise.
        """
        return self._raw_data.get('CustomName', None)

    @property
    def is_fully_powered(self) -> bool:
        """
        Check if beacon has maximum power.

        Returns
        -------
        bool
            True if beacon has 4 pyramid levels (maximum), False otherwise.
        """
        return self.pyramid_levels == 4

    @property
    def has_lock(self) -> bool:
        """
        Check if beacon is locked.

        Returns
        -------
        bool
            True if beacon has a lock string set, False otherwise.
        """
        return self.lock_string is not None

    @property
    def primary_effect_name(self) -> str:
        """
        Get the name of the primary effect.

        Returns
        -------
        str
            Human-readable name of the primary effect.
        """
        return self.EFFECT_NAMES.get(self.primary_effect_id, 'unknown')

    @property
    def secondary_effect_name(self) -> str:
        """
        Get the name of the secondary effect.

        Returns
        -------
        str
            Human-readable name of the secondary effect.
        """
        return self.EFFECT_NAMES.get(self.secondary_effect_id, 'unknown')

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, levels={self.pyramid_levels}>"


class Sign(BaseEntity[str]):
    """Represents a sign block entity."""
    __slots__ = ('_raw_data', '_text_cache')

    def __init__(self, entity_id: str, data: entities.Sign) -> None:
        super().__init__(entity_id)
        self._raw_data = data
        self._text_cache = {}

    @property
    def text_1(self) -> Message:
        """
        First line of text on the sign.

        Returns
        -------
        Message
            Formatted message object containing the first line text.
        """
        if 'text_1' not in self._text_cache:
            self._text_cache['text_1'] = Message(self._raw_data['Text1'], to_json=True)
        return self._text_cache['text_1']

    @property
    def text_2(self) -> Message:
        """
        Second line of text on the sign.

        Returns
        -------
        Message
            Formatted message object containing the second line text.
        """
        if 'text_2' not in self._text_cache:
            self._text_cache['text_2'] = Message(self._raw_data['Text2'], to_json=True)
        return self._text_cache['text_2']

    @property
    def text_3(self) -> Message:
        """
        Third line of text on the sign.

        Returns
        -------
        Message
            Formatted message object containing the third line text.
        """
        if 'text_3' not in self._text_cache:
            self._text_cache['text_3'] = Message(self._raw_data['Text3'], to_json=True)
        return self._text_cache['text_3']

    @property
    def text_4(self) -> Message:
        """
        Fourth line of text on the sign.

        Returns
        -------
        Message
            Formatted message object containing the fourth line text.
        """
        if 'text_4' not in self._text_cache:
            self._text_cache['text_4'] = Message(self._raw_data['Text4'], to_json=True)
        return self._text_cache['text_4']

    @property
    def all_text_lines(self) -> List[Message]:
        """
        Get all text lines as a list.

        Returns
        -------
        List[Message]
            List containing all four text lines as Message objects.
        """
        return [self.text_1, self.text_2, self.text_3, self.text_4]

    @property
    def is_empty(self) -> bool:
        """
        Check if all text lines are empty.

        Returns
        -------
        bool
            True if all text lines contain only whitespace or are empty, False otherwise.
        """
        return all(not str(line).strip() for line in self.all_text_lines)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"


class MobSpawner(BaseEntity[str]):
    """Represents a mob spawner block entity."""
    __slots__ = ('_raw_data',)

    def __init__(self, entity_id: str, data: entities.MobSpawner) -> None:
        super().__init__(entity_id)
        self._raw_data = data

    @property
    def delay(self) -> int:
        """
        Current delay until next spawn attempt.

        Returns
        -------
        int
            Time in ticks until the next spawn attempt.
        """
        return self._raw_data.get('Delay', 20)

    @property
    def min_spawn_delay(self) -> int:
        """
        Minimum delay between spawns.

        Returns
        -------
        int
            Minimum time in ticks between spawn attempts.
        """
        return self._raw_data.get('MinSpawnDelay', 20)

    @property
    def max_spawn_delay(self) -> int:
        """
        Maximum delay between spawns.

        Returns
        -------
        int
            Maximum time in ticks between spawn attempts.
        """
        return self._raw_data.get('MaxSpawnDelay', 800)

    @property
    def spawn_count(self) -> int:
        """
        Number of entities to spawn per attempt.

        Returns
        -------
        int
            Count of entities spawned in each spawn attempt.
        """
        return self._raw_data.get('SpawnCount', 4)

    @property
    def max_nearby_entities(self) -> int:
        """
        Maximum entities that can exist nearby.

        Returns
        -------
        int
            Maximum number of entities allowed in the spawning area.
        """
        return self._raw_data.get('MaxNearbyEntities', 6)

    @property
    def required_player_range(self) -> int:
        """
        Player must be within this range for spawning.

        Returns
        -------
        int
            Maximum distance in blocks a player can be for spawning to occur.
        """
        return self._raw_data.get('RequiredPlayerRange', 16)

    @property
    def spawn_range(self) -> int:
        """
        Range in which entities can spawn.

        Returns
        -------
        int
            Radius in blocks around the spawner where entities can appear.
        """
        return self._raw_data.get('SpawnRange', 4)

    @property
    def spawn_data(self) -> Optional[entities.MobSpawnerEntityData]:
        """
        Data for the entity to spawn.

        Returns
        -------
        Optional[entities.MobSpawnerEntityData]
            Entity configuration data if set, None otherwise.
        """
        return self._raw_data.get('SpawnData')

    @property
    def spawn_potentials(self) -> Optional[List[entities.MobSpawnerSpawnPotentialEntry]]:
        """
        List of potential entities to spawn with weights.

        Returns
        -------
        Optional[List[entities.MobSpawnerSpawnPotentialEntry]]
            List of spawn potential entries with weights, None if not configured.
        """
        return self._raw_data.get('SpawnPotentials')

    @property
    def custom_spawn_rules(self) -> Optional[Dict[str, Any]]:
        """
        Custom rules for spawning behavior.

        Returns
        -------
        Optional[Dict[str, Any]]
            Dictionary of custom spawn rules if set, None otherwise.
        """
        return self._raw_data.get('custom_spawn_rules')

    @property
    def has_spawn_data(self) -> bool:
        """
        Check if spawner has spawn data configured.

        Returns
        -------
        bool
            True if spawn data is configured, False otherwise.
        """
        return self.spawn_data is not None

    @property
    def has_spawn_potentials(self) -> bool:
        """
        Check if spawner has multiple spawn potentials.

        Returns
        -------
        bool
            True if spawn potentials list exists and is not empty, False otherwise.
        """
        return self.spawn_potentials is not None and len(self.spawn_potentials) > 0

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} delay={self.delay}, spawn_count={self.spawn_count}>"


class Skull(BaseEntity[str]):
    """Represents a skull block entity."""
    __slots__ = ('_raw_data',)

    SKULL_TYPES: ClassVar[Dict[int, str]] = {
        0: 'skeleton',
        1: 'wither_skeleton',
        2: 'zombie',
        3: 'player',
        4: 'creeper',
        5: 'dragon'
    }

    def __init__(self, entity_id: str, data: entities.Skull) -> None:
        super().__init__(entity_id)
        self._raw_data = data

    @property
    def rotation(self) -> int:
        """
        Rotation of the skull.

        Returns
        -------
        int
            Rotation value from 0-15 representing 16 possible orientations.
        """
        return self._raw_data['Rot']

    @property
    def skull_type(self) -> int:
        """
        Type of skull.

        Returns
        -------
        int
            Skull type ID: 0=skeleton, 1=wither skeleton, 2=zombie,
            3=player, 4=creeper, 5=dragon.
        """
        return self._raw_data['SkullType']

    @property
    def owner(self) -> Optional[entities.SkullOwner]:
        """
        Owner information for player heads.

        Returns
        -------
        Optional[entities.SkullOwner]
            Owner data for player heads, None for non-player skulls.
        """
        return self._raw_data.get('Owner')

    @property
    def has_owner(self) -> bool:
        """
        Check if skull has an owner.

        Returns
        -------
        bool
            True if skull has owner information (player head), False otherwise.
        """
        return self.owner is not None

    @property
    def skull_type_name(self) -> str:
        """
        Get the name of the skull type.

        Returns
        -------
        str
            Human-readable name of the skull type.
        """
        return self.SKULL_TYPES.get(self.skull_type, 'unknown')

    @property
    def is_player_head(self) -> bool:
        """
        Check if this is a player head.

        Returns
        -------
        bool
            True if skull type is 3 (player), False otherwise.
        """
        return self.skull_type == 3

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} type={self.skull_type} rotation={self.rotation}>"


class StructureBlock(BaseEntity[str]):
    """
    Represents a structure block entity.
    """
    __slots__ = ('_raw_data', '_position_cache', '_size_cache')

    def __init__(self, entity_id: str, data: entities.StructureBlock) -> None:
        super().__init__(entity_id)
        self._raw_data = data
        self._position_cache = None
        self._size_cache = None

    @property
    def metadata(self) -> str:
        """
        Additional metadata for the structure entities.

        Returns
        -------
        str
            Metadata string associated with the structure entities.
        """
        return self._raw_data['metadata']

    @property
    def mirror(self) -> Literal['NONE', 'LEFT_RIGHT', 'FRONT_BACK']:
        """
        Mirror setting for structure placement.

        Returns
        -------
        Literal['NONE', 'LEFT_RIGHT', 'FRONT_BACK']
            Mirror configuration for structure operations.
        """
        return self._raw_data['mirror']

    @property
    def ignore_entities(self) -> int:
        """
        Whether to ignore entities when saving/loading.

        Returns
        -------
        int
            Flag indicating if entities should be ignored (1) or included (0).
        """
        return self._raw_data['ignoreEntities']

    @property
    def is_powered(self) -> bool:
        """
        Whether the structure block is powered.

        Returns
        -------
        bool
            True if structure block is receiving redstone power, False otherwise.
        """
        return bool(self._raw_data['powered'])

    @property
    def seed(self) -> int:
        """
        Random seed for structure generation.

        Returns
        -------
        int
            Seed value used for randomization in structure operations.
        """
        return self._raw_data['seed']

    @property
    def author(self) -> str:
        """
        Author of the structure.

        Returns
        -------
        str
            Name of the player who created or last modified the structure.
        """
        return self._raw_data['author']

    @property
    def rotation(self) -> Literal['NONE', 'CLOCKWISE_90', 'CLOCKWISE_180', 'COUNTERCLOCKWISE_90']:
        """
        Rotation setting for structure placement.

        Returns
        -------
        Literal['NONE', 'CLOCKWISE_90', 'CLOCKWISE_180', 'COUNTERCLOCKWISE_90']
            Rotation configuration for structure operations.
        """
        return self._raw_data['rotation']

    @property
    def mode(self) -> Literal['SAVE', 'LOAD', 'CORNER', 'DATA']:
        """
        Current mode of the structure entities.

        Returns
        -------
        Literal['SAVE', 'LOAD', 'CORNER', 'DATA']
            Operating mode of the structure entities.
        """
        return self._raw_data['mode']

    @property
    def position(self) -> Vector3D[int]:
        """
        Position offset for the structure.

        Returns
        -------
        Vector3D[int]
            3D coordinate offset relative to the structure entities.
        """
        if self._position_cache is None:
            self._position_cache = Vector3D(
                self._raw_data['posX'],
                self._raw_data['posY'],
                self._raw_data['posZ']
            )
        return self._position_cache

    @property
    def integrity(self) -> float:
        """
        Structural integrity percentage.

        Returns
        -------
        float
            Integrity value from 0.0 to 1.0 representing structure completeness.
        """
        return self._raw_data['integrity']

    @property
    def show_air_blocks(self) -> bool:
        """
        Whether to show air blocks in the structure.

        Returns
        -------
        bool
            True if air blocks should be visible, False otherwise.
        """
        return bool(self._raw_data['showair'])

    @property
    def name(self) -> str:
        """
        Name of the structure.

        Returns
        -------
        str
            Structure identifier name.
        """
        return self._raw_data['name']

    @property
    def size(self) -> Vector3D[int]:
        """
        Size of the structure in blocks.

        Returns
        -------
        Vector3D[int]
            3D dimensions of the structure (width, height, depth).
        """
        if self._size_cache is None:
            self._size_cache = Vector3D(
                self._raw_data['sizeX'],
                self._raw_data['sizeY'],
                self._raw_data['sizeZ']
            )
        return self._size_cache

    @property
    def show_bounding_box(self) -> bool:
        """
        Whether to show the bounding box.

        Returns
        -------
        bool
            True if bounding box visualization is enabled, False otherwise.
        """
        return bool(self._raw_data['showboundingbox'])

    @property
    def is_save_mode(self) -> bool:
        """
        Check if structure block is in save mode.

        Returns
        -------
        bool
            True if mode is 'SAVE', False otherwise.
        """
        return self.mode == 'SAVE'

    @property
    def is_load_mode(self) -> bool:
        """
        Check if structure block is in load mode.

        Returns
        -------
        bool
            True if mode is 'LOAD', False otherwise.
        """
        return self.mode == 'LOAD'

    @property
    def volume(self) -> int:
        """
        Calculate the volume of the structure.

        Returns
        -------
        int
            Total volume in blocks (width × height × depth).
        """
        return self.size.x * self.size.y * self.size.z

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} mode={self.mode} position={self.position}>"


class EndGateway(BaseEntity[str]):
    """Represents an end gateway block entity."""

    __slots__ = ('_raw_data', '_exit_portal_cache')

    def __init__(self, entity_id: str, data: entities.EndGateway) -> None:
        super().__init__(entity_id)
        self._raw_data = data
        self._exit_portal_cache = None

    @property
    def age(self) -> int:
        """
        Age of the end gateway.

        Returns
        -------
        int
            Time in ticks since the gateway was created.
        """
        return self._raw_data['Age']

    @property
    def exit_portal(self) -> Optional[Vector3D[float]]:
        """
        Coordinates of the exit portal.

        Returns
        -------
        Optional[Vector3D[float]]
            3D coordinates of the destination portal, None if not set.
        """
        if self._exit_portal_cache is None and self._raw_data.get('ExitPortal'):
            exit_data = self._raw_data['ExitPortal']
            self._exit_portal_cache = Vector3D(
                exit_data['X'],
                exit_data['Y'],
                exit_data['Z']
            )
        return self._exit_portal_cache

    @property
    def has_exit_portal(self) -> bool:
        """
        Check if end gateway has an exit portal set.

        Returns
        -------
        bool
            True if exit portal coordinates are configured, False otherwise.
        """
        return self.exit_portal is not None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} exit_portal={self.exit_portal}>"


class ShulkerBox(BaseEntity[str]):
    """Represents a shulker box block entity."""

    __slots__ = ('_raw_data',)

    def __init__(self, entity_id: str, data: Dict[str, Any]) -> None:
        super().__init__(entity_id)
        self._raw_data = data or None

    @property
    def raw_data(self) -> Optional[Dict[str, Any]]:
        """
        Raw data for the shulker box.

        Returns
        -------
        Optional[Dict[str, Any]]
            Dictionary containing shulker box data, None if no data available.
        """
        return self._raw_data

    @property
    def has_data(self) -> bool:
        """
        Check if shulker box has any data.

        Returns
        -------
        bool
            True if raw data is available, False otherwise.
        """
        return self._raw_data is not None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"


class Bed(BaseEntity[str]):
    """
    Represents a bed block entity.
    """
    __slots__ = ('_raw_data',)

    # Color mappings same as Banner
    COLOR_NAMES: ClassVar[Dict[int, str]] = {
        0: 'white', 1: 'orange', 2: 'magenta', 3: 'light_blue',
        4: 'yellow', 5: 'lime', 6: 'pink', 7: 'gray',
        8: 'light_gray', 9: 'cyan', 10: 'purple', 11: 'blue',
        12: 'brown', 13: 'green', 14: 'red', 15: 'black'
    }

    def __init__(self, entity_id: str, data: entities.Bed) -> None:
        super().__init__(entity_id)
        self._raw_data = data

    @property
    def color(self) -> str:
        """
        Color of the bed.

        Returns
        -------
        str
            Human-readable color name of the bed.
        """
        return self.COLOR_NAMES.get(self._raw_data['color'], 'unknown')

    def __repr__(self) -> str:
        return f"<Bed id={self.id} color={self.color}>"


class FlowerPot(BaseEntity[str]):
    """Represents a flower pot block entity."""
    __slots__ = ('_raw_data',)

    EMPTY_ITEM: ClassVar[str] = 'minecraft:air'

    def __init__(self, entity_id: str, data: entities.FlowerPot) -> None:
        super().__init__(entity_id)
        self._raw_data = data

    @property
    def item(self) -> str:
        """
        Item contained in the flower pot.

        Returns
        -------
        str
            Minecraft item identifier of the contained plant or flower.
        """
        return self._raw_data['Item']

    @property
    def item_data(self) -> int:
        """
        Metadata/damage value for the item.

        Returns
        -------
        int
            Numerical data value associated with the contained item.
        """
        return self._raw_data['Data']

    @property
    def is_empty(self) -> bool:
        """
        Check if flower pot is empty.

        Returns
        -------
        bool
            True if pot contains only air (empty), False if it contains an item.
        """
        return self.item == self.EMPTY_ITEM

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} item={self.item}, data={self.item_data}>"