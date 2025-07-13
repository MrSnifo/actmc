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

from .protocol import ProtocolBuffer, read_varint
from .math import Vector3D, Vector2D
from typing import TYPE_CHECKING
import struct
import array

if TYPE_CHECKING:
    from typing import List, Dict, Union, Optional, Tuple, ClassVar
    from .entities.entity import BaseEntity

__all__ = ('Block', 'ChunkSection', 'Chunk', 'IndirectPalette', 'DirectPalette')


class Block:
    """
    Represents a block state in the Minecraft world.

    A Block encapsulates the fundamental properties of a single block position,
    including its type, metadata, world position, and any associated block entity.

    Attributes
    ----------
    id: int
        Block type identifier
    metadata: int
        Block metadata value
    entity: Optional[BaseEntity]
        Associated block entity (e.g., chest, furnace)
    position: Optional[Vector3D[int]]
        World position coordinates
    """
    __slots__ = ('id', 'metadata', 'position', 'entity')

    # Block ID constants
    AIR_ID: ClassVar[int] = 0
    MAX_BLOCK_ID: ClassVar[int] = 255
    MAX_METADATA: ClassVar[int] = 15

    def __init__(self, block_id: int, metadata: int = 0, position: Optional[Vector3D[int]] = None) -> None:
        self.id: int = block_id
        self.metadata: int = metadata
        self.entity: Optional[BaseEntity] = None
        self.position: Optional[Vector3D[int]] = position

    def is_valid(self) -> bool:
        """Check if block state has valid ID and metadata values.

        Returns
        -------
        bool
            True if block ID is in [0, 255] and metadata is in [0, 15]
        """
        return 0 <= self.id <= self.MAX_BLOCK_ID and 0 <= self.metadata <= self.MAX_METADATA

    def is_solid(self) -> bool:
        """Check if block is solid for collision and pathfinding purposes.

        Returns
        -------
        bool
            True if block is not air (ID != 0), False for air blocks

        Notes
        -----
        This method considers any non-air block as solid. For more complex
        collision detection, additional logic may be needed based on block type.
        """
        return self.id != self.AIR_ID

    def __eq__(self, other) -> bool:
        """Check equality based on block ID and metadata.

        Parameters
        ----------
        other: object
            To compare with

        Returns
        -------
        bool
            True if both objects are Block instances with same ID and metadata
        """
        return isinstance(other, Block) and self.id == other.id and self.metadata == other.metadata

    def __hash__(self) -> int:
        """Generate hash based on block ID and metadata.

        Returns
        -------
        int
            Hash value for use in sets and dictionaries
        """
        return hash((self.id, self.metadata))

    def __repr__(self) -> str:
        """Return string representation of the block.

        Returns
        -------
        str
            Formatted string showing block properties
        """
        return "<Block id={} metadata={} position={}{}>".format(
            self.id,
            self.metadata,
            self.position,
            f" entity={self.entity}" if self.entity else ""
        )


