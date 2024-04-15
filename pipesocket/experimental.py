import asyncio
import multiprocessing, queue, asyncio
from loguru import logger

from .classes import Server, Client

class PipeSocket():
    def __init__(self, server_bool = False):
        self._send_q = multiprocessing.Queue()
        self._receive_q = multiprocessing.Queue()
        if server_bool:
            self._process = multiprocessing.Process(target=self.start_server)
        else:
            self._process = multiprocessing.Process(target=self.start_client)
        self._process.start()
    
    def put(self, message):
        self._send_q.put(message)

    def get(self):
        message = self._receive_q.get()
        return message
    
    def start_server(self):
        self.server = BetterServer(self._send_q, self._receive_q)
        self.server.run()

    def start_client(self):
        self.client = BetterClient(self._send_q, self._receive_q)
        self.client.run()


class BetterServer(Server):
    def __init__(self, send_q, receive_q):
        super().__init__()
        self.send_q = send_q
        self.receive_q = receive_q
    
    async def process_input(self, input):
        # return super().process_input(input)
        # logger.debug(f"Client received: {input}")
        self.receive_q.put(input)
        return True

    async def send(self):
        try:
            message = self.send_q.get_nowait()
            # logger.debug(message)
            return message
        except queue.Empty:
            # logger.debug("Queue was empty")
            await asyncio.sleep(0.3)
            # return "Nope"

class BetterClient(Client):
    def __init__(self, send_q, receive_q):
        super().__init__()
        self.send_q = send_q
        self.receive_q = receive_q

    async def process_input(self, input):
        # return super().process_input(input)
        # logger.debug(f"Client received: {input}")
        self.receive_q.put(input)
        return True

    async def send(self):
        try:
            message = self.send_q.get_nowait()
            # logger.debug(message)
            return message
        except queue.Empty:
            # logger.debug("Queue was empty")
            await asyncio.sleep(0.3)
            # return "Nope"