# Concepts

## What is actmc?

**actmc** is a Python library for connecting to Minecraft servers.
It is designed for creating bots and automation rather than playing the game.
The library handles network communication without providing graphics, controls,
or a user interface.

## Connecting to Servers

You need two things to connect:

* **Host**: The server address (like `localhost` or `play.example.com`)

* **Port**: Usually `25565`

```python
# Simple way to connect
client.run('localhost', 25565)

# Or with async/await
await client.start('localhost', 25565)
```

## Events

When things happen on the server (like players chatting or joining), actmc turns them into events that your code can respond to:

```python
from actmc import Client

client = Client('steve')

@client.event
async def on_connect():
    print("Connected!")

@client.event
async def on_join():
    print("Joined the served!")
```

## Version Support

**actmc** works with **Minecraft Java Edition 1.12.2** on **offline-mode servers**.

Install a specific protocol version:

```bash
pip install "actmc==1.12.2.postX"
```

Replace **X** with the desired post version (e.g., `post2`).
