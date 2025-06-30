from __future__ import annotations
from .entity import Insentient

__all__ = ('EnderDragon',)

class EnderDragon(Insentient):
    """Ender dragon entity."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:ender_dragon"

    @property
    def dragon_phase(self) -> int:
        """Dragon phase from metadata index 12.

        Returns:
            0: circling
            1: strafing (preparing to shoot fireball)
            2: flying to portal to land
            3: landing on portal
            4: taking off from portal
            5: landed, performing breath attack
            6: landed, looking for player for breath attack
            7: landed, roar before beginning breath attack
            8: charging player
            9: flying to portal to die
            10: hovering with no AI (default)
        """
        return int(self.get_metadata_value(12, 10))