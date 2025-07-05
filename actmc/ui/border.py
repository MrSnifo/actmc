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

from ..math import Vector2D

__all__ = ('WorldBorder',)

class WorldBorder:
    """
    Minecraft World Border representation and packet parser.

    Attributes
    ----------
    center: Vector2D
        Center position of the world border
    current_diameter: float
        Current diameter of the world border in blocks
    target_diameter: float
        Target diameter when lerping/resizing
    speed: int
        Time in milliseconds to reach target diameter
    portal_teleport_boundary: int
        Portal teleport boundary limit (usually 29999984)
    warning_time: int
        Warning time in seconds
    warning_blocks: int
        Warning distance in blocks
    """

    __slots__ = ('center', 'current_diameter', 'target_diameter',
                 'speed', 'portal_teleport_boundary', 'warning_time', 'warning_blocks')

    def __init__(self, center: Vector2D, current_diameter: float, target_diameter: float, speed: int,
                 portal_teleport_boundary: int,
                 warning_time: int = 15, warning_blocks: int = 5) -> None:
        self.center: Vector2D = center
        self.current_diameter: float = max(0.0, current_diameter)
        self.target_diameter: float = max(0.0, target_diameter)
        self.speed: int = max(0, speed)
        self.portal_teleport_boundary: int = portal_teleport_boundary
        self.warning_time: int = max(0, warning_time)
        self.warning_blocks: int = max(0, warning_blocks)

    @classmethod
    def from_coordinates(cls, center_x: float, center_z: float, current_diameter: float,
                         target_diameter: float, speed: int, portal_teleport_boundary: int,
                         warning_time: int = 15, warning_blocks: int = 5) -> 'WorldBorder':
        """
        Create WorldBorder from separate x and z coordinates.

        Parameters
        ----------
        center_x: float
            X coordinate of border center
        center_z: float
            Z coordinate of border center
        current_diameter: float
            Current diameter of the world border in blocks
        target_diameter: float
            Target diameter when lerping/resizing
        speed: int
            Time in milliseconds to reach target diameter
        portal_teleport_boundary: int
            Portal teleport boundary limit (usually 29999984)
        warning_time: int, optional
            Warning time in seconds (default: 15)
        warning_blocks: int, optional
            Warning distance in blocks (default: 5)

        Returns
        -------
        WorldBorder
            New WorldBorder instance
        """
        return cls(Vector2D(center_x, center_z), current_diameter, target_diameter, speed, portal_teleport_boundary,
                   warning_time, warning_blocks)

    def current_radius(self) -> float:
        """
        Get current radius of the border.

        Returns
        -------
        float
            Current radius in blocks
        """
        return self.current_diameter / 2.0

    def target_radius(self) -> float:
        """
        Get target radius of the border.

        Returns
        -------
        float
            Target radius in blocks
        """
        return self.target_diameter / 2.0

    def is_resizing(self) -> bool:
        """
        Check if border is currently resizing.

        Returns
        -------
        bool
            True if current diameter differs from target diameter
        """
        return abs(self.current_diameter - self.target_diameter) > 0.001

    def is_shrinking(self) -> bool:
        """
        Check if border is shrinking.

        Returns
        -------
        bool
            True if target diameter is smaller than current diameter
        """
        return self.target_diameter < self.current_diameter

    def is_expanding(self) -> bool:
        """
        Check if border is expanding.

        Returns
        -------
        bool
            True if target diameter is larger than current diameter
        """
        return self.target_diameter > self.current_diameter

    def distance_to_border(self, position: Vector2D) -> float:
        """
        Calculate distance from a position to the border edge.

        Parameters
        ----------
        position: Vector2D
            Position to check

        Returns
        -------
        float
            Distance to border edge (positive = inside, negative = outside)
        """
        distance_from_center = position.distance_to(self.center)
        return self.current_radius() - distance_from_center

    def distance_to_border_coords(self, coords: Vector2D) -> float:
        """
        Calculate distance from coordinates to the border edge.

        Parameters
        ----------
        coords: Vector2D
            Position coordinates to check

        Returns
        -------
        float
            Distance to border edge (positive = inside, negative = outside)
        """
        return self.distance_to_border(coords)

    def is_inside_border(self, position: Vector2D) -> bool:
        """
        Check if a position is inside the border.

        Parameters
        ----------
        position: Vector2D
            Position to check

        Returns
        -------
        bool
            True if position is inside the border
        """
        return self.distance_to_border(position) > 0

    def is_inside_border_coords(self, coords: Vector2D) -> bool:
        """
        Check if coordinates are inside the border.

        Parameters
        ----------
        coords: Vector2D
            Position coordinates to check

        Returns
        -------
        bool
            True if position is inside the border
        """
        return self.is_inside_border(coords)

    def is_in_warning_zone(self, position: Vector2D) -> bool:
        """
        Check if a position is in the warning zone.

        Parameters
        ----------
        position: Vector2D
            Position to check

        Returns
        -------
        bool
            True if position is within warning distance of border
        """
        distance_to_edge = self.distance_to_border(position)
        return 0 < distance_to_edge < self.warning_blocks

    def is_in_warning_zone_coords(self, coords: Vector2D) -> bool:
        """
        Check if coordinates are in the warning zone.

        Parameters
        ----------
        coords: Vector2D
            Position coordinates to check

        Returns
        -------
        bool
            True if position is within warning distance of border
        """
        return self.is_in_warning_zone(coords)

    def get_warning_level(self, position: Vector2D) -> float:
        """
        Get warning level for a position (0.0 to 1.0).
        Based on Notchian client warning calculation.

        Parameters
        ----------
        position: Vector2D
            Position to check

        Returns
        -------
        float
            Warning level from 0.0 (no warning) to 1.0 (maximum warning)
        """
        if self.speed > 0:
            resize_speed = abs(self.target_diameter - self.current_diameter) / (self.speed / 1000.0)
            distance = max(
                min(resize_speed * 1000 * self.warning_time, abs(self.target_diameter - self.current_diameter)),
                self.warning_blocks
            )
        else:
            distance = self.warning_blocks

        player_distance = self.distance_to_border(position)

        if player_distance < distance:
            return 1.0 - (player_distance / distance)
        else:
            return 0.0

    def get_warning_level_coords(self, coords: Vector2D) -> float:
        """
        Get warning level for coordinates (0.0 to 1.0).
        Based on Notchian client warning calculation.

        Parameters
        ----------
        coords: Vector2D
            Position coordinates to check

        Returns
        -------
        float
            Warning level from 0.0 (no warning) to 1.0 (maximum warning)
        """
        return self.get_warning_level(coords)

    def set_center(self, center: Vector2D) -> None:
        """
        Set border center position.

        Parameters
        ----------
        center: Vector2D
            New center position
        """
        self.center = center

    def set_center_coords(self, coords: Vector2D) -> None:
        """
        Set border center position from coordinates.

        Parameters
        ----------
        coords: Vector2D
            New center position coordinates
        """
        self.center = coords

    def set_size(self, diameter: float) -> None:
        """
        Set border size immediately.

        Parameters
        ----------
        diameter: float
            New diameter in blocks
        """
        diameter = max(0.0, diameter)
        self.current_diameter = diameter
        self.target_diameter = diameter
        self.speed = 0

    def lerp_size(self, old_diameter: float, new_diameter: float, speed: int) -> None:
        """
        Start border size interpolation.

        Parameters
        ----------
        old_diameter: float
            Starting diameter
        new_diameter: float
            Target diameter
        speed: int
            Time in milliseconds to reach target
        """
        self.current_diameter = max(0.0, old_diameter)
        self.target_diameter = max(0.0, new_diameter)
        self.speed = max(0, speed)

    def set_warning_time(self, warning_time: int) -> None:
        """
        Set warning time.

        Parameters
        ----------
        warning_time: int
            Warning time in seconds
        """
        self.warning_time = max(0, warning_time)

    def set_warning_blocks(self, warning_blocks: int) -> None:
        """
        Set warning distance.

        Parameters
        ----------
        warning_blocks: int
            Warning distance in blocks
        """
        self.warning_blocks = max(0, warning_blocks)

    def __repr__(self) -> str:
        """Return string representation of the world border."""
        return f"<WorldBorder center={self.center}, diameter={self.current_diameter}, target={self.target_diameter}>"
