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

from .errors import DataTooShortError, InvalidDataError
import struct
import json
import uuid
import io

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Union, Optional, Tuple, Dict, List, Any
    from .types import entities, advancement

__all__ = (
    'ProtocolBuffer',
    'write_varint',
    'read_varint',
    'write_varlong',
    'read_varlong',
    'pack_string',
    'read_string',
    'read_angle',
    'read_chat',
    'read_chat_lenient',
    'pack_byte',
    'read_byte',
    'pack_ubyte',
    'read_ubyte',
    'pack_short',
    'read_short',
    'pack_ushort',
    'read_ushort',
    'pack_int',
    'read_int',
    'pack_uint',
    'read_uint',
    'pack_long',
    'read_long',
    'pack_ulong',
    'read_ulong',
    'pack_float',
    'read_float',
    'pack_double',
    'read_double',
    'pack_bool',
    'read_bool',
    'pack_uuid',
    'read_uuid',
    'peek_varint',
    'skip_bytes',
    'read_byte_array',
    'pack_byte_array',
    'pack_position',
    'read_position',
    'pack_nbt',
    'read_nbt',
    'read_entity_metadata',
    'read_slot',
    'read_criterion_progress',
    'read_advancement_progress',
    'read_advancement_display',
    'read_advancement'
)

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
        self._stream.seek(0, 2)
        end = self._stream.tell()
        self._stream.seek(current)
        return end - current


def write_varint(value: int) -> bytes:
    """Write a VarInt to bytes"""
    if value < 0:
        raise InvalidDataError("VarInt cannot be negative")

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
        raise InvalidDataError("VarLong cannot be negative")

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


def pack_string(value: str) -> bytes:
    """Pack a string with VarInt length prefix"""
    if len(value) > 32767:
        raise InvalidDataError("String too long (max 32767 characters)")

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
    return data.decode('utf-8')


def read_chat(data: ProtocolBuffer) -> Union[str, Dict, List]:
    """Read a chat component from the protocol buffer"""
    json_string = read_string(data, 262144)

    if not json_string:
        return ""

    try:
        parsed_json = json.loads(json_string)
        return parsed_json
    except json.JSONDecodeError:
        return json_string


def read_chat_lenient(data: ProtocolBuffer) -> Union[str, Dict, List]:
    """Read chat data with lenient JSON parsing"""
    json_string = read_string(data, max_length=262144)

    if not json_string:
        return ""

    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        try:
            fixed_string = json_string.replace("'", '"')
            return json.loads(fixed_string)
        except json.JSONDecodeError:
            return json_string


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
    """Pack a signed byte"""
    return _STRUCT_FORMATS['byte'].pack(value)


def read_byte(buffer: ProtocolBuffer) -> int:
    """Read a signed byte"""
    return _STRUCT_FORMATS['byte'].unpack(buffer.read(1))[0]


def pack_ubyte(value: int) -> bytes:
    """Pack an unsigned byte"""
    return _STRUCT_FORMATS['ubyte'].pack(value)


def read_ubyte(buffer: ProtocolBuffer) -> int:
    """Read an unsigned byte"""
    return _STRUCT_FORMATS['ubyte'].unpack(buffer.read(1))[0]


def pack_short(value: int) -> bytes:
    """Pack a signed short"""
    return _STRUCT_FORMATS['short'].pack(value)


def read_short(buffer: ProtocolBuffer) -> int:
    """Read a signed short"""
    return _STRUCT_FORMATS['short'].unpack(buffer.read(2))[0]


def pack_ushort(value: int) -> bytes:
    """Pack an unsigned short"""
    return _STRUCT_FORMATS['ushort'].pack(value)


def read_ushort(buffer: ProtocolBuffer) -> int:
    """Read an unsigned short"""
    return _STRUCT_FORMATS['ushort'].unpack(buffer.read(2))[0]


def pack_int(value: int) -> bytes:
    """Pack a signed int"""
    return _STRUCT_FORMATS['int'].pack(value)


def read_int(buffer: ProtocolBuffer) -> int:
    """Read a signed int"""
    return _STRUCT_FORMATS['int'].unpack(buffer.read(4))[0]


def pack_uint(value: int) -> bytes:
    """Pack an unsigned int"""
    return _STRUCT_FORMATS['uint'].pack(value)


def read_uint(buffer: ProtocolBuffer) -> int:
    """Read an unsigned int"""
    return _STRUCT_FORMATS['uint'].unpack(buffer.read(4))[0]


def pack_long(value: int) -> bytes:
    """Pack a signed long"""
    return _STRUCT_FORMATS['long'].pack(value)


def read_long(buffer: ProtocolBuffer) -> int:
    """Read a signed long"""
    return _STRUCT_FORMATS['long'].unpack(buffer.read(8))[0]


