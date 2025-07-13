## Action Bar Events

### Action Bar

* **Description**: Action bar message received
* **Parameters**:

  * `message`: [`Message`][actmc.ui.chat.Message] - The message
* **Usage**:

  ```python
  @client.event
  async def on_action_bar(message: Message) -> None:
      ...
  ```

### Title Set Title

* **Description**: Title text set
* **Parameters**:

  * `text`: [`str`][str] - Title text
* **Usage**:

  ```python
  @client.event
  async def on_title_set_title(text: str) -> None:
      ...
  ```

### Title Set Subtitle

* **Description**: Subtitle text set
* **Parameters**:

  * `text`: [`str`][str] - Subtitle text
* **Usage**:

  ```python
  @client.event
  async def on_title_set_subtitle(text: str) -> None:
      ...
  ```

### Title Set Action Bar

* **Description**: Action bar text set
* **Parameters**:

  * `text`: [`str`][str] - Action bar text
* **Usage**:

  ```python
  @client.event
  async def on_title_set_action_bar(text: str) -> None:
      ...
  ```

### Title Set Times

* **Description**: Title times set
* **Parameters**:

  * `fade_in`: [`int`][int] - Fade-in time (ticks)
  * `stay`: [`int`][int] - Stay time (ticks)
  * `fade_out`: [`int`][int] - Fade-out time (ticks)
* **Usage**:

  ```python
  @client.event
  async def on_title_set_times(fade_in: int, stay: int, fade_out: int) -> None:
      ...
  ```

### Title Hide

* **Description**: Title hidden
* **Usage**:

  ```python
  @client.event
  async def on_title_hide() -> None:
      ...
  ```

### Title Reset

* **Description**: Title reset
* **Usage**:

  ```python
  @client.event
  async def on_title_reset() -> None:
      ...
  ```