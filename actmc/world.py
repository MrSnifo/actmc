import struct
import math
from typing import List, Dict, Optional, Tuple

from .math import Vector3D
from .protocol import ProtocolBuffer, write_varint, read_varint
from .abc import Palette


class BlockState:
    """Represents a block state with ID and metadata."""

    def __init__(self, block_id: int, metadata: int = 0):
        self.block_id = block_id
        self.metadata = metadata

    def is_valid(self) -> bool:
        """Check if this block state is valid."""
        return 0 <= self.block_id <= 255 and 0 <= self.metadata <= 15

    def __eq__(self, other):
        if not isinstance(other, BlockState):
            return False
        return self.block_id == other.block_id and self.metadata == other.metadata

    def __hash__(self):
        return hash((self.block_id, self.metadata))

    def __repr__(self):
        return f"BlockState(id={self.block_id}, meta={self.metadata})"


class IndirectPalette(Palette):
    """Indirect palette that maps local indices to global palette IDs."""

    def __init__(self, bits_per_block: int):
        self.bits_per_block = max(4, bits_per_block)  # Minimum 4 bits
        self.id_to_state: Dict[int, BlockState] = {}
        self.state_to_id: Dict[BlockState, int] = {}

    def add_state(self, state: BlockState) -> int:
        """Add a state to the palette and return its ID."""
        if state in self.state_to_id:
            return self.state_to_id[state]

        palette_id = len(self.id_to_state)
        self.id_to_state[palette_id] = state
        self.state_to_id[state] = palette_id
        return palette_id

    def id_for_state(self, state: BlockState) -> int:
        if state not in self.state_to_id:
            return self.add_state(state)
        return self.state_to_id[state]

    def state_for_id(self, palette_id: int) -> BlockState:
        return self.id_to_state.get(palette_id, BlockState(0, 0))  # Default to air

    def get_bits_per_block(self) -> int:
        return self.bits_per_block

    def read(self, buffer: ProtocolBuffer) -> None:
        self.id_to_state.clear()
        self.state_to_id.clear()

        palette_length = read_varint(buffer)
        for palette_id in range(palette_length):
            state_id = read_varint(buffer)
            state = self._get_state_from_global_palette_id(state_id)
            self.id_to_state[palette_id] = state
            self.state_to_id[state] = palette_id

    def write(self, buffer: ProtocolBuffer) -> None:
        write_varint(len(self.id_to_state))
        for palette_id in range(len(self.id_to_state)):
            state = self.id_to_state[palette_id]
            state_id = self._get_global_palette_id_from_state(state)
            write_varint(state_id)

    @staticmethod
    def _get_global_palette_id_from_state(state: BlockState) -> int:
        """Convert block state to global palette ID."""
        if state.is_valid():
            return (state.block_id << 4) | state.metadata
        return 0

    @staticmethod
    def _get_state_from_global_palette_id(palette_id: int) -> BlockState:
        """Convert global palette ID to block state."""
        block_id = palette_id >> 4
        metadata = palette_id & 0x0F
        state = BlockState(block_id, metadata)
        return state if state.is_valid() else BlockState(0, 0)


class DirectPalette(Palette):
    """Direct palette that uses global palette IDs directly."""

    def __init__(self):
        self.bits_per_block = 13  # Current vanilla value

    def id_for_state(self, state: BlockState) -> int:
        return self._get_global_palette_id_from_state(state)

    def state_for_id(self, palette_id: int) -> BlockState:
        return self._get_state_from_global_palette_id(palette_id)

    def get_bits_per_block(self) -> int:
        return self.bits_per_block

    def read(self, buffer: ProtocolBuffer) -> None:
        # Read dummy palette length (should be 0)
        dummy_length = read_varint(buffer)
        assert dummy_length == 0, f"Expected dummy palette length of 0, got {dummy_length}"

    def write(self, buffer: ProtocolBuffer) -> None:
        # Ignore
        write_varint(0)

    @staticmethod
    def _get_global_palette_id_from_state(state: BlockState) -> int:
        """Convert block state to global palette ID."""
        if state.is_valid():
            return (state.block_id << 4) | state.metadata
        return 0

    @staticmethod
    def _get_state_from_global_palette_id(palette_id: int) -> BlockState:
        """Convert global palette ID to block state."""
        block_id = palette_id >> 4
        metadata = palette_id & 0x0F
        state = BlockState(block_id, metadata)
        return state if state.is_valid() else BlockState(0, 0)


