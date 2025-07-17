from actmc.ui import Message
from actmc import Client

client = Client('Steve')

@client.event
async def on_ready() -> None:
    """Called when connected and ready"""
    print(f"Connected as {client.user.username}")

@client.event
async def on_message(message: Message) -> None:
    """Called for both chat and system messages."""
    if '!ping' in message.to_plain_text().lower():
        await client.send_message('Pong!')

client.run('localhost', 25565)
