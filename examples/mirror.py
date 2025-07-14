from actmc.entities.entity import Entity
from actmc.entities.player import Player
from typing import Optional
from actmc import Client

client = Client('Steve')

@client.event
async def on_ready():
    """Bot connected."""
    print("Bot is connected and ready!")

async def try_mirror(entity: Entity, on_ground: Optional[bool] = None) -> None:
    """Mirror player movements and rotations exactly."""
    if isinstance(entity, Player) and entity.id != client.user.id:
        await client.user.translate(entity.position, entity.rotation, on_ground=on_ground)
        await client.user.sprint(entity.sprinting)
        await client.user.sneak(entity.crouched)


@client.event
async def on_entity_move_look(entity: Entity, _, on_ground: bool) -> None:
    """Mirror on move & look."""
    await try_mirror(entity, on_ground)

@client.event
async def on_entity_move(entity: Entity, _, on_ground: bool) -> None:
    """Mirror on move."""
    await try_mirror(entity, on_ground)

@client.event
async def on_entity_look(entity: Entity, on_ground: bool) -> None:
    """Mirror on look."""
    await try_mirror(entity, on_ground)

@client.event
async def on_entity_head_look(entity: Entity) -> None:
    """Mirror head look."""
    await try_mirror(entity)

@client.event
async def on_entity_animation(entity: Entity, animation_id: int) -> None:
    """Mirror Swing main."""
    if isinstance(entity, Player) and entity.id != client.user.id:
        # Swing main arm
        if animation_id == 0:
            await client.user.swing_arm()

client.run('localhost', 25565)