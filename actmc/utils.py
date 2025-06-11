from struct import pack, unpack
from typing import Tuple
import json
import zlib
import uuid
from typing import Optional, List, Union
import logging


def write_varint(value: int) -> bytes:
    """Write a VarInt to bytes"""
    buf = bytearray()
    while True:
        towrite = value & 0x7f
        value >>= 7
        if value:
            buf.append(towrite | 0x80)
        else:
            buf.append(towrite)
            break
    return bytes(buf)


def read_varint(data: bytes, offset: int = 0) -> Tuple[int, int]:
    """Read VarInt from bytes"""
    value = 0
    position = 0
    while True:
        if offset >= len(data):
            raise ValueError("Unexpected end of data while reading VarInt")

        current_byte = data[offset]
        offset += 1

        value |= (current_byte & 0x7F) << position
        if (current_byte & 0x80) == 0:
            break

        position += 7
        if position >= 32:
            raise ValueError("VarInt too big (max 5 bytes)")
    return value, offset


def write_varlong(value: int) -> bytes:
    """Write a VarLong to bytes"""
    buf = bytearray()
    while True:
        towrite = value & 0x7f
        value >>= 7
        if value:
            buf.append(towrite | 0x80)
        else:
            buf.append(towrite)
            break
    return bytes(buf)


def read_varlong(data: bytes, offset: int = 0) -> Tuple[int, int]:
    """Read VarLong from bytes"""
    value = 0
    position = 0
    while True:
        if offset >= len(data):
            raise ValueError("Unexpected end of data while reading VarLong")

        current_byte = data[offset]
        offset += 1

        value |= (current_byte & 0x7F) << position
        if (current_byte & 0x80) == 0:
            break

        position += 7
        if position >= 64:
            raise ValueError("VarLong too big (max 10 bytes)")
    return value, offset


def read_angle(data: bytes, offset: int) -> tuple[float, int]:
    angle_byte = data[offset]
    offset += 1
    degrees = (angle_byte * 360) / 256
    return degrees, offset


def read_slot(data: bytes, offset: int):
    # First a boolean: 0 means empty slot, 1 means not empty
    is_present = data[offset]
    offset += 1
    if is_present == 0:
        return None, offset

    # Item ID as VarInt
    item_id, offset = read_varint(data, offset)

    # Item count (signed byte)
    item_count = data[offset]
    offset += 1

    # NBT data: you need an NBT parser here, or skip if not implemented
    # For now, just read length varint then skip that many bytes
    nbt_length, offset = read_varint(data, offset)
    nbt_data = data[offset:offset + nbt_length]
    offset += nbt_length

    # You might want to parse nbt_data properly if you have a parser

    slot_data = {
        "item_id": item_id,
        "count": item_count,
        "nbt": nbt_data  # raw for now
    }

    return slot_data, offset

def read_entity_metadata(data: bytes, offset: int):
    metadata = []
    while True:
        index = data[offset]
        offset += 1
        if index == 0xFF:
            break
        data_type = data[offset]
        offset += 1

        if data_type == 0:  # Byte
            value = data[offset]
            offset += 1
        elif data_type == 1:  # VarInt
            value, offset = read_varint(data, offset)
        elif data_type == 2:  # Float
            value, offset = read_float(data, offset)
        elif data_type == 3:  # String
            value, offset = read_string(data, offset)
        elif data_type == 6:  # Slot
            value, offset = read_slot(data, offset)
        else:
            raise ValueError(f"Unsupported data_type {data_type} in entity metadata")

        metadata.append((index, data_type, value))

    return metadata, offset


def read_nbt(data: bytes, offset: int):
    """
    Minimal stub to parse NBT data from bytes starting at offset.
    This example skips the entire NBT tag by reading until the
    end of the compound tag (TAG_End, 0x00) is found.

    Real NBT parsing is more complex and involves recursive reading.
    """
    # NBT format always starts with a TAG type byte
    # 0x00 means end of a compound tag
    # For simplicity, just find the next 0x00 byte after offset and
    # assume NBT ends there (not always correct, but a placeholder)
    start = offset
    length = len(data)

    while offset < length:
        tag_type = data[offset]
        offset += 1
        if tag_type == 0:  # TAG_End, end of compound
            break
        # skip the name (short-prefixed string)
        name_length = (data[offset] << 8) + data[offset + 1]
        offset += 2 + name_length
        # skipping payload is non-trivial - so break here
        # or you can raise NotImplementedError
        raise NotImplementedError("Full NBT parsing not implemented")

    nbt_bytes = data[start:offset]
    return nbt_bytes, offset


def read_chat(data: bytes, offset: int):
    length, offset = read_varint(data, offset)  # Read length of JSON string
    chat_json = data[offset:offset + length].decode('utf-8')  # Decode JSON string
    offset += length
    try:
        chat_obj = json.loads(chat_json)  # Parse JSON to Python dict
    except json.JSONDecodeError:
        chat_obj = {"text": chat_json}  # Fallback to raw text if JSON invalid
    return chat_obj, offset

