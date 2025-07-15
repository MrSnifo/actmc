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
import math

if TYPE_CHECKING:
    from typing import TypeVar, Union, Tuple, Iterator, List
    T = TypeVar('T', int, float, default=Union[int, float])

__all__ = ('Vector3D', 'Vector2D', 'Rotation')

class Vector3D[T]:
    """
    A generic 3D vector class supporting basic vector operations.

    Attributes
    ----------
    x: T
        X coordinate
    y: T
        Y coordinate
    z: T
        Z coordinate
    """

    __slots__ = ('x', 'y', 'z')

    def __init__(self, x: T = 0, y: T = 0, z: T = 0) -> None:
        self.x: T = x
        self.y: T = y
        self.z: T = z

    def to_floor(self) -> Vector3D[int]:
        """
        Convert each component of the vector to its floored integer value.

        Returns
        -------
        Vector3D[int]
            Vector with integer components
        """
        return Vector3D(math.floor(self.x), math.floor(self.y), math.floor(self.z))

    def to_2d(self) -> Vector2D[T]:
        """
        Convert a 3D vector to a 2D vector by removing the Y (height) component.

        Returns
        -------
        Vector2D[int]
            A 2D vector with the X and Z components of this vector
        """
        return Vector2D(self.x, self.z)

    def magnitude(self) -> float:
        """
        Calculate the magnitude (length) of the vector.

        Returns
        -------
        float
            Magnitude of the vector
        """
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def magnitude_squared(self) -> Union[int, float]:
        """
        Calculate the squared magnitude of the vector (more efficient than magnitude).

        Returns
        -------
        Union[int, float]
            Squared magnitude of the vector
        """
        return self.x * self.x + self.y * self.y + self.z * self.z

    def normalize(self) -> Vector3D[float]:
        """
        Return a normalized (unit) vector in the same direction.

        Returns
        -------
        Vector3D[float]
            Normalized vector with magnitude 1, or zero vector if original magnitude is 0
        """
        mag = self.magnitude()
        if mag == 0:
            return Vector3D(0.0, 0.0, 0.0)
        return Vector3D(self.x / mag, self.y / mag, self.z / mag)

    def distance_to(self, other: Vector3D[T]) -> float:
        """
        Calculate the Euclidean distance to another vector.

        Parameters
        ----------
        other: Vector3D[T]
            Target vector

        Returns
        -------
        float
            Distance between the two vectors
        """
        return (self - other).magnitude()

    def copy(self) -> Vector3D[T]:
        """
        Return a copy of the vector.

        Returns
        -------
        Vector3D[T]
            A new Vector3D instance with the same components.
        """
        return Vector3D(self.x, self.y, self.z)

    def dot(self, other: Vector3D[T]) -> float:
        """
        Calculate the dot product with another vector.

        Parameters
        ----------
        other : Vector3D[T]
            The other vector

        Returns
        -------
        float
            The dot product result
        """
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: Vector3D[T]) -> Vector3D[float]:
        """
        Calculate the cross product with another vector.

        Parameters
        ----------
        other : Vector3D[T]
            The other vector

        Returns
        -------
        Vector3D[float]
            The cross product result
        """
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def is_zero(self, tolerance: float = 1e-6) -> bool:
        """
        Check if vector is approximately zero within tolerance.

        Parameters
        ----------
        tolerance : float, optional
            Tolerance for zero check (default: 1e-6)

        Returns
        -------
        bool
            True if vector magnitude is below tolerance
        """
        return self.magnitude() < tolerance

    def lerp(self, other: Vector3D[T], t: float) -> Vector3D[float]:
        """
        Linear interpolation between this vector and another.

        Parameters
        ----------
        other : Vector3D[T]
            Target vector
        t : float
            Interpolation factor (0.0 = this vector, 1.0 = other vector)

        Returns
        -------
        Vector3D[float]
            Interpolated vector
        """
        return self + (other - self) * t

    def clamp_magnitude(self, max_magnitude: float) -> Vector3D[float]:
        """
        Clamp vector magnitude to maximum value.

        Parameters
        ----------
        max_magnitude : float
            Maximum allowed magnitude

        Returns
        -------
        Vector3D[float]
            Vector with clamped magnitude
        """
        mag = self.magnitude()
        if mag > max_magnitude:
            return self.normalize() * max_magnitude
        return Vector3D(float(self.x), float(self.y), float(self.z))

    def angle_to(self, other: Vector3D[T]) -> float:
        """
        Calculate the angle between this vector and another in radians.

        Parameters
        ----------
        other : Vector3D[T]
            Target vector

        Returns
        -------
        float
            Angle in radians (0 to π)
        """
        dot_product = self.dot(other)
        mag_product = self.magnitude() * other.magnitude()
        if mag_product == 0:
            return 0.0
        return math.acos(max(-1.0, min(1.0, dot_product / mag_product)))

    def project_onto(self, other: Vector3D[T]) -> Vector3D[float]:
        """
        Project this vector onto another vector.

        Parameters
        ----------
        other : Vector3D[T]
            Vector to project onto

        Returns
        -------
        Vector3D[float]
            Projected vector
        """
        other_mag_sq = other.magnitude_squared()
        if other_mag_sq == 0:
            return Vector3D(0.0, 0.0, 0.0)
        return other * (self.dot(other) / other_mag_sq)

    def reflect(self, normal: Vector3D[T]) -> Vector3D[float]:
        """
        Reflect this vector across a surface with given normal.

        Parameters
        ----------
        normal : Vector3D[T]
            Surface normal vector (should be normalized)

        Returns
        -------
        Vector3D[float]
            Reflected vector
        """
        return self - normal * (2 * self.dot(normal))

    @staticmethod
    def average(vectors: List[Vector3D[T]]) -> Vector3D[float]:
        """
        Calculate the average of multiple vectors.

        Parameters
        ----------
        vectors : List[Vector3D[T]]
            List of vectors to average

        Returns
        -------
        Vector3D[float]
            Average vector, or zero vector if list is empty
        """
        if not vectors:
            return Vector3D(0.0, 0.0, 0.0)

        count = len(vectors)
        total_x = sum(v.x for v in vectors)
        total_y = sum(v.y for v in vectors)
        total_z = sum(v.z for v in vectors)

        return Vector3D(total_x / count, total_y / count, total_z / count)

    def __eq__(self, other: Vector3D) -> bool:
        """
        Check equality with another Vector3D.

        Parameters
        ----------
        other: Vector3D
            Object to compare with

        Returns
        -------
        bool
            True if vectors are equal, False otherwise
        """
        return isinstance(other, Vector3D) and (self.x, self.y, self.z) == (other.x, other.y, other.z)

    def __hash__(self) -> int:
        """
        Return hash of the vector for use in sets and dictionaries.

        Returns
        -------
        int
            Hash value
        """
        return hash((self.x, self.y, self.z))

    def __repr__(self) -> str:
        """
        Return string representation of the vector.

        Returns
        -------
        str
            String representation
        """
        fmt = lambda n: str(int(n)) if n == int(n) else f"{n:.2f}"
        return f"<Vector3D x={fmt(self.x)}, y={fmt(self.y)}, z={fmt(self.z)}>"

    def __add__(self, other: Vector3D[T]) -> Vector3D[T]:
        """
        Add two vectors component-wise.

        Parameters
        ----------
        other: Vector3D[T]
            Vector to add

        Returns
        -------
        Vector3D[T]
            Sum of the two vectors
        """
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Vector3D[T]) -> Vector3D[T]:
        """
        Subtract two vectors component-wise.

        Parameters
        ----------
        other: Vector3D[T]
            Vector to subtract

        Returns
        -------
        Vector3D[T]
            Difference of the two vectors
        """
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: Union[int, float]) -> Vector3D[T]:
        """
        Multiply vector by a scalar.

        Parameters
        ----------
        scalar: Union[int, float]
            Scalar value to multiply by

        Returns
        -------
        Vector3D[T]
            Scaled vector
        """
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: Union[int, float]) -> Vector3D[T]:
        """
        Right multiplication by scalar (scalar * vector).

        Parameters
        ----------
        scalar: Union[int, float]
            Scalar value to multiply by

        Returns
        -------
        Vector3D[T]
            Scaled vector
        """
        return self.__mul__(scalar)

    def __truediv__(self, scalar: Union[int, float]) -> Vector3D[float]:
        """
        Divide vector by a scalar.

        Parameters
        ----------
        scalar: Union[int, float]
            Scalar value to divide by

        Returns
        -------
        Vector3D[float]
            Scaled vector

        Raises
        ------
        ZeroDivisionError
            If scalar is zero
        """
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide vector by zero")
        return Vector3D(self.x / scalar, self.y / scalar, self.z / scalar)

    def __neg__(self) -> Vector3D[T]:
        """
        Negate the vector.

        Returns
        -------
        Vector3D[T]
            Negated vector
        """
        return Vector3D(-self.x, -self.y, -self.z)

    def __iter__(self) -> Iterator[T]:
        """
        Iterate over vector components.

        Yields
        ------
        T
            Vector components (x, y, z)
        """
        yield self.x
        yield self.y
        yield self.z


