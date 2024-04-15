import asyncio
import multiprocessing, queue, asyncio
from loguru import logger

from .classes import Server, Client

from dataclasses import dataclass
import json

@dataclass
class JSONMessage:
    type: str = None
    message: str = None
    dump: str = None

    def __post_init__(self):
        if self.dump is not None:
            dump = json.loads(self.dump)
            self.type = dump['type']
            self.message = dump['message']
        else:
            dump = {"type": self.type, "message": self.message}
            self.dump = json.dumps(dump)
    
@dataclass
class SystemMessage(JSONMessage):
    type: str = 'system'
    
@dataclass
class Message(JSONMessage):
    type: str = 'message'

class PipeSocket():
    def __init__(self, server_bool = False):
        self._send_q = multiprocessing.Queue()
        self._receive_q = multiprocessing.Queue()
        if server_bool:
            self._process = multiprocessing.Process(target=self.start_server)
        else:
            self._process = multiprocessing.Process(target=self.start_client)
        self._process.start()
    
    # def put(self, message):
    #     self._send_q.put(message)

    def put_message(self, message):
        message = Message(message=message)
        self._send_q.put(message.dump)

    # def get(self):
    #     message = self._receive_q.get()
    #     return message

    def process_message(self, message):
        if message.type == 'message':
            return message.message
        elif message.type == 'system':
            logger.debug(f"Received SystemMessage: {message.message}")
            return None

    
    def get_message(self):
        dump = self._receive_q.get()
        message = JSONMessage(dump=dump)
        return self.process_message(message)
    
    def get_message_nowait(self):
        try:
            dump = self._receive_q.get_nowait()
            message = JSONMessage(dump=dump)
            return self.process_message(message)
        except queue.Empty:
            return None
        
    
    # def get_nowait(self):
    #     try:
    #         message = self._receive_q.get_nowait()
    #         return message
    #     except queue.Empty:
    #         return None
        
    def system_message(self, message):
        system_message = SystemMessage(message=message)
        self._send_q.put(system_message.dump)

    # def receive_system_message(self):
    #     dump = self.get()
    #     system_message = SystemMessage(dump=dump)
    #     print(system_message)
    
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