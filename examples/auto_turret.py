from actmc.entities import Entity, Living, Player, Monster
from actmc import Client, Vector3D, Rotation
from actmc.utils import calculate_rotation
from typing import Optional, List
from actmc.ext import tasks
from actmc.ui import Window
import asyncio
import math
import time


class AutoTurret(Client):
    """
    Automated turret system for Minecraft that tracks and shoots at targets.

    Parameters
    ----------
    username: str
        Bot username
    range_distance: float
        Maximum targeting range in blocks
    whitelist: Optional[List[str]], default=None
        Player names to never target. None = no players, [] = all players
    target_all: bool
        Target all living entities vs monsters only

    Notes
    -----
    - Requires bow and arrows in inventory to operate.
    - The bow will be automatically equipped when shooting.
    - Accuracy may be reduced if the target is at a lower elevation.
    """

    def __init__(self, username: str, range_distance: float, whitelist: Optional[List[str]] = None,
                 target_all: bool = False) -> None:
        super().__init__(username)
        # Targeting config
        self.range_distance = range_distance
        self.whitelist = whitelist
        self.target_all = target_all
        # Target tracking
        self.target: Optional[Living] = None
        self.target_velocities: List[Vector3D] = []
        self.last_target_pos: Optional[Vector3D] = None
        # Shooting state
        self.last_shot_time = 0.0
        self.shot_cooldown = 0.7
        self.is_shooting = False
        # Aiming mechanics
        self.aim_smoothing = 0.4
        self.last_rotation: Optional[Rotation] = None
        # Physics settings
        self.gravity = 0.05
        self.base_arrow_speed = 3.0
        self.eye_height = 1.62

    def _is_valid_target(self, entity: Entity) -> bool:
        """Check if entity is a valid target."""
        if not isinstance(entity, Living) or entity.id == self.user.id:
            return False

        # Player targeting logic
        if isinstance(entity, Player):
            if self.whitelist is None:
                return False
            if len(self.whitelist) == 0:
                return True
            return not entity.info or entity.info.name.lower() not in self.whitelist

        # Non-player targeting
        return self.target_all or isinstance(entity, Monster)

    def _get_target_velocity(self) -> Vector3D:
        """Average recent velocities of the target for predictive aiming."""
        if len(self.target_velocities) < 2:
            return Vector3D(0, 0, 0)

        recent = self.target_velocities[-3:]
        return Vector3D(
            sum(v.x for v in recent) / len(recent),
            sum(v.y for v in recent) / len(recent),
            sum(v.z for v in recent) / len(recent)
        )

    @staticmethod
    def _get_charge_time(distance: float) -> float:
        """Get dynamic arrow charge time based on distance."""
        if distance <= 2:
            return 0.2
        if distance <= 7:
            return 0.4
        return 0.7 if distance > 15 else 0.5 + (distance - 5) * 0.02

    def _calculate_shot_angle(self, target_pos: Vector3D, charge_time: float) -> Optional[float]:
        """Calculate the pitch angle required to hit the target."""
        charge_factor = min(1.0, max(0.3, charge_time))
        arrow_speed = self.base_arrow_speed * charge_factor

        dx = target_pos.x - self.user.position.x
        dz = target_pos.z - self.user.position.z
        dy = (target_pos.y + 0.5) - (self.user.position.y + self.eye_height)
        horizontal_dist = math.hypot(dx, dz)

        if horizontal_dist == 0 or horizontal_dist > self.range_distance:
            return math.degrees(math.atan2(-dy, horizontal_dist))

        v2 = arrow_speed ** 2
        disc = v2 ** 2 - self.gravity * (self.gravity * horizontal_dist ** 2 + 2 * dy * v2)

        if disc >= 0:
            return math.degrees(-math.atan((v2 - math.sqrt(disc)) / (self.gravity * horizontal_dist)))
        else:
            return math.degrees(math.atan2(-dy, horizontal_dist))

    def _predict_target_position(self, target: Living) -> Vector3D:
        """Predict where the target will be after some time based on velocity."""
        velocity = self._get_target_velocity()
        return target.position + velocity if velocity.magnitude() >= 0.1 else target.position.copy()

    def _smooth_rotation(self, new_rotation: Rotation) -> Rotation:
        """Smooth the aiming transition to reduce jitter."""
        if not self.last_rotation:
            self.last_rotation = new_rotation
            return new_rotation

        yaw_diff = (new_rotation.yaw - self.last_rotation.yaw + 540) % 360 - 180
        smooth_yaw = self.last_rotation.yaw + yaw_diff * self.aim_smoothing
        smooth_pitch = self.last_rotation.pitch + (new_rotation.pitch - self.last_rotation.pitch) * self.aim_smoothing
        self.last_rotation = Rotation(yaw=smooth_yaw, pitch=smooth_pitch)
        return self.last_rotation

    @tasks.ticks(tps=10)
    async def aim_and_track(self) -> None:
        """Continuously track and aim at the closest valid target."""
        enemies = [e for e in self.entities.values() if self._is_valid_target(e)]
        if not enemies:
            self.target = None
            return

        closest = min(enemies, key=lambda e: e.position.distance_to(self.user.position))
        distance = closest.position.distance_to(self.user.position)

        if distance > self.range_distance:
            self.target = None
            return

        # Update target
        if self.target != closest:
            self.target = closest
            self.target_velocities.clear()
            self.last_target_pos = None
            print(f"[Target] {closest.__class__.__name__}")

        # Record recent velocity
        if self.last_target_pos:
            self.target_velocities.append((self.target.position - self.last_target_pos) * 10)
            self.target_velocities = self.target_velocities[-5:]

        self.last_target_pos = self.target.position.copy()
        # Predict position and aim
        charge_time = self._get_charge_time(distance)
        predicted_pos = self._predict_target_position(self.target)
        rot = calculate_rotation(self.user.position, predicted_pos)

        if pitch := self._calculate_shot_angle(predicted_pos, charge_time):
            rot = Rotation(yaw=rot.yaw, pitch=pitch)

        await self.user.translate(rotation=self._smooth_rotation(rot))

    @tasks.ticks(tps=4)
    async def shooting_loop(self) -> None:
        """Handles when and how to shoot based on cooldown and target status."""
        if (not self.target or self.is_shooting or
            len(self.target_velocities) < 2 or
            time.time() - self.last_shot_time < self.shot_cooldown):
            return

        distance = self.target.position.distance_to(self.user.position)
        if distance > self.range_distance:
            return

        self.is_shooting = True
        self.last_shot_time = time.time()

        try:
            charge_time = self._get_charge_time(distance)
            await self.user.use_item()
            await asyncio.sleep(charge_time)
            await self.user.release_item_use()
            print(f"[Shot] {distance:.1f}m | {charge_time:.2f}s | {self._get_target_velocity().magnitude():.1f} blocks/s")
        except Exception as e:
            print(f"[Shot Error] {e}")
        finally:
            self.is_shooting = False

    async def on_join(self) -> None:
        """Called when the bot successfully joins the world."""
        print(f"[Turret] Active - Range: {self.range_distance}m")
        self.aim_and_track.start()
        self.shooting_loop.start()

    async def on_disconnect(self) -> None:
        """Cleanup when disconnected."""
        self.aim_and_track.stop()
        self.shooting_loop.stop()

    async def on_window_items_updated(self, window: Window) -> None:
        """Ensures a bow is equipped if available in the inventory."""
        if window.id != self.user.inventory.id or (window.slots[36].item and window.slots[36].item.id == 261):
            return

        for slot in window.slots:
            if slot.item and slot.item.id == 261:
                await self.hotbar_swap(window, slot.index, hotbar_key=0)
                print("[Equipment] Bow equipped")
                break

turret = AutoTurret('Steve', range_distance=14, whitelist=None, target_all=False)
turret.run('localhost')
