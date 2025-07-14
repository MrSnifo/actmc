# Events in ACTMC

Events in **actmc** let your bot react to things happening in Minecraft.
Think of them as notifications that tell your code "Hey, something just happened!".

## How It Works

Simple concept:

1. You write a function
2. The client watches for activities  
3. When something happens, your function runs automatically

## Two Ways to Handle Events

You can register events using two approaches:

=== "Standalone"

    #### Using the [@client.event](../core/client.md#actmc.client.Client.event) decorator

    ```python
    from actmc import Client

    client = Client('Steve')

    @client.event
    async def on_connect():
        print("Connected to server!")

    @client.event
    async def on_join():
        await client.send_message(f'Joined as {client.user.username}')

    client.run('localhost')
    ```

=== "Subclassing"

    #### Direct method definition (no decorator needed)

    ```python
    from actmc import Client

    class MyBot(Client):
        def __init__(self, username):
            super().__init__(username)

        async def on_connect(self):
            print("Connected to server!")
        
        async def on_join(self):
            await self.send_message(f'Joined as {self.user.username}')

    bot = MyBot('Steve')
    bot.run('localhost')
    ```

## Why Use Events?

Events make your bot responsive and efficient:

- No need to constantly check for changes
- Code only runs when something actually happens
- Clean organization for different reactions
