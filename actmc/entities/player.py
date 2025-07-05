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
from .entity import Living

if TYPE_CHECKING:
    from typing import Any, ClassVar, Optional, Tuple, Dict
    from ..math import Vector3D, Rotation
    from ..ui import tab

__all__ = ('Player',)


class Player(Living):
    """
    Player entity extending Living.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for players.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the player.
    """

    __slots__ = ('_tablist',)

    def __init__(self,
                 entity_id: int,
                 uuid: str,
                 position: Vector3D[float],
                 rotation: Rotation,
                 metadata: Dict[int, Any],
                 tablist: Dict[str, Optional[tab.PlayerInfo]]) -> None:
        super().__init__(entity_id, uuid, position, rotation, metadata)
        self._tablist: Dict[str, Optional[tab.PlayerInfo]] = tablist

    ENTITY_TYPE: ClassVar[str] = 'minecraft:player'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.6, 1.8)

    @property
    def info(self) -> Optional[tab.PlayerInfo]:
        """
        Get additional player information from the server's tab list.

        Returns
        -------
        Optional[tab.TabPlayer]
            The player's tab list entry if they are currently online and
            visible in the tab list, None otherwise.
        """
        return self._tablist.get(self.uuid)

    @property
    def additional_hearts(self) -> float:
        """
        Additional hearts.

        Returns
        -------
        float
            The number of additional hearts the player has.
        """
        return float(self.get_metadata_value(11, 0.0))

    @property
    def score(self) -> int:
        """
        Player score.

        Returns
        -------
        int
            The player's current score.
        """
        return int(self.get_metadata_value(12, 0))

    @property
    def displayed_skin_parts(self) -> int:
        """
        Displayed skin parts bit mask.

        Returns
        -------
        int
            Bit mask representing which skin parts are displayed.
        """
        return int(self.get_metadata_value(13, 0))

    @property
    def main_hand(self) -> int:
        """
        Main hand preference.

        Returns
        -------
        int
            The main hand preference (0=left, 1=right).
        """
        return int(self.get_metadata_value(14, 1))

    @property
    def left_shoulder_entity(self) -> Optional[Any]:
        """
        Left shoulder entity NBT data.

        Returns
        -------
        Optional[Any]
            NBT data of the entity on the left shoulder, or None if empty.
        """
        return self.get_metadata_value(15)

    @property
    def right_shoulder_entity(self) -> Optional[Any]:
        """
        Right shoulder entity NBT data.

        Returns
        -------
        Optional[Any]
            NBT data of the entity on the right shoulder, or None if empty.
        """
        return self.get_metadata_value(16)

    @property
    def cape_enabled(self) -> bool:
        """
        Whether cape is enabled (bit 0).

        Returns
        -------
        bool
            True if the cape is enabled, False otherwise.
        """
        return bool(self.displayed_skin_parts & 0x01)

    @property
    def jacket_enabled(self) -> bool:
        """
        Whether jacket is enabled (bit 1).

        Returns
        -------
        bool
            True if the jacket is enabled, False otherwise.
        """
        return bool(self.displayed_skin_parts & 0x02)

    @property
    def left_sleeve_enabled(self) -> bool:
        """
        Whether left sleeve is enabled (bit 2).

        Returns
        -------
        bool
            True if the left sleeve is enabled, False otherwise.
        """
        return bool(self.displayed_skin_parts & 0x04)

    @property
    def right_sleeve_enabled(self) -> bool:
        """
        Whether right sleeve is enabled (bit 3).

        Returns
        -------
        bool
            True if the right sleeve is enabled, False otherwise.
        """
        return bool(self.displayed_skin_parts & 0x08)

    @property
    def left_pants_leg_enabled(self) -> bool:
        """
        Whether left pants leg is enabled (bit 4).

        Returns
        -------
        bool
            True if the left pants leg is enabled, False otherwise.
        """
        return bool(self.displayed_skin_parts & 0x10)

    @property
    def right_pants_leg_enabled(self) -> bool:
        """
        Whether right pants leg is enabled (bit 5).

        Returns
        -------
        bool
            True if the right pants leg is enabled, False otherwise.
        """
        return bool(self.displayed_skin_parts & 0x20)

    @property
    def hat_enabled(self) -> bool:
        """
        Whether hat is enabled (bit 6).

        Returns
        -------
        bool
            True if the hat is enabled, False otherwise.
        """
        return bool(self.displayed_skin_parts & 0x40)

    @property
    def is_left_handed(self) -> bool:
        """
        Whether player is left-handed (main hand = 0).

        Returns
        -------
        bool
            True if the player is left-handed, False otherwise.
        """
        return self.main_hand == 0

    @property
    def is_right_handed(self) -> bool:
        """
        Whether player is right-handed (main hand = 1).

        Returns
        -------
        bool
            True if the player is right-handed, False otherwise.
        """
        return self.main_hand == 1

    @property
    def has_left_shoulder_parrot(self) -> bool:
        """
        Whether player has a parrot on left shoulder.

        Returns
        -------
        bool
            True if there's an entity on the left shoulder, False otherwise.
        """
        return self.left_shoulder_entity is not None

    @property
    def has_right_shoulder_parrot(self) -> bool:
        """
        Whether player has a parrot on right shoulder.

        Returns
        -------
        bool
            True if there's an entity on the right shoulder, False otherwise.
        """
        return self.right_shoulder_entity is not None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, health={self.health}, score={self.score}>"