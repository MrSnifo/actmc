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

from typing import TYPE_CHECKING
from . import utils
import asyncio

if TYPE_CHECKING:
    from asyncio import StreamReader, StreamWriter
    from typing import ClassVar, Optional, Tuple

import logging
_logger = logging.getLogger(__name__)

class TcpClient:
    """Represents an asynchronous TCP client for establishing and managing connections."""
    DEFAULT_LIMIT: ClassVar[int] = 65536
    PROTOCOL: ClassVar[int] = 340

    __slots__ = ('host', 'port')

    def __init__(self, host: str, port: Optional[int]) -> None:
        self.host = host
        self.port = port

    async def connect(self) -> Tuple[StreamReader, StreamWriter]:
        """Establish an asynchronous TCP connection to the specified host and port."""
        _logger.info(f"Connecting to {self.host}:{self.port}...")
        reader, writer = await asyncio.open_connection(
            host=self.host, port=self.port, limit=self.DEFAULT_LIMIT
        )
        _logger.info(f"Connection established to {self.host}:{self.port}")
        return reader, writer
    @property
    def build_handshake_packet(self, next_state: int = 2) -> bytes:
        """Construct the Minecraft handshake packet."""
        return (
            utils.write_varint(self.PROTOCOL) +
            utils.string(self.host) +
            utils.short(self.port) +
            utils.write_varint(next_state)
        )

    @staticmethod
    def build_login_packet(username: str) -> bytes:
        """Construct the login start packet with the given username."""
        return utils.string(username)
