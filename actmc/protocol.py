import struct
import json
import uuid
import zlib
import io
from typing import Dict, Union, Any, Optional, Tuple
from .errors import DataTooShortError, InvalidDataError


class ProtocolBuffer:
    """A wrapper around BytesIO with protocol-specific methods"""

    def __init__(self, data: Union[bytes, bytearray] = b''):
        self._stream = io.BytesIO(data)

    def read(self, size: int) -> bytes:
        """Read exactly size bytes or raise error"""
        data = self._stream.read(size)
        if len(data) != size:
            raise DataTooShortError(f"Expected {size} bytes, got {len(data)}")
        return data

    def write(self, data: bytes) -> None:
        """Write data to buffer"""
        self._stream.write(data)

    def tell(self) -> int:
        """Get current position"""
        return self._stream.tell()

    def seek(self, pos: int) -> None:
        """Seek to position"""
        self._stream.seek(pos)

    def getvalue(self) -> bytes:
        """Get all buffer contents"""
        return self._stream.getvalue()

    def remaining(self) -> int:
        """Get number of bytes remaining"""
        current = self._stream.tell()
        self._stream.seek(0, 2)  # Seek to end
        end = self._stream.tell()
        self._stream.seek(current)  # Seek back
        return end - current


# VarInt/VarLong operations
def write_varint(value: int) -> bytes:
    """Write a VarInt to bytes"""
    if value < 0:
        raise ValueError("VarInt cannot be negative")

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


def read_varint(buffer: ProtocolBuffer) -> int:
    """Read VarInt from buffer"""
    value = 0
    position = 0
    while True:
        byte_data = buffer.read(1)
        current_byte = byte_data[0]

        value |= (current_byte & 0x7F) << position
        if (current_byte & 0x80) == 0:
            break

        position += 7
        if position >= 32:
            raise InvalidDataError("VarInt too big (max 5 bytes)")
    return value


def write_varlong(value: int) -> bytes:
    """Write a VarLong to bytes"""
    if value < 0:
        raise ValueError("VarLong cannot be negative")

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


def read_varlong(buffer: ProtocolBuffer) -> int:
    """Read VarLong from buffer"""
    value = 0
    position = 0
    while True:
        byte_data = buffer.read(1)
        current_byte = byte_data[0]

        value |= (current_byte & 0x7F) << position
        if (current_byte & 0x80) == 0:
            break

        position += 7
        if position >= 64:
            raise InvalidDataError("VarLong too big (max 10 bytes)")
    return value


# String operations
def pack_string(value: str) -> bytes:
    """Pack a string with VarInt length prefix"""
    if len(value) > 32767:  # Minecraft string limit
        raise ValueError("String too long (max 32767 characters)")

    encoded = value.encode('utf-8')
    return write_varint(len(encoded)) + encoded


def read_string(buffer: ProtocolBuffer, max_length: int = 32767) -> str:
    """Read a string from buffer with optional max length check"""
    length = read_varint(buffer)
    if length > max_length:
        raise InvalidDataError(f"String too long: {length} > {max_length}")

    data = buffer.read(length)
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError as e:
        raise InvalidDataError(f"Invalid UTF-8 string: {e}")


def read_chat(buffer: ProtocolBuffer) -> Dict[str, Any]:
    """Read chat component from buffer"""
    chat_json = read_string(buffer)
    try:
        return json.loads(chat_json)
    except json.JSONDecodeError:
        return {"text": chat_json}


# Primitive type operations with struct format cache
_STRUCT_FORMATS = {
    'byte': struct.Struct('>b'),
    'ubyte': struct.Struct('>B'),
    'short': struct.Struct('>h'),
    'ushort': struct.Struct('>H'),
    'int': struct.Struct('>i'),
    'uint': struct.Struct('>I'),
    'long': struct.Struct('>q'),
    'ulong': struct.Struct('>Q'),
    'float': struct.Struct('>f'),
    'double': struct.Struct('>d'),
}


def pack_byte(value: int) -> bytes:
    return _STRUCT_FORMATS['byte'].pack(value)


def read_byte(buffer: ProtocolBuffer) -> int:
    return _STRUCT_FORMATS['byte'].unpack(buffer.read(1))[0]


def pack_ubyte(value: int) -> bytes:
    return _STRUCT_FORMATS['ubyte'].pack(value)


def read_ubyte(buffer: ProtocolBuffer) -> int:
    return _STRUCT_FORMATS['ubyte'].unpack(buffer.read(1))[0]


def pack_short(value: int) -> bytes:
    return _STRUCT_FORMATS['short'].pack(value)


