# Quickstart

## Installation

### From PyPI

```bash
python3 -m pip install -U actmc
```

### Development Version

```bash
git clone https://github.com/mrsnifo/actmc.git
cd actmc
python3 -m pip install -U .
```

### Virtual Environment

```bash
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install actmc
```

## Requirements

* Python 3.12 or higher
* Basic async/await knowledge

## Example Bot

A simple bot that connects to a server and replies to a command:

```python
from actmc.ui.chat import Message
from actmc import Client

client = Client('Steve')

@client.event
async def on_ready():
    """Called when the bot has connected and is ready to receive events."""
    print("Bot connected!")

async def handle_message(message: Message) -> None:
    """Handles incoming chat or system messages."""
    if '!ping' in message.to_plain_text().lower():
        await client.send_message('Pong!')

@client.event
async def on_system_message(message: Message) -> None:
    """
    Called when a system message is received.
    Some servers send chat messages as system messages, so listen here too.
    """
    await handle_message(message)

@client.event
async def on_chat_message(message: Message) -> None:
    """
    Called when a chat message is received.
    Listen here in case the server sends chat normally.
    """
    await handle_message(message)

client.run('localhost', 25565)
```

### Learn More

Want to build more advanced bots or explore available events?

Check out the [event reference](./reference/event/index.md).

