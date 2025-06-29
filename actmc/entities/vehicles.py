from __future__ import annotations

from typing import Dict, Any

from .entity import Entity


class Boat(Entity):
    """Boat entity extending Entity."""
    __slots__ = ()

    @property
    def time_since_last_hit(self) -> int:
        """Time since last hit from metadata index 6."""
        return int(self.get_metadata_value(6, 0))

    @property
    def forward_direction(self) -> int:
        """Forward direction from metadata index 7."""
        return int(self.get_metadata_value(7, 1))

    @property
    def damage_taken(self) -> float:
        """Damage taken from metadata index 8."""
        return float(self.get_metadata_value(8, 0.0))

    @property
    def boat_type(self) -> int:
        """Boat type ID from metadata index 9."""
        return int(self.get_metadata_value(9, 0))

    @property
    def right_paddle_turning(self) -> bool:
        """Whether right paddle is turning from metadata index 10."""
        return bool(self.get_metadata_value(10, False))

    @property
    def left_paddle_turning(self) -> bool:
        """Whether left paddle is turning from metadata index 11."""
        return bool(self.get_metadata_value(11, False))

    @property
    def wood_type(self) -> str:
        """Wood type of the boat."""
        wood_types = {
            0: "oak",
            1: "spruce",
            2: "birch",
            3: "jungle",
            4: "acacia",
            5: "dark_oak"
        }
        return wood_types.get(self.boat_type, 'unknown')

    @property
    def is_paddling(self) -> bool:
        """Whether either paddle is turning."""
        return self.right_paddle_turning or self.left_paddle_turning

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class Minecart(Entity):
    """Base Minecart entity extending Entity."""
    __slots__ = ()

    @property
    def shaking_power(self) -> int:
        """Shaking power from metadata index 6."""
        return int(self.get_metadata_value(6, 0))

    @property
    def shaking_direction(self) -> int:
        """Shaking direction from metadata index 7."""
        return int(self.get_metadata_value(7, 1))

    @property
    def shaking_multiplier(self) -> float:
        """Shaking multiplier from metadata index 8."""
        return float(self.get_metadata_value(8, 0.0))

    @property
    def custom_block_id(self) -> int:
        """Custom block ID from metadata index 9."""
        return int(self.get_metadata_value(9, 0))

    @property
    def custom_block_y_position(self) -> int:
        """Custom block Y position from metadata index 10."""
        return int(self.get_metadata_value(10, 6))

    @property
    def show_custom_block(self) -> bool:
        """Whether to show custom block from metadata index 11."""
        return bool(self.get_metadata_value(11, False))

    @property
    def is_shaking(self) -> bool:
        """Whether the minecart is shaking."""
        return self.shaking_power > 0

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class MinecartContainer(Minecart):
    """Container Minecart entity extending Minecart."""
    __slots__ = ()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class MinecartHopper(MinecartContainer):
    """Hopper Minecart entity extending MinecartContainer."""
    __slots__ = ()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class MinecartChest(MinecartContainer):
    """Chest Minecart entity extending MinecartContainer."""
    __slots__ = ()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class MinecartFurnace(Minecart):
    """Furnace Minecart entity extending Minecart."""
    __slots__ = ()

    @property
    def is_powered(self) -> bool:
        """Whether furnace is powered from metadata index 12."""
        return bool(self.get_metadata_value(12, False))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class MinecartTNT(Minecart):
    """TNT Minecart entity extending Minecart."""
    __slots__ = ()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class MinecartSpawner(Minecart):
    """Spawner Minecart entity extending Minecart."""
    __slots__ = ()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}>"


class MinecartCommandBlock(Minecart):
    """Command Block Minecart entity extending Minecart."""
    __slots__ = ()

    @property
    def command(self) -> str:
        """Command string from metadata index 12."""
        return str(self.get_metadata_value(12, ""))

    @property
    def last_output(self) -> Dict[str, Any]:
        """Last output from metadata index 13."""
        return dict(self.get_metadata_value(13, {"text": ""}))

    @property
    def has_command(self) -> bool:
        """Whether the command block has a command."""
        return bool(self.command.strip())

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, position={self.position}, has_command={self.has_command}>"