class ChunkSection:
    """Represents a 16x16x16 chunk section."""

    SECTION_WIDTH = 16
    SECTION_HEIGHT = 16
    BLOCKS_PER_SECTION = SECTION_WIDTH * SECTION_HEIGHT * SECTION_WIDTH

    def __init__(self):
        self.blocks = [[[BlockState(0, 0) for _ in range(self.SECTION_WIDTH)]
                        for _ in range(self.SECTION_WIDTH)]
                       for _ in range(self.SECTION_HEIGHT)]
        self.block_light = [[[0 for _ in range(self.SECTION_WIDTH)]
                             for _ in range(self.SECTION_WIDTH)]
                            for _ in range(self.SECTION_HEIGHT)]
        self.sky_light = [[[0 for _ in range(self.SECTION_WIDTH)]
                           for _ in range(self.SECTION_WIDTH)]
                          for _ in range(self.SECTION_HEIGHT)]
        self.palette: Optional[Palette] = None

    def get_state(self, x: int, y: int, z: int) -> BlockState:
        """Get block state at coordinates."""
        return self.blocks[y][z][x]

    def set_state(self, x: int, y: int, z: int, state: BlockState) -> None:
        """Set block state at coordinates."""
        self.blocks[y][z][x] = state

    def get_block_light(self, x: int, y: int, z: int) -> int:
        """Get block light level at coordinates."""
        return self.block_light[y][z][x]

    def set_block_light(self, x: int, y: int, z: int, light: int) -> None:
        """Set block light level at coordinates."""
        self.block_light[y][z][x] = light & 0xF

    def get_sky_light(self, x: int, y: int, z: int) -> int:
        """Get sky-light level at coordinates."""
        return self.sky_light[y][z][x]

    def set_sky_light(self, x: int, y: int, z: int, light: int) -> None:
        """Set sky-light level at coordinates."""
        self.sky_light[y][z][x] = light & 0xF

    def is_empty(self) -> bool:
        """Check if this section contains only air blocks."""
        for y in range(self.SECTION_HEIGHT):
            for z in range(self.SECTION_WIDTH):
                for x in range(self.SECTION_WIDTH):
                    state = self.blocks[y][z][x]
                    if state.block_id != 0 or state.metadata != 0:
                        return False
        return True

    @staticmethod
    def choose_palette(bits_per_block: int) -> Palette:
        """Choose appropriate palette based on bits per block."""
        if bits_per_block <= 4:
            return IndirectPalette(4)
        elif bits_per_block <= 8:
            return IndirectPalette(bits_per_block)
        else:
            return DirectPalette()

    def build_palette(self) -> Palette:
        """Build palette from current block data."""
        unique_states = set()
        for y in range(self.SECTION_HEIGHT):
            for z in range(self.SECTION_WIDTH):
                for x in range(self.SECTION_WIDTH):
                    unique_states.add(self.blocks[y][z][x])

        bits_needed = max(4, math.ceil(math.log2(len(unique_states)))) if len(unique_states) > 1 else 4
        palette = self.choose_palette(bits_needed)

        if isinstance(palette, IndirectPalette):
            for state in unique_states:
                palette.add_state(state)

        return palette


class Chunk:
    """Represents a full chunk column (16x256x16)."""

    CHUNK_WIDTH = 16
    CHUNK_HEIGHT = 256
    SECTION_HEIGHT = 16
    SECTIONS_PER_CHUNK = CHUNK_HEIGHT // SECTION_HEIGHT

    def __init__(self, x: int, z: int):
        self.x: int = x
        self.z: int = z
        self.sections: List[Optional[ChunkSection]] = [None] * self.SECTIONS_PER_CHUNK
        self.biomes = [1] * (self.CHUNK_WIDTH * self.CHUNK_WIDTH)  # Default to plains
        self.block_entities = []

    def get_section(self, section_y: int) -> Optional[ChunkSection]:
        """Get chunk section at the given Y level."""
        if 0 <= section_y < self.SECTIONS_PER_CHUNK:
            return self.sections[section_y]
        return None

    def set_section(self, section_y: int, section: ChunkSection) -> None:
        """Set chunk section at the given Y level."""
        if 0 <= section_y < self.SECTIONS_PER_CHUNK:
            self.sections[section_y] = section

    def is_section_empty(self, section_y: int) -> bool:
        """Check if a section is empty."""
        section = self.get_section(section_y)
        return section is None or section.is_empty()

    def get_biome(self, x: int, z: int) -> int:
        """Get biome ID at coordinates."""
        return self.biomes[z * self.CHUNK_WIDTH + x]

    def set_biome(self, x: int, z: int, biome_id: int) -> None:
        """Set biome ID at coordinates."""
        self.biomes[z * self.CHUNK_WIDTH + x] = biome_id


