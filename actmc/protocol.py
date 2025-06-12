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


# Compression utilities
class PacketCompressor:
    """Handles packet compression/decompression with proper protocol format"""

    def __init__(self, compression_threshold: int = 256):
        self.compression_threshold = compression_threshold

    def compress_packet(self, packet_id: int, packet_data: bytes) -> bytes:
        """
        Compress packet according to Minecraft protocol format:
        - If compressed: [packet_length][data_length][compressed_data]
        - If not compressed: [packet_length][data_length=0][packet_id][packet_data]
        """
        # Create uncompressed packet content
        uncompressed_buffer = ProtocolBuffer()
        uncompressed_buffer.write(write_varint(packet_id))
        uncompressed_buffer.write(packet_data)
        uncompressed_data = uncompressed_buffer.getvalue()

        # Check if we should compress
        if len(uncompressed_data) >= self.compression_threshold:
            # Compress the data
            try:
                compressed_data = zlib.compress(uncompressed_data, level=zlib.Z_BEST_SPEED)
            except zlib.error as e:
                raise InvalidDataError(f"Failed to compress packet: {e}")

            # Build compressed packet
            result_buffer = ProtocolBuffer()
            result_buffer.write(write_varint(len(uncompressed_data)))  # Data length (uncompressed size)
            result_buffer.write(compressed_data)

            # Prepend total packet length
            packet_content = result_buffer.getvalue()
            return write_varint(len(packet_content)) + packet_content
        else:
            # Not compressed - data length is 0
            result_buffer = ProtocolBuffer()
            result_buffer.write(write_varint(0))  # Data length = 0 (not compressed)
            result_buffer.write(uncompressed_data)

            # Prepend total packet length
            packet_content = result_buffer.getvalue()
            return write_varint(len(packet_content)) + packet_content

    @staticmethod
    def decompress_packet(data: bytes) -> Tuple[int, bytes]:
        """
        Decompress packet data and return (packet_id, packet_data)
        """
        if not data:
            raise InvalidDataError("Empty packet data")

        buffer = ProtocolBuffer(data)

        # Read packet length (we don't actually need this for decompression)
        try:
            packet_length = read_varint(buffer)
        except (DataTooShortError, InvalidDataError):
            raise InvalidDataError("Invalid packet length")

        # Verify we have enough data
        if buffer.remaining() != packet_length:
            raise InvalidDataError(f"Packet length mismatch: expected {packet_length}, got {buffer.remaining()}")

        # Read data length
        try:
            data_length = read_varint(buffer)
        except (DataTooShortError, InvalidDataError):
            raise InvalidDataError("Invalid data length")

        if data_length == 0:
            # Not compressed - read packet ID and data directly
            try:
                packet_id = read_varint(buffer)
                packet_data = buffer.read(buffer.remaining())
                return packet_id, packet_data
            except DataTooShortError:
                raise InvalidDataError("Incomplete uncompressed packet")
        else:
            # Compressed - decompress first
            compressed_data = buffer.read(buffer.remaining())
            if not compressed_data:
                raise InvalidDataError("No compressed data found")

            try:
                decompressed = zlib.decompress(compressed_data)
            except zlib.error as e:
                raise InvalidDataError(f"Failed to decompress packet: {e}")

            # Verify decompressed size
            if len(decompressed) != data_length:
                raise InvalidDataError(f"Decompressed size mismatch: expected {data_length}, got {len(decompressed)}")

            # Parse decompressed data
            decompressed_buffer = ProtocolBuffer(decompressed)
            try:
                packet_id = read_varint(decompressed_buffer)
                packet_data = decompressed_buffer.read(decompressed_buffer.remaining())
                return packet_id, packet_data
            except DataTooShortError:
                raise InvalidDataError("Incomplete decompressed packet")

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