# Basic type packers/unpackers (expanded)

def byte(value: int) -> bytes:
    return pack('>b', value)


def read_byte(data: bytes, offset: int = 0) -> Tuple[int, int]:
    return unpack('>b', data[offset:offset + 1])[0], offset + 1


def ubyte(value: int) -> bytes:
    return pack('>B', value)


def read_ubyte(data: bytes, offset: int = 0) -> Tuple[int, int]:
    return unpack('>B', data[offset:offset + 1])[0], offset + 1


def short(value: int) -> bytes:
    return pack('>h', value)


def read_short(data: bytes, offset: int = 0) -> Tuple[int, int]:
    return unpack('>h', data[offset:offset + 2])[0], offset + 2


def ushort(value: int) -> bytes:
    """Pack an unsigned short (2 bytes, big-endian) - used for ports"""
    return pack('>H', value)


def read_ushort(data: bytes, offset: int = 0) -> Tuple[int, int]:
    """Unpack an unsigned short (2 bytes, big-endian)"""
    return unpack('>H', data[offset:offset + 2])[0], offset + 2


def int(value: int) -> bytes:
    return pack('>i', value)


def read_int(data: bytes, offset: int = 0) -> Tuple[int, int]:
    return unpack('>i', data[offset:offset + 4])[0], offset + 4


def uint(value: int) -> bytes:
    return pack('>I', value)


def read_uint(data: bytes, offset: int = 0) -> Tuple[int, int]:
    return unpack('>I', data[offset:offset + 4])[0], offset + 4


def long(value: int) -> bytes:
    return pack('>q', value)


def read_long(data: bytes, offset: int = 0) -> Tuple[int, int]:
    return unpack('>q', data[offset:offset + 8])[0], offset + 8


def ulong(value: int) -> bytes:
    return pack('>Q', value)


def read_ulong(data: bytes, offset: int = 0) -> Tuple[int, int]:
    return unpack('>Q', data[offset:offset + 8])[0], offset + 8


def float(value: float) -> bytes:
    return pack('>f', value)


def read_float(data: bytes, offset: int = 0) -> Tuple[float, int]:
    return unpack('>f', data[offset:offset + 4])[0], offset + 4


def double(value: float) -> bytes:
    return pack('>d', value)


def read_double(data: bytes, offset: int = 0) -> Tuple[float, int]:
    return unpack('>d', data[offset:offset + 8])[0], offset + 8


def string(value: str) -> bytes:
    encoded = value.encode('utf-8')
    return write_varint(len(encoded)) + encoded


def read_uuid(data: bytes, offset: int):
    # UUID is 16 bytes long
    uuid_bytes = data[offset:offset + 16]
    offset += 16
    # Convert bytes to UUID string with hyphens
    u = str(uuid.UUID(bytes=uuid_bytes))
    return u, offset


def read_string(data: bytes, offset: int = 0) -> Tuple[str, int]:
    length, offset = read_varint(data, offset)
    return data[offset:offset + length].decode('utf-8'), offset + length


def bool(value: bool) -> bytes:
    return b'\x01' if value else b'\x00'


def read_bool(data: bytes, offset: int = 0) -> Tuple[bool, int]:
    return data[offset] != 0, offset + 1


def compress_packet(packet_id: int, data: bytes) -> bytes:
    uncompressed = write_varint(packet_id) + data
    compressor = zlib.compressobj(level=zlib.Z_DEFAULT_COMPRESSION, wbits=15)
    compressed = compressor.compress(uncompressed)
    return compressed + compressor.flush()


def decompress_packet(compressed_data: bytes, uncompressed_size: int) -> tuple[int, bytes]:
    decompressor = zlib.decompressobj(wbits=15)
    uncompressed = decompressor.decompress(compressed_data, uncompressed_size)
    uncompressed += decompressor.flush()
    if len(uncompressed) != uncompressed_size:
        raise ValueError("Decompressed size mismatch")
    packet_id, offset = read_varint(uncompressed)
    return packet_id, uncompressed[offset:]



LOGGER_TRACE: int = 5
logging.addLevelName(LOGGER_TRACE, "TRACE")

def trace(self, message, *args, **kwargs):
    if self.isEnabledFor(LOGGER_TRACE):
        self._log(LOGGER_TRACE, message, args, **kwargs)

logging.Logger.trace = trace

def setup_logging(*,
                  handler: Optional[logging.Handler] = None,
                  level: Optional[int] = None,
                  root: bool = True) -> None:
    """
    Setup logging configuration, including custom TRACE level.
    """
    if level is None:
        level = logging.INFO

    # Accept level as string 'TRACE' or int
    if isinstance(level, str):
        level = level.upper()
        if level == "TRACE":
            level = LOGGER_TRACE
        else:
            level = getattr(logging, level, logging.INFO)

    if handler is None:
        handler = logging.StreamHandler()

    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname}] {name}: {message}', dt_fmt, style='{')

    if root:
        logger = logging.getLogger()
    else:
        library, _, _ = __name__.partition('.')
        logger = logging.getLogger(library)

    handler.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(handler)