class ChunkDataCodec:
    """Handles encoding and decoding of chunk data packets."""

    @staticmethod
    def read_chunk_data_packet(data: bytes) -> Chunk:
        """Read a chunk data packet and return a Chunk object."""
        buffer = ProtocolBuffer(data)

        # Read packet header
        chunk_x = struct.unpack('>i', buffer.read(4))[0]
        chunk_z = struct.unpack('>i', buffer.read(4))[0]
        ground_up_continuous = struct.unpack('?', buffer.read(1))[0]
        primary_bit_mask = read_varint(buffer)
        size = read_varint(buffer)

        # Read chunk data
        chunk_data = buffer.read(size)
        chunk = Chunk(chunk_x, chunk_z)
        ChunkDataCodec._read_chunk_column(chunk, ground_up_continuous, primary_bit_mask, chunk_data)

        # Read block entities
        block_entity_count = read_varint(buffer)
        for _ in range(block_entity_count):
            # Skip NBT data for now (would need NBT parser)
            pass

        return chunk

    @staticmethod
    def _read_chunk_column(chunk: Chunk, full: bool, mask: int, data: bytes) -> None:
        """Read chunk column data."""
        buffer = ProtocolBuffer(data)

        for section_y in range(chunk.SECTIONS_PER_CHUNK):
            if (mask & (1 << section_y)) != 0:
                section = ChunkSection()
                ChunkDataCodec._read_chunk_section(section, buffer)
                chunk.set_section(section_y, section)

        if full:
            for z in range(chunk.CHUNK_WIDTH):
                for x in range(chunk.CHUNK_WIDTH):
                    biome_id = struct.unpack('B', buffer.read(1))[0]
                    chunk.set_biome(x, z, biome_id)

    @staticmethod
    def _read_chunk_section(section: ChunkSection, buffer: ProtocolBuffer) -> None:
        """Read a single chunk section."""
        bits_per_block = struct.unpack('B', buffer.read(1))[0]
        palette = section.choose_palette(bits_per_block)
        palette.read(buffer)

        # Read compacted data array
        data_array_length = read_varint(buffer)
        data_array = []
        for _ in range(data_array_length):
            data_array.append(struct.unpack('>Q', buffer.read(8))[0])

        # Decode blocks
        individual_value_mask = (1 << bits_per_block) - 1

        for y in range(section.SECTION_HEIGHT):
            for z in range(section.SECTION_WIDTH):
                for x in range(section.SECTION_WIDTH):
                    block_number = ((y * section.SECTION_HEIGHT) + z) * section.SECTION_WIDTH + x
                    start_long = (block_number * bits_per_block) // 64
                    start_offset = (block_number * bits_per_block) % 64
                    end_long = ((block_number + 1) * bits_per_block - 1) // 64

                    if start_long == end_long:
                        data = (data_array[start_long] >> start_offset)
                    else:
                        end_offset = 64 - start_offset
                        data = ((data_array[start_long] >> start_offset) |
                                (data_array[end_long] << end_offset))

                    data &= individual_value_mask
                    state = palette.state_for_id(data)
                    section.set_state(x, y, z, state)

        # Read block light
        ChunkDataCodec._read_light_data(buffer, section, 'block')

        # Read sky light (if applicable)
        ChunkDataCodec._read_light_data(buffer, section, 'sky')

        section.palette = palette

    @staticmethod
    def _write_chunk_section(section: ChunkSection, buffer: ProtocolBuffer) -> None:
        """Write a single chunk section."""
        palette = section.build_palette()
        bits_per_block = palette.get_bits_per_block()

        buffer.write(struct.pack('B', bits_per_block))
        palette.write(buffer)

        # Write compacted data array
        data_length = (section.BLOCKS_PER_SECTION * bits_per_block) // 64
        data_array = [0] * data_length
        individual_value_mask = (1 << bits_per_block) - 1

        for y in range(section.SECTION_HEIGHT):
            for z in range(section.SECTION_WIDTH):
                for x in range(section.SECTION_WIDTH):
                    block_number = ((y * section.SECTION_HEIGHT) + z) * section.SECTION_WIDTH + x
                    start_long = (block_number * bits_per_block) // 64
                    start_offset = (block_number * bits_per_block) % 64
                    end_long = ((block_number + 1) * bits_per_block - 1) // 64

                    state = section.get_state(x, y, z)
                    value = palette.id_for_state(state) & individual_value_mask

                    data_array[start_long] |= (value << start_offset)

                    if start_long != end_long:
                        data_array[end_long] = (value >> (64 - start_offset))

        write_varint(data_length)
        for long_value in data_array:
            buffer.write(struct.pack('>Q', long_value))

        # Write light data
        ChunkDataCodec._write_light_data(buffer, section, 'block')
        ChunkDataCodec._write_light_data(buffer, section, 'sky')

    @staticmethod
    def _read_light_data(buffer: ProtocolBuffer, section: ChunkSection, light_type: str) -> None:
        for y in range(section.SECTION_HEIGHT):
            for z in range(section.SECTION_WIDTH):
                for x in range(0, section.SECTION_WIDTH, 2):
                    value = struct.unpack('B', buffer.read(1))[0]

                    if light_type == 'block':
                        section.set_block_light(x, y, z, value & 0xF)
                        section.set_block_light(x + 1, y, z, (value >> 4) & 0xF)
                    else:
                        section.set_sky_light(x, y, z, value & 0xF)
                        section.set_sky_light(x + 1, y, z, (value >> 4) & 0xF)

    @staticmethod
    def _write_light_data(buffer: ProtocolBuffer, section: ChunkSection, light_type: str) -> None:
        """Write light data (block or sky light)."""
        for y in range(section.SECTION_HEIGHT):
            for z in range(section.SECTION_WIDTH):
                for x in range(0, section.SECTION_WIDTH, 2):
                    if light_type == 'block':
                        value = (section.get_block_light(x, y, z) |
                                 (section.get_block_light(x + 1, y, z) << 4))
                    else:
                        value = (section.get_sky_light(x, y, z) |
                                 (section.get_sky_light(x + 1, y, z) << 4))

                    buffer.write(struct.pack('B', value))


