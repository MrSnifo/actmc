# Quickstart

## Installation

### From PyPI (Recommended)

```bash
python3 -m pip install -U actmc
```

### Development Version

```bash
git clone https://github.com/mrsnifo/actmc.git
cd actmc
python3 -m pip install -U .
```

### (Optional) Virtual Environment

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
from actmc import Client
from actmc.ui.chat import Message

client = Client('steve')

@client.event
async def on_ready():
    print(f"Connected as {client.user.username}")

@client.event
async def on_message(message: Message):
    if message.to_plain_text() == "!ping":
        await client.send_message("Pong!")

client.run('localhost', 25565)
```

### Handling Errors

```python
@client.event
async def on_error(event_name: str, error: Exception):
    print(f"Error in {event_name}: {error}")
```