def read_short(buffer: ProtocolBuffer) -> int:
    return _STRUCT_FORMATS['short'].unpack(buffer.read(2))[0]


def pack_ushort(value: int) -> bytes:
    return _STRUCT_FORMATS['ushort'].pack(value)


def read_ushort(buffer: ProtocolBuffer) -> int:
    return _STRUCT_FORMATS['ushort'].unpack(buffer.read(2))[0]


def pack_int(value: int) -> bytes:
    return _STRUCT_FORMATS['int'].pack(value)


def read_int(buffer: ProtocolBuffer) -> int:
    return _STRUCT_FORMATS['int'].unpack(buffer.read(4))[0]


def pack_uint(value: int) -> bytes:
    return _STRUCT_FORMATS['uint'].pack(value)


def read_uint(buffer: ProtocolBuffer) -> int:
    return _STRUCT_FORMATS['uint'].unpack(buffer.read(4))[0]


def pack_long(value: int) -> bytes:
    return _STRUCT_FORMATS['long'].pack(value)


def read_long(buffer: ProtocolBuffer) -> int:
    return _STRUCT_FORMATS['long'].unpack(buffer.read(8))[0]


def pack_ulong(value: int) -> bytes:
    return _STRUCT_FORMATS['ulong'].pack(value)


def read_ulong(buffer: ProtocolBuffer) -> int:
    return _STRUCT_FORMATS['ulong'].unpack(buffer.read(8))[0]


def pack_float(value: float) -> bytes:
    return _STRUCT_FORMATS['float'].pack(value)


def read_float(buffer: ProtocolBuffer) -> float:
    return _STRUCT_FORMATS['float'].unpack(buffer.read(4))[0]


def pack_double(value: float) -> bytes:
    return _STRUCT_FORMATS['double'].pack(value)


def read_double(buffer: ProtocolBuffer) -> float:
    return _STRUCT_FORMATS['double'].unpack(buffer.read(8))[0]


def pack_bool(value: bool) -> bytes:
    return b'\x01' if value else b'\x00'


def read_bool(buffer: ProtocolBuffer) -> bool:
    return buffer.read(1)[0] != 0


def pack_uuid(value: Union[str, uuid.UUID]) -> bytes:
    """Pack UUID to bytes"""
    if isinstance(value, str):
        value = uuid.UUID(value)
    return value.bytes


def read_uuid(buffer: ProtocolBuffer) -> str:
    """Read UUID from buffer"""
    uuid_bytes = buffer.read(16)
    return str(uuid.UUID(bytes=uuid_bytes))


# Utility functions
def peek_varint(buffer: ProtocolBuffer) -> int:
    """Peek at VarInt without advancing buffer position"""
    pos = buffer.tell()
    try:
        value = read_varint(buffer)
        return value
    finally:
        buffer.seek(pos)


def skip_bytes(buffer: ProtocolBuffer, count: int) -> None:
    """Skip count bytes in buffer"""
    buffer.read(count)


def read_byte_array(buffer: ProtocolBuffer, length: Optional[int] = None) -> bytes:
    """Read byte array, optionally with VarInt length prefix"""
    if length is None:
        length = read_varint(buffer)
    return buffer.read(length)


def pack_byte_array(data: bytes, include_length: bool = True) -> bytes:
    """Pack byte array, optionally with VarInt length prefix"""
    if include_length:
        return write_varint(len(data)) + data
    return data


def read_position(buffer: ProtocolBuffer) -> Tuple[int, int, int]:
    """
    Read a 64-bit position value from buffer and decode into x, y, z coordinates.

    Position format:
    - x: 26 MSBs (most significant bits)
    - y: 12 bits in the middle
    - z: 26 LSBs (least significant bits)

    Returns:
        Tuple[int, int, int]: (x, y, z) coordinates with proper sign handling
    """
    # Read the 64-bit unsigned value from buffer
    val = read_ulong(buffer)

    # Extract the three components using bit operations
    x = val >> 38  # Get top 26 bits
    y = (val >> 26) & 0xFFF  # Get middle 12 bits
    z = val & 0x3FFFFFF  # Get bottom 26 bits using mask

    # Handle two's complement for signed values
    # x: 26-bit signed (-2^25 to 2^25-1)
    if x >= 2 ** 25:
        x -= 2 ** 26

    # y: 12-bit signed (-2^11 to 2^11-1)
    if y >= 2 ** 11:
        y -= 2 ** 12

    # z: 26-bit signed (-2^25 to 2^25-1)
    if z >= 2 ** 25:
        z -= 2 ** 26

    return (x, y, z)