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

if TYPE_CHECKING:
    from typing import List, Optional
    from .chat import Message

__all__ = ('Property', 'PlayerInfo')

class Property:
    """
    Represents a player property such as skin or cape data.

    Attributes
    ----------
    name: str
        The property name.
    value: str
        Base64-encoded property value.
    signature: Optional[str]
        Cryptographic signature.
    """
    __slots__ = ('name', 'value', 'signature')

    def __init__(self, name: str, value: str, signature: Optional[str]) -> None:
        self.name = name
        self.value = value
        self.signature = signature

    @property
    def is_signed(self) -> bool:
        """
        Whether this property has a cryptographic signature.

        Returns
        -------
        bool
            True if signature is present.
        """
        return self.signature is not None

    def __repr__(self) -> str:
        return f"<Property name={self.name}, is_signed={self.is_signed}>"

class PlayerInfo:
    """
    Represents a player from the server's player list (tab list).

    Attributes
    ----------
    name: str
        The player's username.
    properties: List[Property]
        Player properties (skin, cape data, etc.).
    gamemode: int
        Game mode ID.

        - 0: Survival mode

        - 1: Creative mode

        - 2: Adventure mode

        - 3: Spectator mode
    ping: int
        Network latency in milliseconds.
    display_name: Optional[Message]
        Custom display name with formatting.
    """
    __slots__ = ('name', 'properties', 'gamemode', 'ping', 'display_name')

    def __init__(self,
                 name: str,
                 properties: List[Property],
                 gamemode: int,
                 ping: int,
                 display_name: Optional[Message]) -> None:
        self.name: str = name
        self.properties: List[Property] = properties
        self.gamemode: int = gamemode
        self.ping: int = ping
        self.display_name: Optional[Message] = display_name

    def get_property(self, name: str) -> Optional[Property]:
        """
        Get a property by name.

        Parameters
        ----------
        name: str
            The property name to search for.

        Returns
        -------
        Property or None
            The matching property, or None if not found.
        """
        for prop in self.properties:
            if prop.name == name:
                return prop
        return None

    @property
    def has_skin(self) -> bool:
        """
        Whether player has skin data.

        Returns
        -------
        bool
            True if player has skin textures property.
        """
        return self.get_property("textures") is not None

    def __repr__(self) -> str:
        return f"<PlayerInfo name={self.name}, ping={self.ping}, gamemode={self.gamemode}>"
