from actmc.entities import Entity, Living, Player, Monster
from actmc.utils import calculate_rotation
from actmc import Client, Vector3D
from typing import Optional, List
from actmc.ext import tasks
from actmc.ui import Window
import asyncio

class AutoTurret(Client):
    """
    Automated turret system for Minecraft that tracks and shoots at targets.

    Parameters
    ----------
    username: str
        Bot username
    range_distance: float, default=12
        Maximum targeting range in blocks
    whitelist: Optional[List[str]], default=None
        Player names to never target. None = no players, [] = all players
    target_all: bool
        Target all living entities vs monsters only

    Notes
    -----
    - Requires bow and arrows in inventory to operate.
    - The bow will be automatically equipped when shooting.
    """

    def __init__(self, username: str, range_distance: float = 12,
                 whitelist: Optional[List[str]] = None, target_all: bool = False) -> None:
        super().__init__(username)
        self.range_distance = range_distance
        self.whitelist = whitelist
        self.target_all = target_all
        self.target = None
        self.target_velocities = []
        self.last_target_pos = None

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
        """Calculate average velocity from recent samples."""
        if len(self.target_velocities) < 2:
            return Vector3D(0, 0, 0)

        recent = self.target_velocities[-3:]
        return Vector3D(
            sum(v.x for v in recent) / len(recent),
            sum(v.y for v in recent) / len(recent),
            sum(v.z for v in recent) / len(recent)
        )

    def _predict_position(self, target: Living) -> Vector3D:
        """Predict target position when arrow hits."""
        velocity = self._get_target_velocity()

        if velocity.magnitude() < 0.1:
            return target.position

        distance = target.position.distance_to(self.user.position)
        time_to_hit = distance / 30

        # Add lead time for better accuracy
        return target.position + velocity * (time_to_hit + 0.15)

    @tasks.ticks(tps=10)
    async def aim_and_track(self) -> None:
        """Main targeting loop - find the closest target and aim."""
        # Find valid targets
        enemies = [e for e in self.entities.values() if self._is_valid_target(e)]
        if not enemies:
            self.target = None
            return

        # Get the closest target within range
        closest = min(enemies, key=lambda e: e.position.distance_to(self.user.position))
        distance = closest.position.distance_to(self.user.position)

        if distance > self.range_distance:
            self.target = None
            return

        # Switch targets if needed
        if self.target != closest:
            self.target = closest
            self.target_velocities = []
            self.last_target_pos = None
            target_name = closest.__class__.__name__ if closest else 'Unknown'
            print(f"[Target] {target_name}")

        # Track velocity
        if self.last_target_pos:
            velocity = (self.target.position - self.last_target_pos) * 10
            self.target_velocities.append(velocity)

            # Keep only recent samples
            if len(self.target_velocities) > 5:
                self.target_velocities.pop(0)

        self.last_target_pos = self.target.position.copy()

        # Aim at predicted position
        predicted_pos = self._predict_position(self.target)
        rotation = calculate_rotation(self.user.position, predicted_pos)
        await self.user.translate(rotation=rotation)

    @tasks.loop(seconds=0.15)
    async def shoot(self) -> None:
        """Shooting loop with dynamic release timing."""
        if not self.target or len(self.target_velocities) < 2:
            return

        distance = self.target.position.distance_to(self.user.position)

        # Dynamic release time based on distance
        normalized_distance = distance / self.range_distance
        release_time = 0.15 + (0.9 * normalized_distance)
        release_time = max(0.15, min(1.0, release_time))

        await self.user.use_item()
        await asyncio.sleep(release_time)
        await self.user.release_item_use()

        speed = self._get_target_velocity().magnitude()
        print(f"[Shot] {distance:.1f}m | {release_time:.2f}s | {speed:.1f} blocks/s")

    async def on_join(self) -> None:
        """Initialize turret system."""
        print(f"[Turret] Active - Range: {self.range_distance} blocks")
        self.aim_and_track.start()
        self.shoot.start()

    async def on_disconnect(self) -> None:
        """Clean up on disconnect."""
        self.aim_and_track.stop()
        self.shoot.stop()

    async def on_window_items_updated(self, window: Window) -> None:
        """Auto-equip bow when available."""
        if window.id != self.user.inventory.id:
            return

        # Check if bow already equipped
        if window.slots[36].item and window.slots[36].item.id == 261:
            return

        # Find and equip bow
        for slot in window.slots:
            if slot.item and slot.item.id == 261:
                await self.hotbar_swap(window, slot.index, hotbar_key=0)
                print("[Equipment] Bow equipped")
                break


turret = AutoTurret('Steve', range_distance=15, whitelist=None, target_all=False)
turret.run('localhost')