from struct import pack, unpack
from typing import Tuple
import zlib
from typing import Optional
import logging

class Packet:
    """Minecraft protocol packet utilities with proper VarInt support"""

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    class Packet:
        """Minecraft protocol packet utilities with complete type support"""

        # VarInt/VarLong handling (unchanged from previous)
        @staticmethod
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

        @staticmethod
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

        @staticmethod
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

        @staticmethod
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

    # Basic type packers/unpackers (expanded)
    @staticmethod
    def byte(value: int) -> bytes:
        return pack('>b', value)

    @staticmethod
    def read_byte(data: bytes, offset: int = 0) -> Tuple[int, int]:
        return unpack('>b', data[offset:offset + 1])[0], offset + 1

    @staticmethod
    def ubyte(value: int) -> bytes:
        return pack('>B', value)

    @staticmethod
    def read_ubyte(data: bytes, offset: int = 0) -> Tuple[int, int]:
        return unpack('>B', data[offset:offset + 1])[0], offset + 1

    @staticmethod
    def short(value: int) -> bytes:
        return pack('>h', value)

    @staticmethod
    def read_short(data: bytes, offset: int = 0) -> Tuple[int, int]:
        return unpack('>h', data[offset:offset + 2])[0], offset + 2

    @staticmethod
    def ushort(value: int) -> bytes:
        """Pack an unsigned short (2 bytes, big-endian) - used for ports"""
        return pack('>H', value)

    @staticmethod
    def read_ushort(data: bytes, offset: int = 0) -> Tuple[int, int]:
        """Unpack an unsigned short (2 bytes, big-endian)"""
        return unpack('>H', data[offset:offset + 2])[0], offset + 2

    @staticmethod
    def int(value: int) -> bytes:
        return pack('>i', value)

    @staticmethod
    def read_int(data: bytes, offset: int = 0) -> Tuple[int, int]:
        return unpack('>i', data[offset:offset + 4])[0], offset + 4

    @staticmethod
    def uint(value: int) -> bytes:
        return pack('>I', value)

    @staticmethod
    def read_uint(data: bytes, offset: int = 0) -> Tuple[int, int]:
        return unpack('>I', data[offset:offset + 4])[0], offset + 4

    @staticmethod
    def long(value: int) -> bytes:
        return pack('>q', value)

    @staticmethod
    def read_long(data: bytes, offset: int = 0) -> Tuple[int, int]:
        return unpack('>q', data[offset:offset + 8])[0], offset + 8

    @staticmethod
    def ulong(value: int) -> bytes:
        return pack('>Q', value)

    @staticmethod
    def read_ulong(data: bytes, offset: int = 0) -> Tuple[int, int]:
        return unpack('>Q', data[offset:offset + 8])[0], offset + 8

    @staticmethod
    def float(value: float) -> bytes:
        return pack('>f', value)

    @staticmethod
    def read_float(data: bytes, offset: int = 0) -> Tuple[float, int]:
        return unpack('>f', data[offset:offset + 4])[0], offset + 4

    @staticmethod
    def double(value: float) -> bytes:
        return pack('>d', value)

    @staticmethod
    def read_double(data: bytes, offset: int = 0) -> Tuple[float, int]:
        return unpack('>d', data[offset:offset + 8])[0], offset + 8

    @staticmethod
    def string(value: str) -> bytes:
        encoded = value.encode('utf-8')
        return Packet.write_varint(len(encoded)) + encoded

    @staticmethod
    def read_string(data: bytes, offset: int = 0) -> Tuple[str, int]:
        length, offset = Packet.read_varint(data, offset)
        return data[offset:offset + length].decode('utf-8'), offset + length

    @staticmethod
    def bool(value: bool) -> bytes:
        return b'\x01' if value else b'\x00'

    @staticmethod
    def read_bool(data: bytes, offset: int = 0) -> Tuple[bool, int]:
        return data[offset] != 0, offset + 1


def compress_packet(packet_id: int, data: bytes) -> bytes:
    uncompressed = Packet.write_varint(packet_id) + data
    compressor = zlib.compressobj(level=zlib.Z_DEFAULT_COMPRESSION, wbits=15)
    compressed = compressor.compress(uncompressed)
    return compressed + compressor.flush()


def decompress_packet(compressed_data: bytes, uncompressed_size: int) -> tuple[int, bytes]:
    decompressor = zlib.decompressobj(wbits=15)
    uncompressed = decompressor.decompress(compressed_data, uncompressed_size)
    uncompressed += decompressor.flush()
    if len(uncompressed) != uncompressed_size:
        raise ValueError("Decompressed size mismatch")
    packet_id, offset = Packet.read_varint(uncompressed)
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