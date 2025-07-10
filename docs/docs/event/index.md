# Introduction

Events in **actmc** let your code react to things that happen in Minecraft, like connecting to a server or a player joining.

An **event** is a function that runs automatically when something specific happens. You write the function, and the client calls it at the right time.

## How It Works

1. You write a function and mark it with `@client.event`
2. The client watches for certain activities
3. When something happens, your function runs automatically

## Example

```python
@client.event
async def on_connect():
    print("Connected to server!")
```

This code prints a message every time you connect to a Minecraft server.

## Why Use Events?

Events make your code simple and efficient:
- No need to constantly check for changes
- Your code only runs when something actually happens
- Easy to organize different reactions to different events