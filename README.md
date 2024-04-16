# pipesocket

`pipesocket` is a Python package designed for testing socket communication between a client and a server. It facilitates message passing using WebSocket technology.

## Installation

To install `pipesocket`, you can use `pip`:

```bash
pip install git+https://github.com/saltchicken/pipesocket
```

## Usage

### Server

To start a server, you can create an instance of `ServerPipeSocket`. You can specify the host IP and port if needed. By default, the server listens on `localhost` at port `8765`.

```python
from pipesocket import ServerPipeSocket

server = ServerPipeSocket()
```

### Client

To start a client, create an instance of `ClientPipeSocket`. You need to provide the host IP and port of the server.

```python
from pipesocket import PipeSocket

client = PipeSocket(host_ip='192.168.1.10', host_port=5555)
```

### Sending and Receiving Messages

Once the client and server are initialized, you can send and receive messages between them.

#### Sending Messages

You can use the `put_message()` method to send a message from the client to the server.

```python
client.put_message("Hello from client!")
```

Similarly, you can use the `put_system_message()` method to send system messages.

```python
client.put_system_message("System message from client!")
```

#### Receiving Messages

On the server side, you can use the `receive_stream_message()` method to continuously receive messages from the client.

```python
server.receive_stream_message()
```

## Examples

### Client Example

```python
from pipesocket import ClientPipeSocket

client = ClientPipeSocket(host_ip='192.168.1.10', host_port=5555)
client.put_message("Hello from client!")
client.put_system_message("System message from client!")
```

### Server Example

```python
from pipesocket import ServerPipeSocket

server = ServerPipeSocket()
server.receive_stream_message()
```

## Additional Notes

- The `pipesocket` package also includes experimental features such as `JSONMessage` and `SystemMessage`.
- For more advanced usage, refer to the documentation within the package files.
