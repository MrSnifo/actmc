## Chat Events

Note
----
Some servers may send all messages, including player chat, as system messages.
If `on_chat_message` doesn't trigger, check `on_system_message` instead.

### Chat Message

* **Description**: Player chat message received
* **Parameters**:

  * `message`: \[`Message`]\[actmc.ui.chat.Message]
* **Usage**:

  ```python
  @client.event
  async def on_chat_message(message: Message) -> None:
      ...
  ```

### System Message

* **Description**: System message received (can include player chat)
* **Parameters**:

  * `message`: \[`Message`]\[actmc.ui.chat.Message]
* **Usage**:

  ```python
  @client.event
  async def on_system_message(message: Message) -> None:
      ...
  ```
