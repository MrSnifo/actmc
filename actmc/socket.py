from __future__ import annotations

import asyncio
from .utils import Packet

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from asyncio import StreamReader, StreamWriter
    from typing import Tuple, Optional, ClassVar

import logging

_logger = logging.getLogger(__name__)

class ClientSocket:
    """
    Represents an asynchronous TCP client for establishing and managing connections.

    Attributes
    ----------
    DEFAULT_LIMIT: ClassVar[int]
        The default buffer limit (in bytes) for the asyncio StreamReader.
        Defaults to 65,536 bytes (64 KiB).

        Note
        ----
        For protocols involving large payloads (e.g., Minecraft chunk data or modded servers),
        this value may need to be increased (e.g., to 131072 or 524288) to avoid partial reads
        or buffer overflows during high-volume data transmission.

    PROTOCOL: ClassVar[int]
        The protocol version used for communication. For Minecraft, 340 corresponds to version 1.12.2.
    """
    DEFAULT_LIMIT: ClassVar[int] = 65536
    PROTOCOL: ClassVar[int] = 340

    __slots__ = ('host', 'port', 'username')

    def __init__(self, host: str, port: Optional[int]) -> None:
        self.host = host
        self.port = port

    async def connect(self) -> Tuple[StreamReader, StreamWriter]:
        return await asyncio.open_connection(host=self.host, port=self.port, limit=self.DEFAULT_LIMIT)


    @property
    def handshake_packet(self) -> bytes:
        """
        Construct the Minecraft handshake packet.

        This packet is used to initiate communication with the server and
        switch to the desired state (e.g., login or status).

        Returns
        -------
        bytes
            The encoded handshake packet, prefixed with its length as a VarInt.

        Notes
        -----
        Fields included:
        - Packet ID (0x00 for handshake)
        - Protocol version (e.g., 340)
        - Server address (hostname or IP)
        - Server port (unsigned short, big-endian)
        - Next state (2 for login, 1 for status)

        This is the first packet sent by the client and is required before
        sending login or status requests.
        """
        return (Packet.write_varint(self.PROTOCOL) + Packet.string(self.host) + Packet.short(self.port)
                + Packet.write_varint(2))
