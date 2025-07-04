import struct
import json
import uuid
import io

from .errors import DataTooShortError, InvalidDataError
from typing import Union, Optional, Tuple, Dict, List, Any
from .types import entities, advancement

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

    Chat data is sent as a UTF-8 encoded JSON string in the 
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


def pack_position(x: int, y: int, z: int) -> bytes:
    x = x & 0x3FFFFFF
    y = y & 0xFFF
    z = z & 0x3FFFFFF

    val = (x << 38) | (y << 26) | z
    return struct.pack('>Q', val)


def read_position(buffer: ProtocolBuffer) -> Tuple[int, int, int]:
    val = read_ulong(buffer)

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


def pack_nbt(nbt_data: Dict[str, Any]) -> bytes:
    """Pack NBT data to bytes - minimal implementation for slot data"""
    buffer = bytearray()

    # NBT starts with a compound tag (type 10)
    buffer.extend(pack_ubyte(10))

    # Write empty root name (compound name is empty string)
    buffer.extend(pack_ushort(0))

    # Write compound contents
    for name, value in nbt_data.items():
        tag_type = _get_nbt_type(value)
        buffer.extend(pack_ubyte(tag_type))
        buffer.extend(_pack_nbt_string(name))
        buffer.extend(_pack_nbt_payload(value, tag_type))

    # End tag
    buffer.extend(pack_ubyte(0))

    return bytes(buffer)


def _pack_nbt_string(value: str) -> bytes:
    """Pack NBT string (length-prefixed with unsigned short)"""
    encoded = value.encode('utf-8')
    return pack_ushort(len(encoded)) + encoded


def _pack_nbt_payload(value: Any, tag_type: int) -> bytes:
    """Pack the payload of an NBT tag based on its type"""
    if tag_type == 1:  # Byte
        return pack_byte(value)
    elif tag_type == 2:  # Short
        return pack_short(value)
    elif tag_type == 3:  # Int
        return pack_int(value)
    elif tag_type == 4:  # Long
        return pack_long(value)
    elif tag_type == 5:  # Float
        return pack_float(value)
    elif tag_type == 6:  # Double
        return pack_double(value)
    elif tag_type == 8:  # String
        return _pack_nbt_string(value)
    elif tag_type == 9:  # List
        buffer = bytearray()
        if not value:
            buffer.extend(pack_ubyte(0))  # Empty list type
            buffer.extend(pack_int(0))  # Length 0
        else:
            list_type = _get_nbt_type(value[0])
            buffer.extend(pack_ubyte(list_type))
            buffer.extend(pack_int(len(value)))
            for item in value:
                buffer.extend(_pack_nbt_payload(item, list_type))
        return bytes(buffer)
    elif tag_type == 10:  # Compound
        buffer = bytearray()
        for name, item_value in value.items():
            item_type = _get_nbt_type(item_value)
            buffer.extend(pack_ubyte(item_type))
            buffer.extend(_pack_nbt_string(name))
            buffer.extend(_pack_nbt_payload(item_value, item_type))
        buffer.extend(pack_ubyte(0))  # End tag
        return bytes(buffer)
    else:
        raise ValueError(f"Unsupported NBT tag type: {tag_type}")


def _get_nbt_type(value: Any) -> int:
    """Get NBT tag type for a Python value"""
    if isinstance(value, bool):
        return 1  # Treat as byte
    elif isinstance(value, int):
        if -128 <= value <= 127:
            return 1  # Byte
        elif -32768 <= value <= 32767:
            return 2  # Short
        elif -2147483648 <= value <= 2147483647:
            return 3  # Int
        else:
            return 4  # Long
    elif isinstance(value, float):
        return 5  # Float
    elif isinstance(value, str):
        return 8  # String
    elif isinstance(value, list):
        return 9  # List
    elif isinstance(value, dict):
        return 10  # Compound
    else:
        raise ValueError(f"Cannot determine NBT type for value: {value}")


def read_nbt(buffer: ProtocolBuffer) -> Dict[str, Any]:
    """Read NBT buffer from protocol buffer - starts with a compound tag"""
    tag_type = read_ubyte(buffer)

    if tag_type != 10:
        raise ValueError(f"NBT must start with 10, got tag type: {tag_type}")

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

        if tag_type == 0:
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
    if tag_type == 0:
        return None

    elif tag_type == 1:
        return read_byte(buffer)  # signed byte

    elif tag_type == 2:
        return read_short(buffer)  # signed short, big-endian

    elif tag_type == 3:
        return read_int(buffer)  # signed int, big-endian

    elif tag_type == 4:
        return read_long(buffer)  # signed long, big-endian

    elif tag_type == 5:
        return read_float(buffer)  # IEEE-754 single precision, big-endian

    elif tag_type == 6:
        return read_double(buffer)  # IEEE-754 double precision, big-endian

    elif tag_type == 7:
        length = read_int(buffer)  # signed int (4 bytes)
        return [read_byte(buffer) for _ in range(length)]

    elif tag_type == 8:
        return _read_nbt_string(buffer)

    elif tag_type == 9:
        return _read_list_payload(buffer)

    elif tag_type == 10:
        return _read_compound_payload(buffer)

    elif tag_type == 11:
        length = read_int(buffer)  # signed int (4 bytes)
        return [read_int(buffer) for _ in range(length)]

    elif tag_type == 12:
        length = read_int(buffer)  # signed int (4 bytes)
        return [read_long(buffer) for _ in range(length)]

    else:
        raise ValueError(f"Unknown NBT tag type: {tag_type}")


