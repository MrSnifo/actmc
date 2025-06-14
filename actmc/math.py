import math
from typing import Tuple

class Vector3D:
    """Represents a 3D vector with X, Y, Z components."""

    def __init__(self, x: float, y: float, z: float):
        """Initialize vector with X, Y, Z components."""
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def magnitude(self) -> float:
        """Calculate the magnitude of the vector."""
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5

    def normalize(self) -> 'Vector3D':
        """Return a normalized version of this vector."""
        mag = self.magnitude()
        if mag == 0:
            return Vector3D(0, 0, 0)
        return Vector3D(self.x / mag, self.y / mag, self.z / mag)

    def __add__(self, other: 'Vector3D') -> 'Vector3D':
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: 'Vector3D') -> 'Vector3D':
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> 'Vector3D':
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def __str__(self) -> str:
        return f"Vector3D(x={self.x}, y={self.y}, z={self.z})"

    def __repr__(self) -> str:
        return self.__str__()

    def as_int_tuple(self) -> Tuple[int, int, int]:
        return int(self.x), int(self.y), int(self.z)

    def as_float_tuple(self) -> Tuple[float, float, float]:
        return float(self.x), float(self.y), float(self.z)

class Rotation:
    """Represents rotation with pitch and yaw angles."""

    def __init__(self, pitch_angle: float, yaw_angle: float):
        """Initialize rotation with pitch and yaw angles in degrees."""
        self.pitch_angle = self._normalize_angle(float(pitch_angle))
        self.yaw_angle = self._normalize_angle(float(yaw_angle))

    @staticmethod
    def _normalize_angle(angle: float) -> float:
        """Normalize angle to [-180, 180] range."""
        while angle > 180:
            angle -= 360
        while angle <= -180:
            angle += 360
        return angle

    def to_radians(self) -> tuple[float, float]:
        """Convert angles to radians."""
        return math.radians(self.pitch_angle), math.radians(self.yaw_angle)

    def __str__(self) -> str:
        return f"Rotation(pitch={self.pitch_angle}°, yaw={self.yaw_angle}°)"

    def __repr__(self) -> str:
        return self.__str__()