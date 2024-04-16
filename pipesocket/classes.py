import asyncio
import websockets
from websockets.exceptions import ConnectionClosed
import queue, asyncio
from loguru import logger


class Base():
    def __init__(self, send_q, receive_q, stop_event):
        self.send_q = send_q
        self.receive_q = receive_q
        self.stop_event = stop_event

    async def process_input(self, input):
        self.receive_q.put(input)
        return True

    async def send(self):
        try:
            message = self.send_q.get_nowait()
            return message
        except queue.Empty:
            await asyncio.sleep(0.1)

class Client(Base):
    def __init__(self, host_ip, host_port, send_q, receive_q, stop_event):
        super().__init__(send_q, receive_q, stop_event)
        self.stop_event = stop_event
        if host_ip == 'localhost':
            self.uri = f"ws://localhost:{str(host_port)}"
        else:
            self.uri = f"ws://{host_ip}:{str(host_port)}"

    async def send_routine(self, ws):
        while not self.stop_event.is_set():
            try:
                output = await self.send()
                if not output: continue
                await ws.send(output)
            except websockets.exceptions.ConnectionClosedOK:
                logger.warning('Connection was already closed. Breaking')
                break
        logger.debug('Broke out of send_routine')

    async def receive_routine(self, ws):
        try:
            while True:
                message = await ws.recv()
                # TODO: self.process_input has to return True or else connection is broken.
                result = await self.process_input(message)
                if not result: break
        except ConnectionClosed:
            # TODO: This needs to quit the client
            logger.debug("Server closed connection")
            self.stop_event.set()
        except asyncio.CancelledError:
            logger.debug("Routine cancelled")
        
    async def main(self):
        async with websockets.connect(self.uri) as websocket:
            # send_task = asyncio.create_task(send_routine(websocket))
            task = asyncio.create_task(self.receive_routine(websocket))
            send_task = self.send_routine(websocket)
            # task = receive_routine(websocket)
            await send_task
            task.cancel()
            logger.debug("End of main reached")
            # await asyncio.Future()

    def run(self):
        asyncio.run(self.main())


class Server(Base):
    def __init__(self, host_ip, host_port, send_q, receive_q, stop_event):
        super().__init__(send_q, receive_q, stop_event)
        self.connected_clients = set()
        if host_ip == 'localhost':
            self.host = 'localhost'
            self.port = host_port
        else:
            self.host = '0.0.0.0'
            self.port = host_port

    async def handle_client(self, websocket, path):
        logger.debug(f"{path} connected")
        self.connected_clients.add(websocket)
        try:
            while True:
                message = await websocket.recv()
                # TODO: Run this in its own thread? Why does it block?
                result = await self.process_input(message)
                # loop = asyncio.get_event_loop()
                # result = await loop.run_in_executor(None, self.process_input, message)
        except ConnectionClosed:
            logger.debug(f"{path} disconnected")
            self.connected_clients.remove(websocket)

    async def send_routine(self):
        # TODO: How can I properly break this loop?
        while not self.stop_event.is_set():
            # TODO: Use next 2 lines for synchronous action.
            # loop = asyncio.get_event_loop()
            # output = await loop.run_in_executor(None, self.send)
            output = await self.send()
            if not output: continue
            for ws in self.connected_clients:
                await ws.send(output)
        logger.debug('Broke out of send_routine')

    async def main(self):
        async with websockets.serve(self.handle_client, self.host, self.port):
            # asyncio.create_task(send_routine())
            # await asyncio.Future()
            task = self.send_routine()
            result = await task
            logger.debug("End of main reached")

    def run(self):
        asyncio.run(self.main())