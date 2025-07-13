## Client Events

### connect
- **Description**: Triggered when client successfully connects to server
- **Usage**:
  ```python
  @client.event
  async def on_connect() -> None:
      ...
  ```

### ready
- **Description**: Triggered when client is fully ready
- **Usage**:
  ```python
  @client.event
  async def on_ready() -> None:
      ...
  ```

### disconnect
- **Description**: Triggered when client disconnects
- **Usage**:
  ```python
  @client.event
  async def on_disconnect() -> None:
      ...
  ```

### handshake
- **Description**: Initial handshake complete
- **Usage**:
  ```python
  @client.event
  async def on_handshake() -> None:
      ...
  ```

## Error Handling

### error
- **Description**: Handles dispatch errors
- **Parameters**:
  - `event_name`: [`str`][str] - Name of the event that caused the error
  - `error`: [`Exception`][Exception] - The exception that was raised
- **Usage**:
  ```python
  @client.event
  async def on_error(event_name: str, error: Exception, *args, **kwargs) -> None:
      ...
  ```

## Setup

### setup hook
- **Description**: Setup actions before client starts running
- **Usage**:
  ```python
  class MyClient(Client):
      async def setup_hook(self) -> None:
          # Setup logic here
          ...
  ```