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
from .entities import entity
import struct
import array
import math

if TYPE_CHECKING:
    from typing import List, Dict, Union, ClassVar, Any, Optional


__all__ = ('Block', 'ChunkSection', 'Chunk', 'IndirectPalette', 'DirectPalette')


class Block:
    """
    Represents the state of a block in the world, including its type, metadata, position, and associated entity.

    Parameters
    ----------
    block_id: int
        The block ID. Note: A value of -1 indicates this block state exists only
        to hold Block Entity data (no physical block present).
    metadata: int, optional
        The block metadata, by default 0.
    position: Vector3D[int], optional
        The world position of the block, by default None.

    Attributes
    ----------
    id: int
        The block ID.
    metadata: int
        The block metadata.
    position: Vector3D[int] or None
        The world position of the block.
    entity: Optional[BlockEntity]
        Associated block entity if present.
    """

    __slots__ = ('id', 'metadata', 'position', 'entity')

    def __init__(self, block_id: int, metadata: int = 0, position: Vector3D[int] = None) -> None:
        self.id = block_id
        self.metadata = metadata
        self.entity: Optional[entity.BaseEntity] = None
        self.position = position

    def is_valid(self) -> bool:
        """
        Check if this block state is valid.

        Returns
        -------
        bool
            True if both block_id and metadata are within valid ranges.
        """
        return 0 <= self.id <= 255 and 0 <= self.metadata <= 15

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Block):
            return False
        return (self.id == other.id and
                self.metadata == other.metadata and
                self.position == other.position)

    def __hash__(self) -> int:
        return hash((self.id, self.metadata, self.position))

    def __repr__(self) -> str:
        attrs = [
            f"id={self.id}",
            *(f"metadata={self.metadata!r}" for _ in [self.metadata] if self.metadata),
            f"position={self.position!r}",
            *(f"entity={self.entity!r}" for _ in [self.entity] if self.entity),
        ]
        return f"<BlockState {' '.join(attrs)}>"


class IndirectPalette:
    """
    Indirect palette that maps local indices to global palette IDs.

    Parameters
    ----------
    bits_per_block: int
        Number of bits used to represent each block (minimum 4).

    Attributes
    ----------
    bits_per_block: int
        Number of bits used to represent each block (minimum 4).
    id_to_state: Dict[int, Block]
        Mapping from palette IDs to block states.
    state_to_id: Dict[Block, int]
        Mapping from block states to palette IDs.
    """

    __slots__ = ('bits_per_block', 'id_to_state', 'state_to_id')

    def __init__(self, bits_per_block: int) -> None:
        # Minimum 4 bits
        self.bits_per_block: int = max(4, bits_per_block)
        self.id_to_state: Dict[int, Block] = {}
        self.state_to_id: Dict[Block, int] = {}

    def add_state(self, state: Block) -> int:
        """
        Add a state to the palette and return its ID.

        Parameters
        ----------
        state: Block
            The block state to add.

        Returns
        -------
        int
            The palette ID assigned to this state.
        """
        if state in self.state_to_id:
            return self.state_to_id[state]

        palette_id = len(self.id_to_state)
        self.id_to_state[palette_id] = state
        self.state_to_id[state] = palette_id
        return palette_id

    def id_for_state(self, state: Block) -> int:
        """
        Get the palette ID for a given block state.

        Parameters
        ----------
        state: Block
            The block state to look up.

        Returns
        -------
        int
            The palette ID for the state (adds if not present).
        """
        if state not in self.state_to_id:
            return self.add_state(state)
        return self.state_to_id[state]

    def state_for_id(self, palette_id: int) -> Block:
        """
        Get the block state for a given palette ID.

        Parameters
        ----------
        palette_id: int
            The palette ID to look up.

        Returns
        -------
        Block
            The corresponding block state (air if invalid).
        """
        return self.id_to_state.get(palette_id, Block(0, 0))  # Default to air

    def get_bits_per_block(self) -> int:
        """
        Get the number of bits used per block.

        Returns
        -------
        int
            The bits per block value.
        """
        return self.bits_per_block

    def read(self, buffer: ProtocolBuffer) -> None:
        """
        Read palette data from a buffer.

        Parameters
        ----------
        buffer: ProtocolBuffer
            The buffer to read from.
        """
        self.id_to_state.clear()
        self.state_to_id.clear()

        palette_length = read_varint(buffer)
        for palette_id in range(palette_length):
            state_id = read_varint(buffer)
            state = self._get_state_from_global_palette_id(state_id)
            self.id_to_state[palette_id] = state
            self.state_to_id[state] = palette_id

    @staticmethod
    def _get_state_from_global_palette_id(palette_id: int) -> Block:
        """Convert global palette ID to block state."""
        block_id = palette_id >> 4
        metadata = palette_id & 0x0F
        state = Block(block_id, metadata)
        return state if state.is_valid() else Block(0, 0)

    def __repr__(self) -> str:
        return f"<IndirectPalette bits={self.bits_per_block}, size={len(self.id_to_state)}>"