class IndirectPalette:
    """
    Indirect palette mapping local indices to global palette IDs.

    Used for chunk sections with limited unique block types to compress
    storage by mapping small local IDs to full block state IDs.

    Attributes
    ----------
    bits_per_block: int
        Actual bits per block used (>= 4)
    id_to_state: Dict[int, int]
        Maps palette ID to packed block state
    state_to_id: Dict[int, int]
        Maps packed block state to palette ID

    Notes
    -----
    Block states are packed as: (block_id << 4) | metadata
    This allows efficient storage of both block type and metadata in a single integer.
    """
    __slots__ = ('bits_per_block', 'id_to_state', 'state_to_id')

    # Palette constants
    MIN_BITS_PER_BLOCK: ClassVar[int] = 4
    METADATA_MASK: ClassVar[int] = 0x0F
    METADATA_SHIFT: ClassVar[int] = 4

    def __init__(self, bits_per_block: int) -> None:
        self.bits_per_block: int = max(self.MIN_BITS_PER_BLOCK, bits_per_block)
        self.id_to_state: Dict[int, int] = {}
        self.state_to_id: Dict[int, int] = {}

    def add_state(self, state: Block) -> int:
        """Add block state to palette and return its local ID.

        Parameters
        ----------
        state: Block
            State to add to the palette

        Returns
        -------
        int
            Local palette ID for the state (0-based index)

        Notes
        -----
        If the state already exists in the palette, returns the existing ID.
        Otherwise, assigns a new sequential ID starting from 0.
        """
        packed_id = self._pack_state(state)
        if packed_id in self.state_to_id:
            return self.state_to_id[packed_id]

        palette_id = len(self.id_to_state)
        self.id_to_state[palette_id] = packed_id
        self.state_to_id[packed_id] = palette_id
        return palette_id

    def state_for_id(self, palette_id: int) -> Block:
        """Get block state for a given palette ID.

        Parameters
        ----------
        palette_id: int
            Local palette identifier

        Returns
        -------
        Block
            state corresponding to the ID, or air block if ID not found

        Notes
        -----
        Returns Block(0, 0) for invalid or missing palette IDs.
        """
        packed_id = self.id_to_state.get(palette_id, 0)
        return self._unpack_state(packed_id)

    def read(self, buffer: ProtocolBuffer) -> None:
        """Read palette data from network buffer.

        Parameters
        ----------
        buffer: ProtocolBuffer
            Buffer containing serialized palette data

        Notes
        -----
        Clears existing palette data before reading new data.
        Expected format: varint length followed by varint state IDs.
        """
        self.id_to_state.clear()
        self.state_to_id.clear()

        palette_length = read_varint(buffer)
        for palette_id in range(palette_length):
            state_id = read_varint(buffer)
            packed_id = self._pack_global_state(state_id)
            self.id_to_state[palette_id] = packed_id
            self.state_to_id[packed_id] = palette_id

    @staticmethod
    def _pack_state(state: Block) -> int:
        """Pack block state into single integer.

        Parameters
        ----------
        state: Block
            State to pack

        Returns
        -------
        int
            Packed state as (block_id << 4) | metadata
        """
        return (state.id << IndirectPalette.METADATA_SHIFT) | (state.metadata & IndirectPalette.METADATA_MASK)

    @staticmethod
    def _pack_global_state(state_id: int) -> int:
        """Pack global palette ID into internal format.

        Parameters
        ----------
        state_id: int
            Global palette state ID

        Returns
        -------
        int
            Packed state, or 0 if invalid ID
        """
        block_id = state_id >> IndirectPalette.METADATA_SHIFT
        metadata = state_id & IndirectPalette.METADATA_MASK
        return ((block_id << IndirectPalette.METADATA_SHIFT) | metadata
                if 0 <= block_id <= Block.MAX_BLOCK_ID and 0 <= metadata <= Block.MAX_METADATA else 0)

    @staticmethod
    def _unpack_state(packed_id: int) -> Block:
        """Unpack integer to block state.

        Parameters
        ----------
        packed_id: int
            Packed state ID

        Returns
        -------
        Block
            Unpacked block state
        """
        return Block(packed_id >> IndirectPalette.METADATA_SHIFT, packed_id & IndirectPalette.METADATA_MASK)


class DirectPalette:
    """
    Direct palette using global palette IDs without local mapping.

    Used for chunk sections with many unique block types where the overhead
    of maintaining a local palette exceeds the storage benefits.

    Attributes
    ----------
    bits_per_block: int
        Fixed at 13 bits for direct palette usage

    Notes
    -----
    Direct palettes store global block state IDs directly in the block data
    array, eliminating the need for a local ID mapping.
    """
    __slots__ = ('bits_per_block',)

    # Direct palette constants
    BITS_PER_BLOCK: ClassVar[int] = 13
    METADATA_MASK: ClassVar[int] = 0x0F
    METADATA_SHIFT: ClassVar[int] = 4

    def __init__(self) -> None:
        self.bits_per_block: int = self.BITS_PER_BLOCK

    @staticmethod
    def state_for_id(palette_id: int) -> Block:
        """Get block state for global palette ID.

        Parameters
        ----------
        palette_id: int
            Global palette identifier

        Returns
        -------
        Block
            state corresponding to the ID, or air block for invalid IDs

        Notes
        -----
        Validates that the unpacked block ID and metadata are within valid ranges.
        Returns Block(0, 0) for invalid palette IDs.
        """
        block_id = palette_id >> DirectPalette.METADATA_SHIFT
        metadata = palette_id & DirectPalette.METADATA_MASK
        return (Block(block_id, metadata)
                if 0 <= block_id <= Block.MAX_BLOCK_ID and 0 <= metadata <= Block.MAX_METADATA
                else Block(Block.AIR_ID, 0))

    @staticmethod
    def read(buffer: ProtocolBuffer) -> None:
        """Read dummy palette data from buffer.

        Parameters
        ----------
        buffer: ProtocolBuffer
            Buffer containing palette data

        Raises
        ------
        AssertionError
            If dummy palette length is not 0

        Notes
        -----
        Direct palettes don't store local mapping data, so this method
        only verifies the expected dummy length of 0.
        """
        dummy_length = read_varint(buffer)
        assert dummy_length == 0, f"Expected dummy palette length of 0, got {dummy_length}"


