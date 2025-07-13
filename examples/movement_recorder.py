
from actmc.entities.player import Player
from actmc.entities.entity import Entity
from actmc.ui import Message
from actmc import Client
import asyncio
import time

class Bot(Client):
    """
    Records and replays player movements in Minecraft.

    Commands
    --------
    !target - Lock onto owner player
    !record - Start movement recording
    !stop   - Stop recording
    !play   - Replay movements
    !clear  - Reset recordings
    """
    def __init__(self, username: str, owner_name: str):
        super().__init__(username)
        self.owner_name = owner_name.lower()
        self._entity_id = None
        self.recording = False
        self.records = []
        self._last_record_time = None
        self._record_start_time = None
        self.playing = False

    async def on_ready(self):
        """Called when bot connects successfully."""
        print(f"Bot ready! Commands: !target, !record, !stop, !play, !clear")

    async def on_system_message(self, message: Message):
        """Handle system messages."""
        await self.handle_message(message)

    async def on_chat_message(self, message: Message):
        """Handle chat messages."""
        await self.handle_message(message)

    async def handle_message(self, message: Message):
        """Process chat commands."""
        text = message.to_plain_text().lower()
        if "!target" in text:
            await self._set_target()
        elif "!record" in text:
            await self._start_recording()
        elif "!stop" in text:
            self.recording = False
            print(f"Recorded {len(self.records)} movements")
        elif "!play" in text:
            await self._play_movements()
        elif "!clear" in text:
            self.records.clear()
            print("Cleared recordings")

    async def _set_target(self):
        """Set recording target to the specified owner player.

        Matches the owner_name against tablist player info to find the UUID,
        then locates the corresponding entity in the world.
        """
        # Find owner UUID in tablist by name
        owner_uuid = next(
            (uuid for uuid, player in self.tablist.items()
             if getattr(player, 'name', '').lower() == self.owner_name.lower()),
            None
        )

        if not owner_uuid:
            print(f"Owner player '{self.owner_name}' not found in tablist")
            return

        # Find entity by UUID in world
        self._entity_id = next(
            (eid for eid, entity in self.entities.items()
             if isinstance(entity, Player) and
             getattr(entity, 'uuid', None) == owner_uuid),
            None
        )

        if self._entity_id:
            print(f"Target locked: {self.owner_name} (Entity ID: {self._entity_id})")
        else:
            print(f"Owner found in tablist but not spawned in world (UUID: {owner_uuid})")

    async def _start_recording(self, duration: float = None):
        """Begin recording player movements.

        Parameters
        ----------
        duration : float, optional
            Recording duration in seconds (None for indefinite)
        """
        if not self._entity_id:
            print("Set target first (!target)")
            return

        self.records.clear()
        self.recording = True
        self._record_start_time = time.time()
        self._last_record_time = self._record_start_time

        if duration:
            asyncio.create_task(self._auto_stop_recording(duration))
            print(f"Recording for {duration} seconds...")
        else:
            print("Recording started (use !stop to end)")

    async def _auto_stop_recording(self, duration: float):
        """Automatically stop recording after duration."""
        await asyncio.sleep(duration)
        if self.recording:
            await self._stop_recording()

    async def _stop_recording(self):
        """Stop recording movements."""
        if not self.recording:
            print("Not recording")
            return

        self.recording = False
        duration = time.time() - self._record_start_time
        print(f"Stopped recording ({len(self.records)} movements, {duration:.1f}s)")

    def _clear_recordings(self):
        """Clear all recorded movements."""
        self.records.clear()
        print("Recordings cleared")

    async def _play_movements(self):
        """Replay recorded movements with original timing."""
        if self.playing:
            print("Already playing back movements")
            return

        if not self.records:
            print("No recordings to play")
            return

        self.playing = True
        print(f"Playing {len(self.records)} movements...")
        start = time.time()

        try:
            for i, rec in enumerate(self.records):
                if i > 0:
                    await asyncio.sleep(rec['time_since_last'])
                await self.user.translate(
                    position=rec['position'],
                    rotation=rec.get('rotation'),
                    on_ground=rec.get('on_ground', True)
                )
        finally:
            self.playing = False
            duration = time.time() - start
            print(f"Done in {duration:.1f}s")

    async def _record_movement(self, entity: Entity, on_ground: bool = None):
        """Record a single movement frame."""
        if not self.recording or entity.id != self._entity_id:
            return

        now = time.time()
        self.records.append({
            'position': entity.position,
            'rotation': getattr(entity, 'rotation', None),
            'on_ground': on_ground,
            'timestamp': now - self._record_start_time,
            'time_since_last': now - (self._last_record_time or now)
        })
        self._last_record_time = now

    # Event handlers
    async def on_entity_move_look(self, e, _, g): await self._record_movement(e, g)
    async def on_entity_move(self, e, _, g): await self._record_movement(e, g)
    async def on_entity_look(self, e, g): await self._record_movement(e, g)
    async def on_entity_head_look(self, e): await self._record_movement(e)


if __name__ == "__main__":
    bot = Bot("Steve", "Snifo")
    bot.run("localhost")