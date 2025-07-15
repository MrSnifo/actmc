from actmc import Client

client = Client('Steve')

@client.event
async def on_join() -> None:
    """Called when the bot joins the server."""
    print("Bot joined the server!")

@client.event
async def on_ready() -> None:
    """Called when the bot is fully connected and ready."""
    print("Bot is connected and ready!")

@client.event
async def on_player_health_update(health: float, food: int, saturation: float) -> None:
    """Called whenever the player's health or food updates."""
    print(f"Health update: health={health}, food={food}, saturation={saturation}")
    if health <= 0:
        print("Health is zero or below! Performing respawn...")
        await client.perform_respawn()

client.run('localhost', 25565)