class ChunkSection:
    """
    16x16x16 chunk section optimized for pathfinding and world storage.

    Represents a cubic section of the world containing blocks and block entities.
    Provides efficient storage and access patterns for block data.

    Attributes
    ----------
    chunk_pos: Vector2D[int]
        Parent chunk position
    section_y: int
        Vertical section index
    block_data: array.array
        Packed block data array (block_id << 4 | metadata)
    palette: Optional[Union[IndirectPalette, DirectPalette]]
        Palette used for block state mapping
    block_entities: Dict[int, BaseEntity]
        Maps block indices to their associated entities

    Notes
    -----
    Block data is stored as packed integers where each value contains
    both block ID and metadata: (block_id << 4) | metadata
    """
    __slots__ = ('chunk_pos', 'section_y', 'block_data', 'palette', 'block_entities')

    # Section dimensions
    SECTION_WIDTH: ClassVar[int] = 16
    SECTION_HEIGHT: ClassVar[int] = 16
    BLOCKS_PER_SECTION: ClassVar[int] = SECTION_WIDTH ** 3

    # Bit manipulation constants
    METADATA_MASK: ClassVar[int] = 0x0F
    METADATA_SHIFT: ClassVar[int] = 4
    PALETTE_THRESHOLD: ClassVar[int] = 8

    def __init__(self, chunk_pos: Vector2D[int], section_y: int = 0) -> None:
        self.chunk_pos: Vector2D[int] = chunk_pos
        self.section_y: int = section_y
        self.block_data: array.array = array.array('H', [0] * self.BLOCKS_PER_SECTION)
        self.palette: Optional[Union[IndirectPalette, DirectPalette]] = None
        self.block_entities: Dict[int, BaseEntity] = {}

    @staticmethod
    def _get_index(x: int, y: int, z: int) -> int:
        """Convert 3D coordinates to linear array index.

        Parameters
        ----------
        x, y, z: int
            Local coordinates within the section [0, 15]

        Returns
        -------
        int
            Linear array index

        Notes
        -----
        Uses bit shifting for efficient calculation: (y << 8) | (z << 4) | x
        """
        return (y << 8) | (z << 4) | x

    def get_block_id(self, pos: Vector3D[int]) -> int:
        """Get block ID at the specified position.

        Parameters
        ----------
        pos: Vector3D[int]
            Local coordinates within section [0, 15]

        Returns
        -------
        int
            Block ID at the position

        Notes
        -----
        Extracts only the block ID from packed data, ignoring metadata.
        """
        return self.block_data[self._get_index(pos.x, pos.y, pos.z)] >> self.METADATA_SHIFT

    def get_block(self, pos: Vector3D[int]) -> Tuple[int, int]:
        """Get block ID and metadata at the specified position.

        Parameters
        ----------
        pos: Vector3D[int]
            Local coordinates within section [0, 15]

        Returns
        -------
        Tuple[int, int]
            Block ID and metadata (block_id, metadata)
        """
        idx = self._get_index(pos.x, pos.y, pos.z)
        packed_data = self.block_data[idx]
        return packed_data >> self.METADATA_SHIFT, packed_data & self.METADATA_MASK

    def get_block_entity(self, pos: Vector3D[int]) -> Optional[BaseEntity]:
        """Get block entity at the specified position.

        Parameters
        ----------
        pos: Vector3D[int]
            Local coordinates within section [0, 15]

        Returns
        -------
        Optional[BaseEntity]
            Block entity at position, or None if no entity exists
        """
        idx = self._get_index(pos.x, pos.y, pos.z)
        return self.block_entities.get(idx, None)

    def set_block(self, pos: Vector3D[int], block_id: int, metadata: int = 0) -> None:
        """Set block state at the specified position.

        Parameters
        ----------
        pos: Vector3D[int]
            Local coordinates within section [0, 15]
        block_id: int
            Block type identifier [0, 255]
        metadata: int, default=0
            Block metadata [0, 15]

        Notes
        -----
        Automatically removes any existing block entity at the position.
        """
        idx = self._get_index(pos.x, pos.y, pos.z)
        self.block_data[idx] = (block_id << self.METADATA_SHIFT) | (metadata & self.METADATA_MASK)
        self.block_entities.pop(idx, None)

    def set_entity(self, pos: Vector3D[int], block_entity: BaseEntity) -> None:
        """Set block entity at the specified position.

        Parameters
        ----------
        pos: Vector3D[int]
            Local coordinates within section [0, 15]
        block_entity: BaseEntity
            Block entity to place at the position
        """
        self.block_entities[self._get_index(pos.x, pos.y, pos.z)] = block_entity

    def is_empty(self) -> bool:
        """Check if section contains only air blocks.

        Returns
        -------
        bool
            True if all blocks are air (ID = 0), False otherwise

        Notes
        -----
        Useful for optimization - empty sections can be skipped during
        rendering and collision detection.
        """
        return all(data == 0 for data in self.block_data)

    @staticmethod
    def choose_palette(bits_per_block: int) -> Union[IndirectPalette, DirectPalette]:
        """Choose appropriate palette type based on bits per block.

        Parameters
        ----------
        bits_per_block: int
            Number of bits required per block

        Returns
        -------
        Union[IndirectPalette, DirectPalette]
            IndirectPalette for <= 8 bits, DirectPalette otherwise

        Notes
        -----
        Indirect palettes are more efficient for sections with few unique
        block types, while direct palettes are better for diverse sections.
        """
        return (IndirectPalette(max(IndirectPalette.MIN_BITS_PER_BLOCK, bits_per_block))
                if bits_per_block <= ChunkSection.PALETTE_THRESHOLD
                else DirectPalette())


