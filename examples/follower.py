from actmc.entities.entity import Entity
from actmc.entities.player import Player
from typing import Optional
from actmc import Client


client = Client('Steve')

@client.event
async def on_ready():
    """Bot connected."""
    print("Bot is connected and ready!")


async def try_follow(entity: Entity, on_ground: Optional[bool] = None) -> None:
    """Follow players, keeping 1-4 blocks distance."""
    if isinstance(entity, Player) and entity.id != client.user.id:
        distance = entity.position.distance_to(client.user.position)
        if distance < 4:
            if distance > 1:
                await client.user.translate(entity.position, entity.rotation, on_ground=on_ground)
            else:
                client.user.position.y = entity.position.y
                await client.user.translate(client.user.position, entity.rotation, on_ground=on_ground)

@client.event
async def on_entity_move_look(entity: Entity, _, on_ground: bool) -> None:
    """Follow on move & look."""
    await try_follow(entity, on_ground)

@client.event
async def on_entity_move(entity: Entity, _, on_ground: bool) -> None:
    """Follow on move."""
    await try_follow(entity, on_ground)

@client.event
async def on_entity_look(entity: Entity, on_ground: bool) -> None:
    """Follow on look."""
    await try_follow(entity, on_ground)

@client.event
async def on_entity_head_look(entity: Entity) -> None:
    await try_follow(entity)

client.run('localhost', 25565)
