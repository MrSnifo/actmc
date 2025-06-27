import struct
import json
import uuid
import io
from .errors import DataTooShortError, InvalidDataError
from typing import Union, Optional, Tuple, Dict, List, Any
from .enums import NBTTagType

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

def read_angle(buffer: ProtocolBuffer) -> float:
    """Read an angle from buffer (1 byte, scaled to 360 degrees)"""
    angle_byte = read_ubyte(buffer)
    return (angle_byte * 360) / 256.0

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


def read_chat(data: ProtocolBuffer) -> Union[str, Dict, List]:
    """
    Read a chat component from the protocol buffer.

    Chat data is sent as a UTF-8 encoded JSON string in the protocol.
    The JSON can represent:
    - A simple string (converted to string component)
    - A JSON object (chat component)
    - A JSON array (array of components)

    Args:
        data: ProtocolBuffer containing the packet data

    Returns:
        Parsed JSON data as string, dict, or list

    Raises:
        ValueError: If JSON parsing fails
        IndexError: If not enough data in buffer
    """
    try:
        json_string = read_string(data, 262144)

        # Handle empty string
        if not json_string:
            return ""

        # Try to parse as JSON
        try:
            parsed_json = json.loads(json_string)
            return parsed_json
        except json.JSONDecodeError:
            # If JSON parsing fails, treat as plain text
            # This handles cases where raw text is sent instead of JSON
            return json_string

    except (IndexError, struct.error) as e:
        raise ValueError(f"Failed to read chat data: {e}")


def read_chat_lenient(data: ProtocolBuffer) -> Union[str, Dict, List]:
    """
    Read chat data with lenient JSON parsing.
    Used for disconnect packets and written book text.

    This version is more forgiving with malformed JSON.
    """
    try:
        json_string = read_string(data, max_length=262144)

        if not json_string:
            return ""

        # Try lenient parsing - allow some JSON errors
        try:
            # First try normal JSON parsing
            return json.loads(json_string)
        except json.JSONDecodeError:
            try:
                # Try with some common fixes for malformed JSON
                # Fix single quotes to double quotes
                fixed_string = json_string.replace("'", '"')
                return json.loads(fixed_string)
            except json.JSONDecodeError:
                # If all else fails, return as plain text
                return json_string

    except (IndexError, struct.error) as e:
        raise ValueError(f"Failed to read chat data: {e}")

# Primitive types operations with struct format cache
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

    return x, y, z


def read_nbt(buffer: ProtocolBuffer) -> Dict[str, Any]:
    """Read NBT buffer from protocol buffer - starts with a compound tag"""
    tag_type = read_ubyte(buffer)

    if tag_type != NBTTagType.TAG_COMPOUND:
        raise ValueError(f"NBT must start with TAG_Compound, got tag type: {tag_type}")

    # Read the root compound name
    root_name = _read_nbt_string(buffer)

    # Read the compound contents
    compound_buffer = _read_compound_payload(buffer)

    return {root_name: compound_buffer} if root_name else compound_buffer


def _read_nbt_string(buffer: ProtocolBuffer) -> str:
    """Read NBT string (length-prefixed with unsigned short)"""
    length = read_ushort(buffer)  # unsigned short (2 bytes)
    if length == 0:
        return ""
    return buffer.read(length).decode('utf-8')


def _read_compound_payload(buffer: ProtocolBuffer) -> Dict[str, Any]:
    """Read the payload of a compound tag"""
    compound = {}

    while True:
        tag_type = read_ubyte(buffer)

        if tag_type == NBTTagType.TAG_END:
            break

        # Read tag name
        name = _read_nbt_string(buffer)

        # Read tag payload
        value = _read_nbt_payload(buffer, tag_type)
        compound[name] = value

    return compound


def _read_list_payload(buffer: ProtocolBuffer) -> List[Any]:
    """Read the payload of a list tag"""
    list_type = read_ubyte(buffer)
    length = read_int(buffer)  # signed int (4 bytes)

    items = []
    for _ in range(length):
        # List items have no names, just payloads
        items.append(_read_nbt_payload(buffer, list_type))

    return items


def _read_nbt_payload(buffer: ProtocolBuffer, tag_type: int) -> Any:
    """Read the payload of an NBT tag based on its type"""
    if tag_type == NBTTagType.TAG_END:
        return None

    elif tag_type == NBTTagType.TAG_BYTE:
        return read_byte(buffer)  # signed byte

    elif tag_type == NBTTagType.TAG_SHORT:
        return read_short(buffer)  # signed short, big-endian

    elif tag_type == NBTTagType.TAG_INT:
        return read_int(buffer)  # signed int, big-endian

    elif tag_type == NBTTagType.TAG_LONG:
        return read_long(buffer)  # signed long, big-endian

    elif tag_type == NBTTagType.TAG_FLOAT:
        return read_float(buffer)  # IEEE-754 single precision, big-endian

    elif tag_type == NBTTagType.TAG_DOUBLE:
        return read_double(buffer)  # IEEE-754 double precision, big-endian

    elif tag_type == NBTTagType.TAG_BYTE_ARRAY:
        length = read_int(buffer)  # signed int (4 bytes)
        return [read_byte(buffer) for _ in range(length)]

    elif tag_type == NBTTagType.TAG_STRING:
        return _read_nbt_string(buffer)

    elif tag_type == NBTTagType.TAG_LIST:
        return _read_list_payload(buffer)

    elif tag_type == NBTTagType.TAG_COMPOUND:
        return _read_compound_payload(buffer)

    elif tag_type == NBTTagType.TAG_INT_ARRAY:
        length = read_int(buffer)  # signed int (4 bytes)
        return [read_int(buffer) for _ in range(length)]

    elif tag_type == NBTTagType.TAG_LONG_ARRAY:
        length = read_int(buffer)  # signed int (4 bytes)
        return [read_long(buffer) for _ in range(length)]

    else:
        raise ValueError(f"Unknown NBT tag type: {tag_type}")