class Chunk:
    """
    Complete chunk in the world, optimized for pathfinding and storage.

    A chunk represents a 16x16x256 column of blocks divided into 16x16x16 sections.
    Provides efficient access to block data and manages chunk loading/unloading.

    Attributes
    ----------
    position: Vector2D[int]
        Chunk position in world coordinates
    sections: List[Optional[ChunkSection]]
        Array of chunk sections, None for empty sections
    biomes: array.array
        Biome data for the chunk surface (16x16 array)

    Notes
    -----
    Chunks are loaded from network data and automatically parsed into
    sections. Empty sections are represented as None to save memory.
    """
    __slots__ = ('position', 'sections', 'biomes')

    # Chunk dimensions
    CHUNK_WIDTH: ClassVar[int] = 16
    CHUNK_HEIGHT: ClassVar[int] = 256
    SECTION_HEIGHT: ClassVar[int] = 16
    SECTIONS_PER_CHUNK: ClassVar[int] = CHUNK_HEIGHT // SECTION_HEIGHT

    # Default biome ID
    DEFAULT_BIOME: ClassVar[int] = 1

    def __init__(self, chunk_pos: Vector2D[int], full: bool, mask: int, data: bytes) -> None:
        self.position: Vector2D[int] = chunk_pos
        self.sections: List[Optional[ChunkSection]] = [None] * self.SECTIONS_PER_CHUNK
        self.biomes: array.array = array.array('B', [self.DEFAULT_BIOME] * (self.CHUNK_WIDTH ** 2))
        self._load_chunk_column(full, mask, data)

    def get_section(self, section_y: int) -> Optional[ChunkSection]:
        """Get chunk section at the specified Y level.

        Parameters
        ----------
        section_y: int
            Section Y coordinate [0, 15]

        Returns
        -------
        Optional[ChunkSection]
            Chunk section at the Y level, or None if invalid Y or empty section
        """
        return self.sections[section_y] if 0 <= section_y < self.SECTIONS_PER_CHUNK else None

    def set_block_state(self, position: Vector3D[int], section_y: int, block_id: int, metadata: int = 0) -> None:
        """Set block state at the specified position.

        Parameters
        ----------
        position: Vector3D[int]
            Local position within section [0, 15]
        section_y: int
            Section Y coordinate [0, 15]
        block_id: int
            Block type identifier [0, 255]
        metadata: int, default=0
            Block metadata [0, 15]
        """
        section = self.get_section(section_y)
        if section is None:
            section = ChunkSection(self.position, section_y)
            self.set_section(section_y, section)
        section.set_block(position, block_id, metadata)

    def set_block_entity(self, position: Vector3D[int], section_y: int, block_entity: BaseEntity) -> None:
        """Set block entity at the specified position.

        Parameters
        ----------
        position: Vector3D[int]
            Local position within section [0, 15]
        section_y: int
            Section Y coordinate [0, 15]
        block_entity: BaseEntity
            Block entity to place

        Notes
        -----
        Automatically creates a new section if one doesn't exist at the Y level.
        """
        section = self.get_section(section_y)
        if section is None:
            section = ChunkSection(self.position, section_y)
            self.set_section(section_y, section)
        section.set_entity(position, block_entity)

    def set_section(self, section_y: int, section: ChunkSection) -> None:
        """Set chunk section at the specified Y level.

        Parameters
        ----------
        section_y: int
            Section Y coordinate [0, 15]
        section: ChunkSection
            Chunk section to set

        Notes
        -----
        Ignores requests to set sections at invalid Y coordinates.
        """
        if 0 <= section_y < self.SECTIONS_PER_CHUNK:
            self.sections[section_y] = section

    def _load_chunk_column(self, full: bool, mask: int, data: bytes) -> None:
        """Load chunk column from network format.

        Parameters
        ----------
        full: bool
            Whether this is a full chunk containing biome data
        mask: int
            Bitmask indicating which sections are present
        data: bytes
            Raw chunk data in network format

        Notes
        -----
        Parses network data format and populates chunk sections.
        Only processes sections indicated by the mask bits.
        """
        buffer = ProtocolBuffer(data)
        for section_y in range(self.SECTIONS_PER_CHUNK):
            if mask & (1 << section_y):
                section = ChunkSection(self.position, section_y)
                self._read_chunk_section(section, buffer)
                self.set_section(section_y, section)

        if full:
            biome_data = buffer.read(self.CHUNK_WIDTH ** 2)
            self.biomes = array.array('B', biome_data)

    @staticmethod
    def _read_chunk_section(section: ChunkSection, buffer: ProtocolBuffer) -> None:
        """Read chunk section data from network buffer.

        Parameters
        ----------
        section: ChunkSection
            Section to populate with data
        buffer: ProtocolBuffer
            Buffer containing section data in network format

        Notes
        -----
        Parses palette, block data array, and light data from the buffer.
        Converts network format to internal packed block representation.
        """
        bits_per_block = struct.unpack('B', buffer.read(1))[0]
        palette = section.choose_palette(bits_per_block)
        palette.read(buffer)

        # Read data array
        data_array_length = read_varint(buffer)
        data_array = struct.unpack(f'>{data_array_length}Q', buffer.read(8 * data_array_length))
        individual_value_mask = (1 << bits_per_block) - 1

        # Decode blocks to packed format
        for i in range(section.BLOCKS_PER_SECTION):
            bit_index = i * bits_per_block
            start_long, start_offset = bit_index >> 6, bit_index & 63

            if start_offset + bits_per_block <= 64:
                data = (data_array[start_long] >> start_offset) & individual_value_mask
            else:
                end_offset = 64 - start_offset
                data = ((data_array[start_long] >> start_offset) |
                        (data_array[start_long + 1] << end_offset)) & individual_value_mask

            state = palette.state_for_id(data)
            section.block_data[i] = (state.id << 4) | (state.metadata & 0x0F)

        # Skip light data
        light_bytes = section.BLOCKS_PER_SECTION // 2
        buffer.read(light_bytes * 2)  # Block light + sky-light

        section.palette = palette