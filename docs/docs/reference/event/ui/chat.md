## Chat Events

???+ Note

    Some servers may send all messages, including player chat, as system messages.
    If [on_chat_message](#chat-message) doesn't trigger, check [on_system_message](#system-message) instead.
    Additionally, both chat and system messages also trigger the unified [on_message](#message) event.

### Message

* **Description**: Unified event triggered for both chat and system messages.
* **Parameters**:
  * `message`: [`Message`][actmc.ui.chat.Message]
* **Usage**:
  ```python
  @client.event
  async def on_message(message: Message) -> None:
      ...
  ```

### Chat Message

* **Description**: Player chat message received.
* **Parameters**:
  * `message`: [`Message`][actmc.ui.chat.Message]
* **Usage**:
  ```python
  @client.event
  async def on_chat_message(message: Message) -> None:
      ...
  ```

### System Message

* **Description**: System message received (can include player chat or server notices).
* **Parameters**:
  * `message`: [`Message`][actmc.ui.chat.Message]
* **Usage**:
  ```python
  @client.event
  async def on_system_message(message: Message) -> None:
      ...
  ```