class World:
    """Stores and manages chunks in a Minecraft world."""

    CHUNK_WIDTH = 16
    SECTION_HEIGHT = 16
    WORLD_HEIGHT = 256
    SECTIONS_PER_CHUNK = WORLD_HEIGHT // SECTION_HEIGHT

    def __init__(self):
        self.chunks: Dict[Tuple[int, int], Chunk] = {}
        self.chunks_data: Dict[Tuple[int, int], bytes] = {}

    def get_chunk_data(self, chunk_x: int, chunk_z: int) -> Optional[bytes]:
        """Get a chunk bytes if loaded, otherwise None."""
        return self.chunks_data.get((chunk_x, chunk_z))

    def get_chunk(self, chunk_x: int, chunk_z: int) -> Optional[Chunk]:
        """Get a chunk if loaded, otherwise None."""
        return self.chunks.get((chunk_x, chunk_z))

    def load_chunk(self, data: bytes) -> Chunk:
        """Load a chunk into the world."""
        chunk = ChunkDataCodec.read_chunk_data_packet(data)
        self.chunks_data[(chunk.x, chunk.z)] = data
        self.chunks[(chunk.x, chunk.z)] = chunk
        return self.chunks[(chunk.x, chunk.z)]

    def unload_chunk(self, chunk_x: int, chunk_z: int) -> None:
        """Unload a chunk from the world."""
        self.chunks.pop((chunk_x, chunk_z), None)
        self.chunks_data.pop((chunk_x, chunk_z), None)




    def _get_position_components(self, x: int, y: int, z: int) -> Optional[Tuple[Chunk, int, int, int, int]]:
        """Get chunk and relative coordinates for a world position."""
        chunk_x, rel_x = self._world_to_chunk_coord(x)
        chunk_z, rel_z = self._world_to_chunk_coord(z)

        if y < 0 or y >= self.WORLD_HEIGHT:
            return None

        chunk = self.get_chunk(chunk_x, chunk_z)
        if chunk is None:
            return None

        section_y, rel_y = self._block_to_section_coord(y)
        return chunk, section_y, rel_x, rel_y, rel_z

    def set_state(self, position: Vector3D, state: BlockState) -> bool:
        """
        Set block state at world coordinates (x, y, z).
        Returns True if successful, False if chunk not loaded or invalid position.
        """

        result = self._get_position_components(*position.as_int_tuple())
        if result is None:
            return False

        chunk, section_y, rel_x, rel_y, rel_z = result
        section = chunk.get_section(section_y)

        if section is None:
            # Create new section if needed
            section = ChunkSection()
            chunk.set_section(section_y, section)

        section.set_state(rel_x, rel_y, rel_z, state)
        return True

    def get_state(self, position: Vector3D) -> Optional[BlockState]:
        """
        Get block state at world coordinates (x, y, z).
        Returns BlockState if chunk loaded and position valid, None otherwise.
        """
        result = self._get_position_components(*position.as_int_tuple())
        if result is None:
            return None

        chunk, section_y, rel_x, rel_y, rel_z = result
        section = chunk.get_section(section_y)

        if section is None:
            # Return air if section doesn't exist
            return BlockState(0, 0)

        return section.get_state(rel_x, rel_y, rel_z)

    @staticmethod
    def _world_to_chunk_coord(coord: int) -> Tuple[int, int]:
        """Convert world coordinate to (chunk coordinate, chunk-relative coordinate)."""
        chunk_coord = coord >> 4
        rel_coord = coord & 0xF
        return chunk_coord, rel_coord

    @staticmethod
    def _block_to_section_coord(y: int) -> Tuple[int, int]:
        """Convert world Y coordinate to (section index, section-relative Y)."""
        section_y = y // 16
        rel_y = y % 16
        return section_y, rel_y