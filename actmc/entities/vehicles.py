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
from .entity import Entity

if TYPE_CHECKING:
    from typing import ClassVar, Tuple

__all__ = (
    'Boat', 'Minecart', 'MinecartRideable', 'MinecartContainer', 'MinecartChest', 'MinecartHopper',
    'MinecartFurnace', 'MinecartTNT', 'MinecartSpawner', 'MinecartCommandBlock'
)


class Boat(Entity):
    """
    Boat entity for water transportation.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for boats.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the boat.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:boat'
    BOUNDING: ClassVar[Tuple[float, float]] = (1.375, 0.5625)

    @property
    def time_since_last_hit(self) -> int:
        """
        Time since last hit in ticks.

        Returns
        -------
        int
            Time since last hit.
        """
        return int(self.get_metadata_value(6, 0))

    @property
    def forward_direction(self) -> int:
        """
        Forward direction of the boat.

        Returns
        -------
        int
            Forward direction, default 1.
        """
        return int(self.get_metadata_value(7, 1))

    @property
    def damage_taken(self) -> float:
        """
        Damage taken by the boat.

        Returns
        -------
        float
            Damage taken.
        """
        return float(self.get_metadata_value(8, 0.0))

    @property
    def boat_type(self) -> int:
        """
        Type of boat wood.

        Returns
        -------
        int
            Boat type (0=oak, 1=spruce, 2=birch, 3=jungle, 4=acacia, 5=dark oak)
        """
        return int(self.get_metadata_value(9, 0))

    @property
    def right_paddle_turning(self) -> bool:
        """
        Whether right paddle is turning.

        Returns
        -------
        bool
            Right paddle state.
        """
        return bool(self.get_metadata_value(10, False))

    @property
    def left_paddle_turning(self) -> bool:
        """
        Whether left paddle is turning.

        Returns
        -------
        bool
            Left paddle state.
        """
        return bool(self.get_metadata_value(11, False))

    @property
    def wood_type_name(self) -> str:
        """
        Human-readable name of the boat wood type.

        Returns
        -------
        str
            Wood type name corresponding to boat_type value.
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
    """
    Base minecart entity for rail transportation.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for minecarts.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the minecart.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:minecart'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.98, 0.7)

    @property
    def shaking_power(self) -> int:
        """
        Power of minecart shaking.

        Returns
        -------
        int
            Shaking power.
        """
        return int(self.get_metadata_value(6, 0))

    @property
    def shaking_direction(self) -> int:
        """
        Direction of minecart shaking.

        Returns
        -------
        int
            Shaking direction, default 1.
        """
        return int(self.get_metadata_value(7, 1))

    @property
    def shaking_multiplier(self) -> float:
        """
        Multiplier for minecart shaking effect.

        Returns
        -------
        float
            Shaking multiplier.
        """
        return float(self.get_metadata_value(8, 0.0))

    @property
    def custom_block_id(self) -> int:
        """
        Custom block ID and damage value.

        Returns
        -------
        int
            Custom block ID.
        """
        return int(self.get_metadata_value(9, 0))

    @property
    def custom_block_y_position(self) -> int:
        """
        Custom block Y position in 16ths of a block.

        Returns
        -------
        int
            Custom block Y position, default 6.
        """
        return int(self.get_metadata_value(10, 6))

    @property
    def show_custom_block(self) -> bool:
        """
        Whether to show custom block instead of default.

        Returns
        -------
        bool
            Show custom block flag.
        """
        return bool(self.get_metadata_value(11, False))

    @property
    def is_shaking(self) -> bool:
        """
        Whether minecart is currently shaking.

        Returns
        -------
        bool
            True if shaking_power > 0.
        """
        return self.shaking_power > 0


class MinecartRideable(Minecart):
    """
    Rideable minecart that can carry passengers.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for rideable minecarts.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the rideable minecart.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:minecart'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.98, 0.7)


class MinecartContainer(Minecart):
    """
    Base class for minecarts that can store items.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height).
    """

    __slots__ = ()


class MinecartChest(MinecartContainer):
    """
    Chest minecart for item storage and transportation.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for chest minecarts.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the chest minecart.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:chest_minecart'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.98, 0.7)


class MinecartHopper(MinecartContainer):
    """
    Hopper minecart for item collection and transportation.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for hopper minecarts.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the hopper minecart.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:hopper_minecart'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.98, 0.7)


class MinecartFurnace(Minecart):
    """
    Furnace minecart for self-propelled transportation.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for furnace minecarts.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the furnace minecart.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:furnace_minecart'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.98, 0.7)

    @property
    def is_powered(self) -> bool:
        """
        Whether furnace minecart is currently powered.

        Returns
        -------
        bool
            True if the furnace minecart is powered, False otherwise.
        """
        return bool(self.get_metadata_value(12, False))


class MinecartTNT(Minecart):
    """
    TNT minecart for explosive transportation.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for TNT minecarts.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the TNT minecart.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:tnt_minecart'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.98, 0.7)


class MinecartSpawner(Minecart):
    """
    Spawner minecart for mobile mob spawning.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for spawner minecarts.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the spawner minecart.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:spawner_minecart'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.98, 0.7)


class MinecartCommandBlock(Minecart):
    """
    Command block minecart for mobile command execution.

    Attributes
    ----------
    ENTITY_TYPE: ClassVar[str]
        The Minecraft entity type identifier for command block minecarts.
    BOUNDING: ClassVar[Tuple[float, float]]
        The bounding box dimensions (width/depth, height) of the command block minecart.
    """

    __slots__ = ()

    ENTITY_TYPE: ClassVar[str] = 'minecraft:commandblock_minecart'
    BOUNDING: ClassVar[Tuple[float, float]] = (0.98, 0.7)

    @property
    def command(self) -> str:
        """
        Command string to execute.

        Returns
        -------
        str
            Command.
        """
        return str(self.get_metadata_value(12, ""))

    @property
    def last_output(self) -> str:
        """
        Last command output as chat component.

        Returns
        -------
        str
            Last output, default '{"text":""}'.
        """
        return str(self.get_metadata_value(13, '{"text":""}'))