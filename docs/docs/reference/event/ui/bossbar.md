## Boss Bar Events

### Boss Bar Add

* **Description**: Boss bar added
* **Parameters**:

  * `bar`: [`BossBar`][actmc.ui.bossbar.BossBar] - The boss bar
* **Usage**:

  ```python
  @client.event
  async def on_boss_bar_add(bar: BossBar) -> None:
      ...
  ```

### Boss Bar Remove

* **Description**: Boss bar removed
* **Parameters**:

  * `bar`: [`BossBar`][actmc.ui.bossbar.BossBar] - The boss bar
* **Usage**:

  ```python
  @client.event
  async def on_boss_bar_remove(bar: BossBar) -> None:
      ...
  ```

### Boss Bar Update Health

* **Description**: Boss bar health updated
* **Parameters**:

  * `bar`: [`BossBar`][actmc.ui.bossbar.BossBar] - The boss bar
* **Usage**:

  ```python
  @client.event
  async def on_boss_bar_update_health(bar: BossBar) -> None:
      ...
  ```

### Boss Bar Update Title

* **Description**: Boss bar title updated
* **Parameters**:

  * `bar`: [`BossBar`][actmc.ui.bossbar.BossBar] - The boss bar
* **Usage**:

  ```python
  @client.event
  async def on_boss_bar_update_title(bar: BossBar) -> None:
      ...
  ```

### Boss Bar Update Style

* **Description**: Boss bar style updated
* **Parameters**:

  * `bar`: [`BossBar`][actmc.ui.bossbar.BossBar] - The boss bar
* **Usage**:

  ```python
  @client.event
  async def on_boss_bar_update_style(bar: BossBar) -> None:
      ...
  ```

### Boss Bar Update Flags

* **Description**: Boss bar flags updated
* **Parameters**:

  * `bar`: [`BossBar`][actmc.ui.bossbar.BossBar] - The boss bar
* **Usage**:

  ```python
  @client.event
  async def on_boss_bar_update_flags(bar: BossBar) -> None:
      ...
  ```