class Vector2D[T]:
    """
    A generic 2D vector class supporting basic vector operations.

    Attributes
    ----------
    x: T
        X coordinate
    y: T
        Y coordinate
    """

    __slots__ = ('x', 'y')

    def __init__(self, x: T = 0, y: T = 0) -> None:
        self.x: T = x
        self.y: T = y

    def to_int(self) -> Vector2D[int]:
        """
        Convert vector components to integers using truncation.

        Returns
        -------
        Vector2D[int]
            Vector with integer components
        """
        return Vector2D(int(self.x), int(self.y))

    def magnitude(self) -> float:
        """
        Calculate the magnitude (length) of the vector.

        Returns
        -------
        float
            Magnitude of the vector
        """
        return math.sqrt(self.x * self.x + self.y * self.y)

    def magnitude_squared(self) -> Union[int, float]:
        """
        Calculate the squared magnitude of the vector (more efficient than magnitude).

        Returns
        -------
        Union[int, float]
            Squared magnitude of the vector
        """
        return self.x * self.x + self.y * self.y

    def normalize(self) -> Vector2D[float]:
        """
        Return a normalized (unit) vector in the same direction.

        Returns
        -------
        Vector2D[float]
            Normalized vector with magnitude 1, or zero vector if original magnitude is 0
        """
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0.0, 0.0)
        return Vector2D(self.x / mag, self.y / mag)

    def distance_to(self, other: Vector2D[T]) -> float:
        """
        Calculate the Euclidean distance to another vector.

        Parameters
        ----------
        other: Vector2D[T]
            Target vector

        Returns
        -------
        float
            Distance between the two vectors
        """
        return (self - other).magnitude()

    def copy(self) -> Vector2D[T]:
        """
        Return a copy of the vector.

        Returns
        -------
        Vector2D[T]
            A new Vector2D instance with the same components.
        """
        return Vector2D(self.x, self.y)

    def dot(self, other: Vector2D[T]) -> float:
        """
        Calculate the dot product with another vector.

        Parameters
        ----------
        other : Vector2D[T]
            The other vector

        Returns
        -------
        float
            The dot product result
        """
        return self.x * other.x + self.y * other.y

    def is_zero(self, tolerance: float = 1e-6) -> bool:
        """
        Check if vector is approximately zero within tolerance.

        Parameters
        ----------
        tolerance : float, optional
            Tolerance for zero check (default: 1e-6)

        Returns
        -------
        bool
            True if vector magnitude is below tolerance
        """
        return self.magnitude() < tolerance

    def lerp(self, other: Vector2D[T], t: float) -> Vector2D[float]:
        """
        Linear interpolation between this vector and another.

        Parameters
        ----------
        other : Vector2D[T]
            Target vector
        t : float
            Interpolation factor (0.0 = this vector, 1.0 = other vector)

        Returns
        -------
        Vector2D[float]
            Interpolated vector
        """
        return self + (other - self) * t

    def clamp_magnitude(self, max_magnitude: float) -> Vector2D[float]:
        """
        Clamp vector magnitude to maximum value.

        Parameters
        ----------
        max_magnitude : float
            Maximum allowed magnitude

        Returns
        -------
        Vector2D[float]
            Vector with clamped magnitude
        """
        mag = self.magnitude()
        if mag > max_magnitude:
            return self.normalize() * max_magnitude
        return Vector2D(float(self.x), float(self.y))

    @staticmethod
    def average(vectors: List[Vector2D[T]]) -> Vector2D[float]:
        """
        Calculate the average of multiple vectors.

        Parameters
        ----------
        vectors : List[Vector2D[T]]
            List of vectors to average

        Returns
        -------
        Vector2D[float]
            Average vector, or zero vector if list is empty
        """
        if not vectors:
            return Vector2D(0.0, 0.0)

        count = len(vectors)
        total_x = sum(v.x for v in vectors)
        total_y = sum(v.y for v in vectors)

        return Vector2D(total_x / count, total_y / count)

    def __eq__(self, other: Vector2D) -> bool:
        """
        Check equality with another Vector2D.

        Parameters
        ----------
        other: Vector2D
            Object to compare with

        Returns
        -------
        bool
            True if vectors are equal, False otherwise
        """
        return isinstance(other, Vector2D) and (self.x, self.y) == (other.x, other.y)

    def __hash__(self) -> int:
        """
        Return hash of the vector for use in sets and dictionaries.

        Returns
        -------
        int
            Hash value
        """
        return hash((self.x, self.y))

    def __repr__(self) -> str:
        """
        Return string representation of the vector.

        Returns
        -------
        str
            String representation
        """
        fmt = lambda n: str(int(n)) if n == int(n) else f"{n:.2f}"
        return f"<Vector2D x={fmt(self.x)}, y={fmt(self.y)}>"

    def __add__(self, other: Vector2D[T]) -> Vector2D[T]:
        """
        Add two vectors component-wise.

        Parameters
        ----------
        other: Vector2D[T]
            Vector to add

        Returns
        -------
        Vector2D[T]
            Sum of the two vectors
        """
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2D[T]) -> Vector2D[T]:
        """
        Subtract two vectors component-wise.

        Parameters
        ----------
        other: Vector2D[T]
            Vector to subtract

        Returns
        -------
        Vector2D[T]
            Difference of the two vectors
        """
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: Union[int, float]) -> Vector2D[T]:
        """
        Multiply vector by a scalar.

        Parameters
        ----------
        scalar: Union[int, float]
            Scalar value to multiply by

        Returns
        -------
        Vector2D[T]
            Scaled vector
        """
        return Vector2D(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: Union[int, float]) -> Vector2D[T]:
        """
        Right multiplication by scalar (scalar * vector).

        Parameters
        ----------
        scalar: Union[int, float]
            Scalar value to multiply by

        Returns
        -------
        Vector2D[T]
            Scaled vector
        """
        return self.__mul__(scalar)

    def __truediv__(self, scalar: Union[int, float]) -> Vector2D[float]:
        """
        Divide vector by a scalar.

        Parameters
        ----------
        scalar: Union[int, float]
            Scalar value to divide by

        Returns
        -------
        Vector2D[float]
            Scaled vector

        Raises
        ------
        ZeroDivisionError
            If scalar is zero
        """
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide vector by zero")
        return Vector2D(self.x / scalar, self.y / scalar)

    def __neg__(self) -> Vector2D[T]:
        """
        Negate the vector.

        Returns
        -------
        Vector2D[T]
            Negated vector
        """
        return Vector2D(-self.x, -self.y)

    def __iter__(self) -> Iterator[T]:
        """
        Iterate over vector components.

        Yields
        ------
        T
            Vector components (x, y)
        """
        yield self.x
        yield self.y


