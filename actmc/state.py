from ast import parse
from typing import Optional
from .utils import Packet

import logging

_logger = logging.getLogger(__name__)

__all__ = ('ConnectionState',)

class ConnectionState:

    def __init__(self, host: str, port: Optional[int]):
        self.username: Optional[str] = None
        self.host: str = host
        self.port: Optional[int] = port
        self.uid: str = Optional[None]


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
        uuid, offset = Packet.read_string(data, 0)
        username, offset = Packet.read_string(data, offset)
        self.uid = uuid
        self.username = username
