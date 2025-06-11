from typing import Optional
from .tcp import TcpClient
from . import utils
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from .gateway import MinecraftSocket

import logging

_logger = logging.getLogger(__name__)

__all__ = ('ConnectionState',)

class ConnectionState:
    if TYPE_CHECKING:
        _get_socket: Callable[..., MinecraftSocket]

    def __init__(self, tcp: TcpClient):
        self.tcp: TcpClient = tcp
        self.username: Optional[str] = None
        self.uid: str = Optional[None]
        self.brand: Optional[str] = None
        self.registered_channels = []
        self.plugin_channel: Optional[str] = None
        self.teleport_id: Optional[int] = None
        self.player: Optional[None] = None

    async def send_packet(self, packet_id: int, data: bytes) -> None:
        socket = self._get_socket()

        if not socket:
            raise RuntimeError("Socket is not initialized or not connected.")

        packet_id_bytes = utils.write_varint(packet_id)
        uncompressed_payload = packet_id_bytes + data
        uncompressed_len = len(uncompressed_payload)

        if socket.compression_threshold < 0:
            # No compression
            packet_bytes = utils.write_varint(len(uncompressed_payload)) + uncompressed_payload
        else:
            if uncompressed_len < socket.compression_threshold:
                # Send uncompressed, but in compression format (VarInt 0 + data)
                data_length_bytes = utils.write_varint(0)
                payload = data_length_bytes + uncompressed_payload
            else:
                # Compress payload
                compressed_data = utils.compress_packet(packet_id, data)
                data_length_bytes = utils.write_varint(uncompressed_len)
                payload = data_length_bytes + compressed_data

            packet_bytes = utils.write_varint(len(payload)) + payload

        socket.writer.write(packet_bytes)
        await socket.writer.drain()
        _logger.debug(f"Sent packet ID 0x{packet_id:02X} with size {len(packet_bytes)} bytes")


    async def send_initial_packets(self):
        await self.send_packet(0x00, self.tcp.build_handshake_packet)
        await self.send_packet(0x00, self.tcp.build_login_packet(self.username))
        _logger.info(f"Sent handshake and login packets")

    def parse(self, packet_id: int, data: bytes) -> None:
        try:
            func = getattr(self, f'parse_0x{packet_id:02X}'.lower())
            func(data)
        except Exception as error:
            _logger.debug(f'parse_0x{packet_id:02X}'.lower())
            _logger.debug('Failed to parse event: %s', error)

    def parse_0x02(self, data: bytes) -> None:
        """
        Login Success (Packet ID: 0x02)

        Contains player's UUID (36-character string with hyphens) and username.
        Marks successful login and switches connection state to Play.
        """
        uuid, offset = utils.read_string(data, 0)
        username, offset = utils.read_string(data, offset)