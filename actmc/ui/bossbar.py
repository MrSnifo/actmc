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

__all__ = ('BossBar',)

class BossBar:
    """
    Minecraft Boss Bar representation and packet parser.
    
    Attributes
    ----------
    uuid: str
        Unique identifier for this boss bar
    title: str
        Current display title
    health: float
        Current health value (0.0 to 1.0)
    color: int
        Current color ID (0-6)
        - 0: Pink, 1: Blue, 2: Red, 3: Green, 4: Yellow, 5: Purple, 6: White
    division: int
        Current division type (0-4)
        - 0: No division, 1: 6 notches, 2: 10 notches, 3: 12 notches, 4: 20 notches
    flags: int
        Current flag bits
        - 0x1: Darken sky, 0x2: Dragon bar (plays end music)
    """

    __slots__ = ('uuid', 'title', 'health', 'color', 'division', 'flags')

    def __init__(self, bar_uuid: str, title: str, health: float, color: int, division: int, flags: int) -> None:
        self.uuid: str = bar_uuid
        self.title: str = title
        self.health: float = max(0.0, min(1.0, health))
        self.color: int = color 
        self.division: int = division 
        self.flags: int = flags

    def health_percentage(self) -> int:
        """
        Get health as percentage.

        Returns
        -------
        int
            Health value as percentage (0-100)
        """
        return int(self.health * 100)

    def darken_sky(self) -> bool:
        """
        Check if sky darkening is enabled.

        Returns
        -------
        bool
            True if darken sky.
        """
        return bool(self.flags & 0x1)

    def is_dragon_bar(self) -> bool:
        """
        Check if this is a dragon boss bar.

        Returns
        -------
        bool
            True if dragon bar flag (0x2) is set
        """
        return bool(self.flags & 0x2)

    def is_visible(self) -> bool:
        """
        Check if boss bar should be visible.

        Returns
        -------
        bool
            True if health is greater than 0
        """
        return self.health > 0.0

    def __eq__(self, other) -> bool:
        if not isinstance(other, BossBar):
            return False
        return self.uuid == other.uuid

    def __repr__(self) -> str:
        return f"<BossBar uuid={self.uuid}, title='{self.title}', health={self.health:.2f}>"