def pack_ulong(value: int) -> bytes:
    """Pack an unsigned long"""
    return _STRUCT_FORMATS['ulong'].pack(value)


def read_ulong(buffer: ProtocolBuffer) -> int:
    """Read an unsigned long"""
    return _STRUCT_FORMATS['ulong'].unpack(buffer.read(8))[0]


def pack_float(value: float) -> bytes:
    """Pack a float"""
    return _STRUCT_FORMATS['float'].pack(value)


def read_float(buffer: ProtocolBuffer) -> float:
    """Read a float"""
    return _STRUCT_FORMATS['float'].unpack(buffer.read(4))[0]


def pack_double(value: float) -> bytes:
    """Pack a double"""
    return _STRUCT_FORMATS['double'].pack(value)


def read_double(buffer: ProtocolBuffer) -> float:
    """Read a double"""
    return _STRUCT_FORMATS['double'].unpack(buffer.read(8))[0]


def pack_bool(value: bool) -> bytes:
    """Pack a boolean"""
    return b'\x01' if value else b'\x00'


def read_bool(buffer: ProtocolBuffer) -> bool:
    """Read a boolean"""
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
    """Pack position to bytes"""
    x = x & 0x3FFFFFF
    y = y & 0xFFF
    z = z & 0x3FFFFFF

    val = (x << 38) | (y << 26) | z
    return struct.pack('>Q', val)


def read_position(buffer: ProtocolBuffer) -> Tuple[int, int, int]:
    """Read position from buffer"""
    val = read_ulong(buffer)

    x = val >> 38
    y = (val >> 26) & 0xFFF
    z = val & 0x3FFFFFF

    if x >= 2 ** 25:
        x -= 2 ** 26

    if y >= 2 ** 11:
        y -= 2 ** 12

    if z >= 2 ** 25:
        z -= 2 ** 26

    return x, y, z


def pack_nbt(nbt_data: Dict[str, Any]) -> bytes:
    """Pack NBT data to bytes"""
    buffer = bytearray()

    buffer.extend(pack_ubyte(10))
    buffer.extend(pack_ushort(0))

    for name, value in nbt_data.items():
        tag_type = _get_nbt_type(value)
        buffer.extend(pack_ubyte(tag_type))
        buffer.extend(_pack_nbt_string(name))
        buffer.extend(_pack_nbt_payload(value, tag_type))

    buffer.extend(pack_ubyte(0))

    return bytes(buffer)


def _pack_nbt_string(value: str) -> bytes:
    """Pack NBT string (length-prefixed with unsigned short)"""
    encoded = value.encode('utf-8')
    return pack_ushort(len(encoded)) + encoded


def _pack_nbt_payload(value: Any, tag_type: int) -> bytes:
    """Pack the payload of an NBT tag based on its type"""
    if tag_type == 1:
        return pack_byte(value)
    elif tag_type == 2:
        return pack_short(value)
    elif tag_type == 3:
        return pack_int(value)
    elif tag_type == 4:
        return pack_long(value)
    elif tag_type == 5:
        return pack_float(value)
    elif tag_type == 6:
        return pack_double(value)
    elif tag_type == 8:
        return _pack_nbt_string(value)
    elif tag_type == 9:
        buffer = bytearray()
        if not value:
            buffer.extend(pack_ubyte(0))
            buffer.extend(pack_int(0))
        else:
            list_type = _get_nbt_type(value[0])
            buffer.extend(pack_ubyte(list_type))
            buffer.extend(pack_int(len(value)))
            for item in value:
                buffer.extend(_pack_nbt_payload(item, list_type))
        return bytes(buffer)
    elif tag_type == 10:
        buffer = bytearray()
        for name, item_value in value.items():
            item_type = _get_nbt_type(item_value)
            buffer.extend(pack_ubyte(item_type))
            buffer.extend(_pack_nbt_string(name))
            buffer.extend(_pack_nbt_payload(item_value, item_type))
        buffer.extend(pack_ubyte(0))
        return bytes(buffer)
    else:
        raise InvalidDataError(f"Unsupported NBT tag type: {tag_type}")


def _get_nbt_type(value: Any) -> int:
    """Get NBT tag type for a Python value"""
    if isinstance(value, bool):
        return 1
    elif isinstance(value, int):
        if -128 <= value <= 127:
            return 1
        elif -32768 <= value <= 32767:
            return 2
        elif -2147483648 <= value <= 2147483647:
            return 3
        else:
            return 4
    elif isinstance(value, float):
        return 5
    elif isinstance(value, str):
        return 8
    elif isinstance(value, list):
        return 9
    elif isinstance(value, dict):
        return 10
    else:
        raise InvalidDataError(f"Cannot determine NBT type for value: {value}")


