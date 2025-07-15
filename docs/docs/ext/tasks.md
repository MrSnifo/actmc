# Loop System

Want your bot to do things automatically? The Loop system runs your code over and over at regular intervals.

## Basic Usage

```python
from actmc.ext import tasks

@ticks(tps=20)  # Runs 20 times per second
async def my_bot():
    print(f"Tick {my_bot.current_tick}")


# Start it
task = my_bot.start()
```

## Time Options

```python
@tasks.ticks(tps=1)           # Once per second
@tasks.loop(seconds=5.0)      # Every 5 seconds
@tasks.loop(minutes=1.0)      # Every minute
@tasks.loop(hours=2.0)        # Every 2 hours
```

## Examples

### Auto Chat
```python
@ticks(tps=0.5)  # Every 2 seconds
async def auto_chat():
    await client.send_message("Hello world!")
```

### Health Check
```python
@loop(seconds=10.0)
async def health_check():
    if await bot.get_health() < 5:
        await bot.eat_food()
```

## Control

```python
# Start/stop
my_bot.start()
my_bot.stop()

# Pause/resume
my_bot.pause()
my_bot.resume()

# Check status
print(my_bot.is_running)
print(my_bot.current_tick)
```

## Error Handling

```python
@my_bot.on_error
async def handle_error(error, tick):
    print(f"Error on tick {tick}: {error}")
    # Loop continues running
```

Perfect for making your bot do things automatically without you having to trigger them manually!