class DirectPalette:
    """
    Direct palette that uses global palette IDs directly.

    Attributes
    ----------
    bits_per_block: int
        Number of bits used to represent each block (fixed at 13 for vanilla).
    """

    __slots__ = ('bits_per_block',)

    def __init__(self) -> None:
        # Current vanilla value
        self.bits_per_block: int = 13

    def id_for_state(self, state: Block) -> int:
        """
        Get the global palette ID for a given block state.

        Parameters
        ----------
        state: Block
            The block state to convert.

        Returns
        -------
        int
            The global palette ID.
        """
        return self._get_global_palette_id_from_state(state)

    def state_for_id(self, palette_id: int) -> Block:
        """
        Get the block state for a given global palette ID.

        Parameters
        ----------
        palette_id: int
            The global palette ID to convert.

        Returns
        -------
        Block
            The corresponding block state.
        """
        return self._get_state_from_global_palette_id(palette_id)

    def get_bits_per_block(self) -> int:
        """
        Get the number of bits used per block.

        Returns
        -------
        int
            The bits per block value (always 13).
        """
        return self.bits_per_block

    @staticmethod
    def read(buffer: ProtocolBuffer) -> None:
        """
        Read dummy palette data from a buffer.

        Parameters
        ----------
        buffer: ProtocolBuffer
            The buffer to read from.

        Raises
        ------
        AssertionError
            If dummy length is not 0.
        """
        # Read dummy palette length (should be 0)
        dummy_length = read_varint(buffer)
        assert dummy_length == 0, f"Expected dummy palette length of 0, got {dummy_length}"

    @staticmethod
    def _get_global_palette_id_from_state(state: Block) -> int:
        """Convert block state to global palette ID."""
        if state.is_valid():
            return (state.id << 4) | state.metadata
        return 0

    @staticmethod
    def _get_state_from_global_palette_id(palette_id: int) -> Block:
        """Convert global palette ID to block state."""
        block_id = palette_id >> 4
        metadata = palette_id & 0x0F
        state = Block(block_id, metadata)
        return state if state.is_valid() else Block(0, 0)

    def __repr__(self) -> str:
        return f"<DirectPalette bits={self.bits_per_block}>"


