from actmc.entities.misc import DroppedItem
from actmc.utils import calculate_rotation
from actmc.entities.entity import Entity
from actmc.entities.player import Player
from actmc.ui import Window
from actmc import Client
import asyncio

class Trader(Client):
    """
    A trading bot that automatically trades items with players.

    Parameters
    ----------
    username: str
        The username for the bot.
    item_id: int
        Item ID that the bot gives in trade.
    trade_item_id: int
        Item ID that the bot receives in trade.
    refill: bool
        Whether the bot accepts trade items for refill.

    Attributes
    ----------
    look_distance: float
        Maximum distance to detect players.
    """

    def __init__(self, username: str, item_id: int, trade_item_id: int, refill: bool) -> None:
        super().__init__(username)
        self.look_distance = 4.0
        self._refill = refill
        self._item_id = item_id
        self._trade_item_id = trade_item_id
        self._trading_lock = asyncio.Lock()
        self._pending_trades = 0

    async def on_join(self) -> None:
        """Called when the bot joins the server."""
        print(f"Ready to trade as {self.user.username}")

    async def _look_at_closest_player(self) -> None:
        """Find the closest player within range and look at them."""
        players = [e for e in self.entities.values() if isinstance(e, Player) and e.uuid != self.user.uuid]
        if not players:
            return

        closest = min(players, key=lambda p: p.position.distance_to(self.user.position))
        dist = closest.position.distance_to(self.user.position)

        if dist <= self.look_distance:
            rot = calculate_rotation(self.user.position, closest.position)
            await self.user.translate(rotation=rot)

    async def _drop_items(self, item_id: int, count: int) -> int:
        """Drop up to `count` items with the given `item_id`."""
        async with self._trading_lock:
            dropped = 0
            slots = [s for s in self.user.inventory.slots if s.item and s.item.id == item_id]

            # Sort by count (full stacks first)
            slots.sort(key=lambda s: s.item.count, reverse=True)

            for slot in slots:
                if dropped >= count:
                    break

                item = slot.item
                if item.count == 64:
                    await self.drop_item(self.user.inventory, slot.index, drop_stack=True)
                    await asyncio.sleep(0.15)
                    dropped += 64
                else:
                    to_drop = min(item.count, count - dropped)
                    for _ in range(to_drop):
                        await self.drop_item(self.user.inventory, slot.index)
                        await asyncio.sleep(0.15)
                        dropped += 1
            return count - dropped

    async def _perform_trade(self, count: int) -> None:
        """Perform a trade with concurrency control."""
        left = await self._drop_items(self._trade_item_id, count)
        if left > 0:
            print("[Trade] Not enough trade items. Dropping fallback items.")
            await self._drop_items(self._item_id, left)

    async def on_entity_head_look(self, *_) -> None:
        """Called when any entity updates head rotation."""
        await self._look_at_closest_player()

    async def on_collect_item(self, collected: Entity, count: int, collector: Entity) -> None:
        """Called when an item is collected by an entity."""
        if isinstance(collected, DroppedItem) and collector.id == self.user.id:
            if collected.item.id == self._item_id:
                self._pending_trades += count
                print(f"[Collect] Queued {count} trade(s). Total pending: {self._pending_trades}")
                await self.user.sneak(True)
                await asyncio.sleep(0.1)
                await self.user.sneak(False)

    async def on_window_items_updated(self, window: Window) -> None:
        """Called when inventory window items are updated."""
        if window.id != self.user.inventory.id:
            return

        # Drop unrelated items
        for slot in window.slots:
            if slot.item:
                if slot.item.id != self._item_id and slot.item.id == self._trade_item_id and not self._refill:
                    await self._drop_items(slot.item.id, slot.item.count)

        # Process queued trades
        if self._pending_trades > 0:
            count = self._pending_trades
            self._pending_trades = 0
            print(f"[Trade] Performing {count} trade(s)")
            await self._perform_trade(count)

# Bot trades Apple → Golden Apple, no refill
bot = Trader('Steve', 260, 322, False)
bot.run('localhost')