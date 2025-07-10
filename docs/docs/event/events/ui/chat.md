## Chat Events

### Chat Message

* **Description**: Chat message received
* **Parameters**:

  * `message`: [`Message`][actmc.ui.chat.Message] - The chat message
* **Usage**:

  ```python
  @client.event
  async def on_chat_message(message: Message) -> None:
      ...
  ```

### System Message

* **Description**: System message received
* **Parameters**:

  * `message`: [`Message`][actmc.ui.chat.Message] - The system message
* **Usage**:

  ```python
  @client.event
  async def on_system_message(message: Message) -> None:
      ...
  ```