class ChunkSection:
    """
    Represents a 16x16x16 chunk section with flat array storage for maximum performance.

    Parameters
    ----------
    chunk_pos: Vector2D[int]
        The chunk position in the world.
    section_y: int, optional
        The Y level of this section within the chunk, by default 0.

    Attributes
    ----------
    chunk_pos: Vector2D[int]
        The chunk position in the world.
    section_y: int
        The Y level of this section within the chunk.
    block_ids: array.array
        Flat array of block IDs.
    block_metadata: array.array
        Flat array of block metadata.
    block_light: array.array
        Flat array of block light levels.
    sky_light: array.array
        Flat array of sky-light levels.
    palette: Optional[Union[IndirectPalette, DirectPalette]]
        The palette used for this section.
    """

    __slots__ = ('chunk_pos', 'section_y', 'block_ids', 'block_metadata', 'block_light', 'sky_light', 'palette',
                 'block_entities')

    SECTION_WIDTH: ClassVar[int] = 16
    SECTION_HEIGHT: ClassVar[int] = 16
    BLOCKS_PER_SECTION: ClassVar[int] = SECTION_WIDTH * SECTION_HEIGHT * SECTION_WIDTH

    def __init__(self, chunk_pos: Vector2D[int], section_y: int = 0) -> None:
        self.chunk_pos: Vector2D[int] = chunk_pos
        self.section_y = section_y

        # Use flat arrays for maximum performance - much faster than nested lists
        self.block_ids = array.array('H', [0] * self.BLOCKS_PER_SECTION)  # unsigned short
        self.block_metadata = array.array('B', [0] * self.BLOCKS_PER_SECTION)  # unsigned byte
        self.block_light = array.array('B', [0] * self.BLOCKS_PER_SECTION)
        self.sky_light = array.array('B', [0] * self.BLOCKS_PER_SECTION)

        self.palette: Optional[Union[IndirectPalette, DirectPalette]] = None
        self.block_entities: Dict[int, entity.BaseEntity] = {}

    @staticmethod
    def _get_index(x: int, y: int, z: int) -> int:
        """Convert 3D coordinates to flat array index."""
        return (y << 8) | (z << 4) | x  # y*256 + z*16 + x

    def get_state(self, pos: Vector3D[int]) -> Block:
        """
        Get block state at coordinates.

        Parameters
        ----------
        pos: Vector3D[int]
            The position coordinates within the section.

        Returns
        -------
        Block
            The block state at the given coordinates.
        """
        idx = self._get_index(pos.x, pos.y, pos.z)
        world_x = self.chunk_pos.x * self.SECTION_WIDTH + pos.x
        world_y = self.section_y * self.SECTION_HEIGHT + pos.y
        world_z = self.chunk_pos.y * self.SECTION_WIDTH + pos.z

        state = Block(self.block_ids[idx], self.block_metadata[idx], Vector3D(world_x, world_y, world_z))

        # Check for block entity
        if idx in self.block_entities:
            state.entity = self.block_entities[idx]

        return state

    def set_state(self, pos: Vector3D[int], state: Block) -> None:
        """
        Set block state at coordinates.

        Parameters
        ----------
        pos: Vector3D[int]
            The position coordinates within the section.
        state: Block
            The block state to set.
        """
        idx = self._get_index(pos.x, pos.y, pos.z)
        self.block_ids[idx] = state.id
        self.block_metadata[idx] = state.metadata

        if idx in self.block_entities:
            del self.block_entities[idx]

    def set_entity(self, pos: Vector3D[int], block_entity: entity.BaseEntity) -> None:
        idx = self._get_index(pos.x, pos.y, pos.z)
        self.block_entities[idx] = block_entity

    def get_block_light(self, x: int, y: int, z: int) -> int:
        """
        Get block light level at coordinates.

        Parameters
        ----------
        x: int
            The X coordinate.
        y: int
            The Y coordinate.
        z: int
            The Z coordinate.

        Returns
        -------
        int
            The block light level.
        """
        return self.block_light[self._get_index(x, y, z)]

    def set_block_light(self, pos: Vector3D[int], light: int) -> None:
        """
        Set block light level at coordinates.

        Parameters
        ----------
        pos: Vector3D[int]
            The position coordinates.
        light: int
            The light level to set.
        """
        self.block_light[self._get_index(pos.x, pos.y, pos.z)] = light & 0xF

    def get_sky_light(self, pos: Vector3D[int]) -> int:
        """
        Get sky-light level at coordinates.

        Parameters
        ----------
        pos: Vector3D[int]
            The position coordinates.

        Returns
        -------
        int
            The sky-light level.
        """
        return self.sky_light[self._get_index(pos.x, pos.y, pos.z)]

    def set_sky_light(self, pos: Vector3D[int], light: int) -> None:
        """
        Set sky-light level at coordinates.

        Parameters
        ----------
        pos: Vector3D[int]
            The position coordinates.
        light: int
            The light level to set.
        """
        self.sky_light[self._get_index(pos.x, pos.y, pos.z)] = light & 0xF

    def is_empty(self) -> bool:
        """
        Check if this section contains only air blocks.

        Returns
        -------
        bool
            True if all blocks are air.
        """
        for i in range(self.BLOCKS_PER_SECTION):
            if self.block_ids[i] != 0 or self.block_metadata[i] != 0:
                return False
        return True

    @staticmethod
    def choose_palette(bits_per_block: int) -> Union[IndirectPalette, DirectPalette]:
        """
        Choose appropriate palette based on bits per block.

        Parameters
        ----------
        bits_per_block: int
            The number of bits per block.

        Returns
        -------
        Union[IndirectPalette, DirectPalette]
            The appropriate palette type.
        """
        if bits_per_block <= 4:
            return IndirectPalette(4)
        elif bits_per_block <= 8:
            return IndirectPalette(bits_per_block)
        else:
            return DirectPalette()

    def build_palette(self) -> Union[IndirectPalette, DirectPalette]:
        """
        Build palette from current block data.

        Returns
        -------
        Union[IndirectPalette, DirectPalette]
            The constructed palette.
        """
        unique_states = set()
        chunk_x = self.chunk_pos.x * self.SECTION_WIDTH
        chunk_z = self.chunk_pos.y * self.SECTION_WIDTH
        world_y_base = self.section_y * self.SECTION_HEIGHT

        for i in range(self.BLOCKS_PER_SECTION):
            y = i >> 8  # i // 256
            z = (i >> 4) & 0xF  # (i // 16) % 16
            x = i & 0xF  # i % 16

            world_x = chunk_x + x
            world_y = world_y_base + y
            world_z = chunk_z + z

            state = Block(self.block_ids[i], self.block_metadata[i], Vector3D(world_x, world_y, world_z))
            unique_states.add(state)

        bits_needed = max(4, math.ceil(math.log2(len(unique_states)))) if len(unique_states) > 1 else 4
        palette = self.choose_palette(bits_needed)

        if isinstance(palette, IndirectPalette):
            for state in unique_states:
                palette.add_state(state)

        return palette

    def __repr__(self) -> str:
        return f"<ChunkSection palette={type(self.palette).__name__ if self.palette else None}>"


