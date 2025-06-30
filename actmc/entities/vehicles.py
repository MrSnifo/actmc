from __future__ import annotations

from .entity import Entity

__all__ = ('Boat', 'Minecart', 'MinecartRideable', 'MinecartContainer', 'MinecartChest', 'MinecartHopper',
           'MinecartFurnace', 'MinecartTNT', 'MinecartSpawner', 'MinecartCommandBlock')

class Boat(Entity):
    """Boat entity for water transportation. """
    __slots__ = ()
    ENTITY_TYPE = "minecraft:boat"

    @property
    def time_since_last_hit(self) -> int:
        """
        Time since last hit in ticks.

        Returns
        -------
        int
            Time since last hit from metadata index 6, default 0
        """
        return int(self.get_metadata_value(6, 0))

    @property
    def forward_direction(self) -> int:
        """
        Forward direction of the boat.

        Returns
        -------
        int
            Forward direction from metadata index 7, default 1
        """
        return int(self.get_metadata_value(7, 1))

    @property
    def damage_taken(self) -> float:
        """
        Damage taken by the boat.

        Returns
        -------
        float
            Damage taken from metadata index 8, default 0.0
        """
        return float(self.get_metadata_value(8, 0.0))

    @property
    def boat_type(self) -> int:
        """
        Type of boat wood.

        Returns
        -------
        int
            Boat type from metadata index 9 (0=oak, 1=spruce, 2=birch,
            3=jungle, 4=acacia, 5=dark oak), default 0
        """
        return int(self.get_metadata_value(9, 0))

    @property
    def right_paddle_turning(self) -> bool:
        """
        Whether right paddle is turning.

        Returns
        -------
        bool
            Right paddle state from metadata index 10, default False
        """
        return bool(self.get_metadata_value(10, False))

    @property
    def left_paddle_turning(self) -> bool:
        """
        Whether left paddle is turning.

        Returns
        -------
        bool
            Left paddle state from metadata index 11, default False
        """
        return bool(self.get_metadata_value(11, False))

    @property
    def wood_type_name(self) -> str:
        """
        Human-readable name of the boat wood type.

        Returns
        -------
        str
            Wood type name corresponding to boat_type value
        """
        wood_types = {
            0: "oak",
            1: "spruce",
            2: "birch",
            3: "jungle",
            4: "acacia",
            5: "dark_oak"
        }
        return wood_types.get(self.boat_type, "oak")

class Minecart(Entity):
    """Base minecart entity for rail transportation."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:minecart"

    @property
    def shaking_power(self) -> int:
        """
        Power of minecart shaking.

        Returns
        -------
        int
            Shaking power from metadata index 6, default 0
        """
        return int(self.get_metadata_value(6, 0))

    @property
    def shaking_direction(self) -> int:
        """
        Direction of minecart shaking.

        Returns
        -------
        int
            Shaking direction from metadata index 7, default 1
        """
        return int(self.get_metadata_value(7, 1))

    @property
    def shaking_multiplier(self) -> float:
        """
        Multiplier for minecart shaking effect.

        Returns
        -------
        float
            Shaking multiplier from metadata index 8, default 0.0
        """
        return float(self.get_metadata_value(8, 0.0))

    @property
    def custom_block_id(self) -> int:
        """
        Custom block ID and damage value.

        Returns
        -------
        int
            Custom block ID from metadata index 9, default 0
        """
        return int(self.get_metadata_value(9, 0))

    @property
    def custom_block_y_position(self) -> int:
        """
        Custom block Y position in 16ths of a block.

        Returns
        -------
        int
            Custom block Y position from metadata index 10, default 6
        """
        return int(self.get_metadata_value(10, 6))

    @property
    def show_custom_block(self) -> bool:
        """
        Whether to show custom block instead of default.

        Returns
        -------
        bool
            Show custom block flag from metadata index 11, default False
        """
        return bool(self.get_metadata_value(11, False))

    @property
    def is_shaking(self) -> bool:
        """
        Whether minecart is currently shaking.

        Returns
        -------
        bool
            True if shaking_power > 0
        """
        return self.shaking_power > 0

class MinecartRideable(Minecart):
    """Rideable minecart that can carry passengers."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:minecart"

class MinecartContainer(Minecart):
    """Base class for minecarts that can store items."""
    __slots__ = ()

class MinecartChest(MinecartContainer):
    """Chest minecart for item storage and transportation."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:chest_minecart"

class MinecartHopper(MinecartContainer):
    """Hopper minecart for item collection and transportation."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:hopper_minecart"

class MinecartFurnace(Minecart):
    """Furnace minecart for self-propelled transportation."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:furnace_minecart"

    @property
    def is_powered(self) -> bool:
        """Whether furnace minecart is currently powered."""
        return bool(self.get_metadata_value(12, False))

class MinecartTNT(Minecart):
    """TNT minecart for explosive transportation."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:tnt_minecart"

class MinecartSpawner(Minecart):
    """Spawner minecart for mobile mob spawning."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:spawner_minecart"

class MinecartCommandBlock(Minecart):
    """Command block minecart for mobile command execution."""
    __slots__ = ()
    ENTITY_TYPE = "minecraft:commandblock_minecart"

    @property
    def command(self) -> str:
        """
        Command string to execute.

        Returns
        -------
        str
            Command from metadata index 12, default empty string
        """
        return str(self.get_metadata_value(12, ""))

    @property
    def last_output(self) -> str:
        """
        Last command output as chat component.

        Returns
        -------
        str
            Last output from metadata index 13, default '{"text":""}'
        """
        return str(self.get_metadata_value(13, '{"text":""}'))