def read_entity_metadata(buffer: ProtocolBuffer) -> Dict[int, Any]:
    """Read entity metadata from buffer"""
    metadata = {}

    while True:
        # Read the index byte
        index = read_ubyte(buffer)

        # Index 0xFF marks the end of metadata
        if index == 0xFF:
            break

        # Read the type
        metadata_type = read_varint(buffer)

        # Handle unknown metadata types gracefully
        try:
            # Read the value based on type (according to wiki.vg documentation)
            if metadata_type == 0:  # Byte
                value = read_byte(buffer)
            elif metadata_type == 1:  # VarInt
                value = read_varint(buffer)
            elif metadata_type == 2:  # Float
                value = read_float(buffer)
            elif metadata_type == 3:  # String
                value = read_string(buffer)
            elif metadata_type == 4:  # Chat
                value = read_chat(buffer)
            elif metadata_type == 5:  # Slot
                value = read_slot(buffer)
            elif metadata_type == 6:  # Boolean
                value = read_bool(buffer)
            elif metadata_type == 7:  # Rotation (3 floats: x, y, z)
                value = {
                    'x': read_float(buffer),
                    'y': read_float(buffer),
                    'z': read_float(buffer)
                }
            elif metadata_type == 8:  # Position
                value = read_position(buffer)
            elif metadata_type == 9:  # OptPosition (Boolean + Optional Position)
                has_value = read_bool(buffer)
                value = read_position(buffer) if has_value else None
            elif metadata_type == 10:  # Direction (VarInt)
                value = read_varint(buffer)
            elif metadata_type == 11:  # OptUUID (Boolean + Optional UUID)
                has_value = read_bool(buffer)
                value = read_uuid(buffer) if has_value else None
            elif metadata_type == 12:  # OptBlockID (VarInt)
                value = read_varint(buffer)
            elif metadata_type == 13:  # NBT Tag
                value = read_nbt(buffer)
            else:
                value = f"<unknown_type_{metadata_type}>"
        # todo: i don't like this
        except (ValueError, EOFError) as e:
            value = f"<error_reading_type_{metadata_type}: {e}>"


        metadata[index] = {'type': metadata_type, 'value': value}

    return metadata



def read_slot(buffer: ProtocolBuffer) -> Optional[entities.ItemData]:
    """Read slot data from buffer according to Minecraft protocol"""
    # Read Block ID (Short)
    item_id = read_short(buffer)

    if item_id == -1:
        return None

    item_count = read_byte(buffer)

    item_damage = read_short(buffer)

    nbt_data = None
    if buffer.remaining() > 0:
        pos = buffer.tell()
        try:
            nbt_indicator = read_byte(buffer)

            if nbt_indicator == 0:
                # No NBT data
                nbt_data = None
            else:
                buffer.seek(pos)
                nbt_data = read_nbt(buffer)
        except (EOFError, ValueError, struct.error):
            buffer.seek(pos)
            nbt_data = None

    return {'item_id': item_id, 'item_count': item_count, 'item_damage': item_damage, 'nbt': nbt_data } # type: ignore


def read_criterion_progress(buffer: ProtocolBuffer) -> advancement.CriterionProgress:
    """Read criterion progress data from buffer"""
    achieved = read_bool(buffer)
    date_of_achieving = None

    if achieved:
        date_of_achieving = read_long(buffer)

    return {
        'achieved': achieved,
        'date_of_achieving': date_of_achieving
    }


def read_advancement_progress(buffer: ProtocolBuffer) -> advancement.AdvancementProgress:
    """Read advancement progress data from buffer"""
    size = read_varint(buffer)
    criteria = {}

    for _ in range(size):
        criterion_id = read_string(buffer)
        criterion_progress = read_criterion_progress(buffer)
        criteria[criterion_id] = criterion_progress

    return {
        'criteria': criteria
    }


def read_advancement_display(buffer: ProtocolBuffer) -> advancement.AdvancementDisplay:
    """Read advancement display data from buffer"""
    title = read_chat(buffer)
    description = read_chat(buffer)
    icon = read_slot(buffer)
    frame_type = read_varint(buffer)
    flags = read_int(buffer)

    background_texture = None
    if flags & 0x1:  # Has background texture
        background_texture = read_string(buffer)

    x_coord = read_float(buffer)
    y_coord = read_float(buffer)

    return {
        'title': title,
        'description': description,
        'icon': icon,
        'frame_type': frame_type,
        'flags': flags,
        'background_texture': background_texture,
        'x_coord': x_coord,
        'y_coord': y_coord
    }


def read_advancement(buffer: ProtocolBuffer) -> advancement.Advancement:
    """Read a single advancement from buffer"""
    has_parent = read_bool(buffer)
    parent_id = None
    if has_parent:
        parent_id = read_string(buffer)

    # Check if has display data
    has_display = read_bool(buffer)
    display_data = None
    if has_display:
        display_data = read_advancement_display(buffer)

    # Read criteria
    criteria_count = read_varint(buffer)
    criteria = {}
    for _ in range(criteria_count):
        criterion_id = read_string(buffer)
        # Criterion value is void (no content)
        criteria[criterion_id] = None

    # Read requirements
    requirements_count = read_varint(buffer)
    requirements = []
    for _ in range(requirements_count):
        requirement_array_length = read_varint(buffer)
        requirement_array = []
        for _ in range(requirement_array_length):
            requirement = read_string(buffer)
            requirement_array.append(requirement)
        requirements.append(requirement_array)

    return {
        'parent_id': parent_id,
        'display_data': display_data,
        'criteria': criteria,
        'requirements': requirements
    }