def read_nbt(buffer: ProtocolBuffer) -> Dict[str, Any]:
    """Read NBT buffer from protocol buffer"""
    tag_type = read_ubyte(buffer)

    if tag_type != 10:
        raise InvalidDataError(f"NBT must start with compound tag (10), got tag type: {tag_type}")

    root_name = _read_nbt_string(buffer)
    compound_buffer = _read_compound_payload(buffer)

    return {root_name: compound_buffer} if root_name else compound_buffer


def _read_nbt_string(buffer: ProtocolBuffer) -> str:
    """Read NBT string (length-prefixed with unsigned short)"""
    length = read_ushort(buffer)
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

        name = _read_nbt_string(buffer)
        value = _read_nbt_payload(buffer, tag_type)
        compound[name] = value

    return compound


def _read_list_payload(buffer: ProtocolBuffer) -> List[Any]:
    """Read the payload of a list tag"""
    list_type = read_ubyte(buffer)
    length = read_int(buffer)

    items = []
    for _ in range(length):
        items.append(_read_nbt_payload(buffer, list_type))

    return items


def _read_nbt_payload(buffer: ProtocolBuffer, tag_type: int) -> Any:
    """Read the payload of an NBT tag based on its type"""
    if tag_type == 0:
        return None
    elif tag_type == 1:
        return read_byte(buffer)
    elif tag_type == 2:
        return read_short(buffer)
    elif tag_type == 3:
        return read_int(buffer)
    elif tag_type == 4:
        return read_long(buffer)
    elif tag_type == 5:
        return read_float(buffer)
    elif tag_type == 6:
        return read_double(buffer)
    elif tag_type == 7:
        length = read_int(buffer)
        return [read_byte(buffer) for _ in range(length)]
    elif tag_type == 8:
        return _read_nbt_string(buffer)
    elif tag_type == 9:
        return _read_list_payload(buffer)
    elif tag_type == 10:
        return _read_compound_payload(buffer)
    elif tag_type == 11:
        length = read_int(buffer)
        return [read_int(buffer) for _ in range(length)]
    elif tag_type == 12:
        length = read_int(buffer)
        return [read_long(buffer) for _ in range(length)]
    else:
        raise InvalidDataError(f"Unknown NBT tag type: {tag_type}")


def read_entity_metadata(buffer: ProtocolBuffer) -> Dict[int, Any]:
    """Read entity metadata from buffer"""
    metadata = {}

    while True:
        index = read_ubyte(buffer)

        if index == 0xFF:
            break

        metadata_type = read_varint(buffer)

        if metadata_type == 0:
            value = read_byte(buffer)
        elif metadata_type == 1:
            value = read_varint(buffer)
        elif metadata_type == 2:
            value = read_float(buffer)
        elif metadata_type == 3:
            value = read_string(buffer)
        elif metadata_type == 4:
            value = read_chat(buffer)
        elif metadata_type == 5:
            value = read_slot(buffer)
        elif metadata_type == 6:
            value = read_bool(buffer)
        elif metadata_type == 7:
            value = {
                'x': read_float(buffer),
                'y': read_float(buffer),
                'z': read_float(buffer)
            }
        elif metadata_type == 8:
            value = read_position(buffer)
        elif metadata_type == 9:
            has_value = read_bool(buffer)
            value = read_position(buffer) if has_value else None
        elif metadata_type == 10:
            value = read_varint(buffer)
        elif metadata_type == 11:
            has_value = read_bool(buffer)
            value = read_uuid(buffer) if has_value else None
        elif metadata_type == 12:
            value = read_varint(buffer)
        elif metadata_type == 13:
            value = read_nbt(buffer)
        else:
            raise InvalidDataError(f"Unknown metadata type: {metadata_type}")

        metadata[index] = {'type': metadata_type, 'value': value}

    return metadata


def read_slot(buffer: ProtocolBuffer) -> Optional[entities.ItemData]:
    """Read slot data from buffer according to Minecraft protocol"""
    item_id = read_short(buffer)

    if item_id == -1:
        return None

    item_count = read_byte(buffer)
    item_damage = read_short(buffer)

    nbt_data = None
    if buffer.remaining() > 0:
        pos = buffer.tell()
        nbt_indicator = read_byte(buffer)

        if nbt_indicator == 0:
            nbt_data = None
        else:
            buffer.seek(pos)
            nbt_data = read_nbt(buffer)

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
    if flags & 0x1:
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

    has_display = read_bool(buffer)
    display_data = None
    if has_display:
        display_data = read_advancement_display(buffer)

    criteria_count = read_varint(buffer)
    criteria = {}
    for _ in range(criteria_count):
        criterion_id = read_string(buffer)
        criteria[criterion_id] = None

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