class Rotation:
    """
    Represents rotation with pitch and yaw angles in degrees.

    Angles are normalized to the range [-180, 180] degrees.

    Attributes
    ----------
    yaw: float
        Yaw angle in degrees, normalized to (-180, 180)
    pitch: float
        Pitch angle in degrees, normalized to (-180, 180)
    """

    __slots__ = ('yaw', 'pitch')

    def __init__(self,  yaw: float, pitch: float) -> None:
        self.yaw = self._normalize_angle(float(yaw))
        self.pitch = self._normalize_angle(float(pitch))


    @staticmethod
    def _normalize_angle(angle: float) -> float:
        """
        Normalize angle to the range (-180, 180) degrees.

        Parameters
        ----------
        angle: float
            Angle in degrees

        Returns
        -------
        float
            Normalized angle in degrees
        """
        while angle > 180:
            angle -= 360
        while angle <= -180:
            angle += 360
        return angle

    def to_radians(self) -> Tuple[float, float]:
        """
        Convert angles to radians.

        Returns
        -------
        Tuple[float, float]
            Tuple of (pitch_radians, yaw_radians)
        """
        return math.radians(self.pitch), math.radians(self.yaw)

    def to_degrees(self) -> Tuple[float, float]:
        """
        Get angles in degrees.

        Returns
        -------
        Tuple[float, float]
            Tuple of (pitch_degrees, yaw_degrees)
        """
        return self.pitch, self.yaw

    @classmethod
    def from_radians(cls, pitch_radians: float, yaw_radians: float) -> Rotation:
        """
        Create a Rotation from angles in radians.

        Parameters
        ----------
        pitch_radians: float
            Pitch angle in radians
        yaw_radians: float
            Yaw angle in radians

        Returns
        -------
        Rotation
            New Rotation instance
        """
        return cls(math.degrees(pitch_radians), math.degrees(yaw_radians))

    def copy(self) -> Rotation:
        """
        Return a copy of the rotation.

        Returns
        -------
        Rotation
            A new Rotation instance with the same yaw and pitch.
        """
        return Rotation(self.yaw, self.pitch)

    def __add__(self, other: Rotation) -> Rotation:
        """
        Add two rotations.

        Parameters
        ----------
        other: Rotation
            Rotation to add

        Returns
        -------
        Rotation
            Sum of the two rotations
        """
        return Rotation(self.yaw + other.yaw, self.pitch + other.pitch)

    def __sub__(self, other: Rotation) -> Rotation:
        """
        Subtract two rotations.

        Parameters
        ----------
        other: Rotation
            subtract

        Returns
        -------
        Rotation
            Difference of the two rotations
        """
        return Rotation(self.yaw - other.yaw, self.pitch - other.pitch,)

    def __mul__(self, scalar: Union[int, float]) -> Rotation:
        """
        Multiply rotation by a scalar.

        Parameters
        ----------
        scalar: Union[int, float]
            Scalar value to multiply by

        Returns
        -------
        Rotation
            Scaled rotation
        """
        return Rotation(self.yaw * scalar, self.pitch * scalar)

    def __eq__(self, other: object) -> bool:
        """
        Check equality with another Rotation.

        Parameters
        ----------
        other: object
            Object to compare with

        Returns
        -------
        bool
            True if rotations are equal, False otherwise
        """
        return (isinstance(other, Rotation) and
                self.pitch == other.pitch and
                self.yaw == other.yaw)

    def __repr__(self) -> str:
        """
        Return detailed string representation of the rotation.

        Returns
        -------
        str
            String representation
        """
        fmt = lambda n: str(int(n)) if n == int(n) else f"{n:.2f}"
        return f"<Rotation yaw={fmt(self.yaw)}, pitch={fmt(self.pitch)}>"