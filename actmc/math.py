from __future__ import annotations
from typing import Union
import math

Number = Union[int, float]

class Vector3:
    def __init__(self, x: Number = 0.0, y: Number = 0.0, z: Number = 0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, other: Vector3) -> Vector3:
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Vector3) -> Vector3:
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: Number) -> Vector3:
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __truediv__(self, scalar: Number) -> Vector3:
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)

    def distance_to(self, other: Vector3) -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)

    def as_tuple(self) -> tuple[float, float, float]:
        return self.x, self.y, self.z

    def __repr__(self) -> str:
        return f"Vector3(x={self.x}, y={self.y}, z={self.z})"