class Chunk:
    """
    Represents a chunk in the world, identified by its x and z coordinates, containing multiple sections and biome data.

    Parameters
    ----------
    chunk_pos: Vector2D[int]
        The chunk position in the world.

    Attributes
    ----------
    position: Vector2D[int]
        The chunk position in the world.
    sections: List[Optional[ChunkSection]]
        List of chunk sections.
    biomes: array.array
        Array of biome IDs for this chunk.
    """

    __slots__ = ('position', 'sections', 'biomes')

    CHUNK_WIDTH: ClassVar[int] = 16
    CHUNK_HEIGHT: ClassVar[int] = 256
    SECTION_HEIGHT: ClassVar[int] = 16
    SECTIONS_PER_CHUNK: ClassVar[int] = CHUNK_HEIGHT // SECTION_HEIGHT

    def __init__(self, chunk_pos: Vector2D[int]) -> None:
        self.position: Vector2D[int] = chunk_pos
        self.sections: List[Optional[ChunkSection]] = [None] * self.SECTIONS_PER_CHUNK
        self.biomes = array.array('B', [1] * (self.CHUNK_WIDTH * self.CHUNK_WIDTH))

    def get_section(self, section_y: int) -> Optional[ChunkSection]:
        """
        Get chunk section at given Y level.

        Parameters
        ----------
        section_y: int
            The Y level of the section.

        Returns
        -------
        Optional[ChunkSection]
            The chunk section or None if invalid.
        """
        if 0 <= section_y < self.SECTIONS_PER_CHUNK:
            return self.sections[section_y]
        return None

    def get_block_entities(self) -> List[Block]:
        """
        Get all block states that have block entities in this chunk.

        Returns
        -------
        List[Block]
            A list of block states with their associated block entities and world positions.
        """
        block_states_with_entities = []

        for section_y, section in enumerate(self.sections):
            if section is not None:
                for idx, entity in section.block_entities.items():
                    y = idx >> 8
                    z = (idx >> 4) & 0xF
                    x = idx & 0xF

                    local_pos = Vector3D(x, y, z)
                    block_state = section.get_state(local_pos)
                    block_states_with_entities.append(block_state)

        return block_states_with_entities

    def set_section(self, section_y: int, section: ChunkSection) -> None:
        """
        Set chunk section at given Y level.

        Parameters
        ----------
        section_y: int
            The Y level of the section.
        section: ChunkSection
            The section to set.
        """
        if 0 <= section_y < self.SECTIONS_PER_CHUNK:
            self.sections[section_y] = section

    def is_section_empty(self, section_y: int) -> bool:
        """
        Check if section is empty (air only or missing).

        Parameters
        ----------
        section_y: int
            The Y level of the section.

        Returns
        -------
        bool
            True if section is empty or missing.
        """
        section = self.get_section(section_y)
        return section is None or section.is_empty()

    def get_biome(self, x: int, z: int) -> int:
        """
        Get biome ID at coordinates.

        Parameters
        ----------
        x: int
            The X coordinate.
        z: int
            The Z coordinate.

        Returns
        -------
        int
            The biome ID.
        """
        return self.biomes[z * self.CHUNK_WIDTH + x]

    def set_biome(self, x: int, z: int, biome_id: int) -> None:
        """
        Set biome ID at coordinates.

        Parameters
        ----------
        x: int
            The X coordinate.
        z: int
            The Z coordinate.
        biome_id: int
            The biome ID to set.
        """
        self.biomes[z * self.CHUNK_WIDTH + x] = biome_id

    def load_chunk_column(self, full: bool, mask: int, data: bytes) -> None:
        """
        Load chunk column from network format.

        Parameters
        ----------
        full: bool
            True if biomes are included.
        mask: int
            Bitmask indicating which sections are present.
        data: bytes
            Serialized chunk data.
        """
        buffer = ProtocolBuffer(data)

        for section_y in range(self.SECTIONS_PER_CHUNK):
            if (mask & (1 << section_y)) != 0:
                section = ChunkSection(self.position, section_y)
                self._read_chunk_section(section, buffer)
                self.set_section(section_y, section)

        if full:
            # Direct array assignment
            biome_data = buffer.read(self.CHUNK_WIDTH * self.CHUNK_WIDTH)
            self.biomes = array.array('B', biome_data)

    def _read_chunk_section(self, section: ChunkSection, buffer: ProtocolBuffer) -> None:
        """Read chunk section data from buffer."""
        bits_per_block = struct.unpack('B', buffer.read(1))[0]
        palette = section.choose_palette(bits_per_block)
        palette.read(buffer)

        # Read all data array longs at once
        data_array_length = read_varint(buffer)
        data_array = struct.unpack(f'>{data_array_length}Q', buffer.read(8 * data_array_length))

        # Pre-calculate bit manipulation constants
        individual_value_mask = (1 << bits_per_block) - 1

        # Block decoding with direct array access
        for i in range(section.BLOCKS_PER_SECTION):
            bit_index = i * bits_per_block
            start_long = bit_index >> 6  # bit_index // 64
            start_offset = bit_index & 63  # bit_index % 64

            if start_offset + bits_per_block <= 64:
                # Single long read
                data = (data_array[start_long] >> start_offset) & individual_value_mask
            else:
                # Cross-long read
                end_offset = 64 - start_offset
                data = ((data_array[start_long] >> start_offset) |
                       (data_array[start_long + 1] << end_offset)) & individual_value_mask

            # Get state from palette
            state = palette.state_for_id(data)
            section.block_ids[i] = state.id
            section.block_metadata[i] = state.metadata

        # Light data reading with direct array operations
        self._read_light_data(buffer, section.block_light)
        self._read_light_data(buffer, section.sky_light)

        section.palette = palette

    @staticmethod
    def _read_light_data(buffer: ProtocolBuffer, light_array: array.array) -> None:
        """Read light data from buffer into array."""
        # Read all light data at once
        bytes_needed = len(light_array) // 2
        light_data = buffer.read(bytes_needed)

        # Unpack nibbles directly into array
        for i in range(0, len(light_array), 2):
            byte_val = light_data[i // 2]
            light_array[i] = byte_val & 0xF
            light_array[i + 1] = (byte_val >> 4) & 0xF

    def __repr__(self) -> str:
        return f"<Chunk position={self.position}>"