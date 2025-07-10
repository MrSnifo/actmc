# Loop System

Want your bot to do things automatically? The Loop system runs your code over and over at regular intervals.

## Basic Usage

```python
from actmc.ext.ticks import ticks

@ticks(tps=20)  # Runs 20 times per second
async def my_bot(tick, elapsed_time):
    print(f"Tick {tick}")

# Start it
task = my_bot.start()
```

## Examples

### Auto Chat

```python
@ticks(tps=1)  # Once per second
async def auto_chat(tick, elapsed_time):
    await client.send_message("Hello world!")
```

## Control

```python
# Stop the loop
my_bot.stop()

# Pause/resume
my_bot.pause()
my_bot.resume()
```

Perfect for making your bot do things automatically without you having to trigger them manually!