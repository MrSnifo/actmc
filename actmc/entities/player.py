from __future__ import annotations

from typing import Any, Optional


from .entity import Living


class Player(Living):
    """Player entity extending Living."""
    __slots__ = ()

    @property
    def additional_hearts(self) -> float:
        """Additional hearts from metadata index 11."""
        return float(self.get_metadata_value(11, 0.0))

    @property
    def score(self) -> int:
        """Player score from metadata index 12."""
        return int(self.get_metadata_value(12, 0))

    @property
    def displayed_skin_parts(self) -> int:
        """Displayed skin parts bit mask from metadata index 13."""
        return int(self.get_metadata_value(13, 0))

    @property
    def main_hand(self) -> int:
        """Main hand preference from metadata index 14 (0=left, 1=right)."""
        return int(self.get_metadata_value(14, 1))

    @property
    def left_shoulder_entity(self) -> Optional[Any]:
        """Left shoulder entity NBT data from metadata index 15."""
        return self.get_metadata_value(15)

    @property
    def right_shoulder_entity(self) -> Optional[Any]:
        """Right shoulder entity NBT data from metadata index 16."""
        return self.get_metadata_value(16)

    @property
    def cape_enabled(self) -> bool:
        """Whether cape is enabled (bit 0)."""
        return bool(self.displayed_skin_parts & 0x01)

    @property
    def jacket_enabled(self) -> bool:
        """Whether jacket is enabled (bit 1)."""
        return bool(self.displayed_skin_parts & 0x02)

    @property
    def left_sleeve_enabled(self) -> bool:
        """Whether left sleeve is enabled (bit 2)."""
        return bool(self.displayed_skin_parts & 0x04)

    @property
    def right_sleeve_enabled(self) -> bool:
        """Whether right sleeve is enabled (bit 3)."""
        return bool(self.displayed_skin_parts & 0x08)

    @property
    def left_pants_leg_enabled(self) -> bool:
        """Whether left pants leg is enabled (bit 4)."""
        return bool(self.displayed_skin_parts & 0x10)

    @property
    def right_pants_leg_enabled(self) -> bool:
        """Whether right pants leg is enabled (bit 5)."""
        return bool(self.displayed_skin_parts & 0x20)

    @property
    def hat_enabled(self) -> bool:
        """Whether hat is enabled (bit 6)."""
        return bool(self.displayed_skin_parts & 0x40)

    @property
    def is_left_handed(self) -> bool:
        """Whether player is left-handed (main hand = 0)."""
        return self.main_hand == 0

    @property
    def is_right_handed(self) -> bool:
        """Whether player is right-handed (main hand = 1)."""
        return self.main_hand == 1

    @property
    def has_left_shoulder_parrot(self) -> bool:
        """Whether player has a parrot on left shoulder."""
        return self.left_shoulder_entity is not None

    @property
    def has_right_shoulder_parrot(self) -> bool:
        """Whether player has a parrot on right shoulder."""
        return self.right_shoulder_entity is not None

    def __repr__(self) -> str:
        return f"<Player id={self.id}, position={self.position}>"