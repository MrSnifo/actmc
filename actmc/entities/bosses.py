from __future__ import annotations

from typing import ClassVar, Dict
from .entity import Monster, Insentient


class Wither(Monster):
    """Wither boss entity extending Monster."""
    __slots__ = ()

    @property
    def center_head_target(self) -> int:
        """Center head target entity ID from metadata index 12."""
        return int(self.get_metadata_value(12, 0))

    @property
    def left_head_target(self) -> int:
        """Left head target entity ID from metadata index 13."""
        return int(self.get_metadata_value(13, 0))

    @property
    def right_head_target(self) -> int:
        """Right head target entity ID from metadata index 14."""
        return int(self.get_metadata_value(14, 0))

    @property
    def invulnerable_time(self) -> int:
        """Invulnerable time remaining from metadata index 15."""
        return int(self.get_metadata_value(15, 0))

    @property
    def has_center_target(self) -> bool:
        """Whether center head has a target."""
        return self.center_head_target != 0

    @property
    def has_left_target(self) -> bool:
        """Whether left head has a target."""
        return self.left_head_target != 0

    @property
    def has_right_target(self) -> bool:
        """Whether right head has a target."""
        return self.right_head_target != 0

    @property
    def is_invulnerable(self) -> bool:
        """Whether wither is in invulnerable state."""
        return self.invulnerable_time > 0

    @property
    def has_any_target(self) -> bool:
        """Whether any head has a target."""
        return self.has_center_target or self.has_left_target or self.has_right_target

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class EnderDragon(Insentient):
    """Ender Dragon boss entity extending Insentient."""
    __slots__ = ()

    # Dragon phases according to wiki
    PHASES: ClassVar[Dict[int, str]] = {
        0: "circling",
        1: "strafing",
        2: "flying_to_portal_to_land",
        3: "landing_on_portal",
        4: "taking_off_from_portal",
        5: "landed_breath_attack",
        6: "landed_looking_for_player",
        7: "landed_roar_before_breath",
        8: "charging_player",
        9: "flying_to_portal_to_die",
        10: "hovering_no_ai"
    }

    @property
    def dragon_phase(self) -> int:
        """Dragon phase ID from metadata index 12."""
        return int(self.get_metadata_value(12, 10))

    @property
    def phase_name(self) -> str:
        """Get the name of the current dragon phase."""
        return self.PHASES.get(self.dragon_phase, "unknown")

    @property
    def is_landed(self) -> bool:
        """Whether dragon is in a landed state."""
        return self.dragon_phase in {3, 5, 6, 7}

    @property
    def is_attacking(self) -> bool:
        """Whether dragon is in an attacking state."""
        return self.dragon_phase in {1, 5, 8}

    @property
    def is_dying(self) -> bool:
        """Whether dragon is in dying phase."""
        return self.dragon_phase == 9

    @property
    def is_circling(self) -> bool:
        """Whether dragon is circling."""
        return self.dragon_phase == 0

    @property
    def is_at_portal(self) -> bool:
        """Whether dragon is at or interacting with portal."""
        return self.dragon_phase in {2, 3, 4, 9}

    @property
    def has_ai_disabled(self) -> bool:
        """Whether dragon AI is disabled (hovering state)."""
        return self.dragon_phase == 10

    def __repr__(self) -> str:
        phase_str = f" ({self.phase_name})"
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}{phase_str}>"