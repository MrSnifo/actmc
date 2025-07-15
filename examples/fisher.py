from actmc.entities import FishingHook
from actmc import Client, Vector3D
from actmc.ui import Window
import asyncio

class Fisher(Client):
    """A Minecraft fishing bot that automatically catches fish."""

    def __init__(self, username: str) -> None:
        super().__init__(username)

    async def on_ready(self) -> None:
        """Called when the bot joins the server and ready."""
        await self.user.use_item()

    async def on_sound_effect(self, sound_id: int, _, position: Vector3D, *__) -> None:
        """Handle sound effects from the game."""
        # Check for bobber splash sound (ID 153 = fish bite)
        if sound_id == 153:
            # Find the closest fishing hook to the splash position
            closest_hook = min(
                (entity for entity in self.entities.values() if isinstance(entity, FishingHook)),
                key=lambda hook: hook.position.distance_to(position),
                default=None
            )

            if closest_hook:
                if self.user.id == closest_hook.owner_id:
                    await self.user.use_item()  # Reel in
                    await asyncio.sleep(0.5)  # Wait before casting
                    await self.user.use_item()  # Cast again
                print(f"Fish caught! Distance: {closest_hook.position.distance_to(position):.2f}")

    async def on_window_items_updated(self, window: Window) -> None:
        """Handle inventory updates to manage fishing rod placement."""
        if window.id != self.user.inventory.id:
            return

        # Check if fishing rod (ID 346) is already in hand (slot 36)
        hand = window.slots[36]
        if hand.item and hand.item.id == 346:
            return

        # Search inventory for fishing rod
        found = None
        for slot in window.slots:
            if slot.item and slot.item.id == 346:
                found = slot
                break

        if found:
            # Move fishing rod to hotbar slot 0
            await self.hotbar_swap(window, found.index, hotbar_key=0)
            await asyncio.sleep(0.5)
            await self.user.use_item()
        else:
            print('No fishing rods found!')


bot = Fisher('Steve')
bot.run('localhost')