# actmc

[![PyPI - Version](https://img.shields.io/pypi/v/actmc?color=%234CAF50)](https://pypi.org/project/actmc)
[![License: MIT](https://img.shields.io/badge/License-MIT-4CAF50.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

An async Python client for Minecraft Java Edition 1.12.2 servers that run in offline mode.

**Key Features**

* Modern async/await API.
* Comprehensive protocol support.
* Optimised in both speed and memory.

## Installing

**Python 3.12 or higher is required**

To install the library, you can just run the following command:

```bash
# Linux/macOS
python3 -m pip install -U actmc

# Windows
py -3 -m pip install -U actmc
```

To install the development version, do the following:

```bash
$ git clone https://github.com/mrsnifo/actmc
$ cd actmc
$ python3 -m pip install -U .
```

## Quick Example

```python
from actmc import Client
from actmc.ui import Message

client = Client(username='Steve')

@client.event
async def on_ready():
    print('Connected as', client.user.username)

@client.event
async def on_message(message: Message) -> None:
    # Strip chat colors.
    text = message.to_plain_text()
    if 'pog' in text.lower():
        await client.send_message('Poggers!')

client.run('localhost', 25565)
```

## Documentation

For more detailed instructions,
visit the [actmc Documentation](https://actmc.readthedocs.io/latest/).
