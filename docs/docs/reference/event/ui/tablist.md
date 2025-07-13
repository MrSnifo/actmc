## Tablist Events

### Player List Header Footer

* **Description**: Tablist header/footer updated
* **Parameters**:
  * `header`: [`Message`][actmc.ui.chat.Message] - Header text
  * `footer`: [`Message`][actmc.ui.chat.Message] - Footer text
* **Usage**:

  ```python
  @client.event
  async def on_player_list_header_footer(header: Message, footer: Message) -> None:
      ...
  ```

### Players Add

* **Description**: Players added to tablist
* **Parameters**:
  * `players`: [`List`][typing.List][[`PlayerInfo`][actmc.ui.tablist.PlayerInfo]] - Added players
* **Usage**:
  ```python
  @client.event
  async def on_players_add(players: List[PlayerInfo]) -> None:
      ...
  ```

### Players Remove

* **Description**: Players removed from tablist
* **Parameters**:
  * `players`: [`List`][typing.List][[`PlayerInfo`][actmc.ui.tablist.PlayerInfo]] - Removed players
* **Usage**:
  ```python
  @client.event
  async def on_players_remove(players: List[PlayerInfo]) -> None:
      ...
  ```

### Players Gamemode Update

* **Description**: Player gamemode updated
* **Parameters**:
  * `players`: [`List`][typing.List][[`PlayerInfo`][actmc.ui.tablist.PlayerInfo]] - Updated players
* **Usage**:
  ```python
  @client.event
  async def on_players_gamemode_update(players: List[PlayerInfo]) -> None:
      ...
  ```

### Players Ping Update

* **Description**: Player ping updated
* **Parameters**:

  * `players`: [`List`][typing.List][[`PlayerInfo`][actmc.ui.tablist.PlayerInfo]] - Updated players
* **Usage**:

  ```python
  @client.event
  async def on_players_ping_update(players: List[PlayerInfo]) -> None:
      ...
  ```

### Players Display Name Update

* **Description**: Player display name updated
* **Parameters**:

  * `players`: [`List`][typing.List][[`PlayerInfo`][actmc.ui.tablist.PlayerInfo]] - Updated players
* **Usage**:

  ```python
  @client.event
  async def on_players_display_name_update(players: List[PlayerInfo]) -> None:
      ...
  ```