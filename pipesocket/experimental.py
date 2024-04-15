import asyncio
import multiprocessing, queue, asyncio
import json
from loguru import logger
from dataclasses import dataclass

from .classes import Server, Client

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
    def __init__(self, server_bool = False, host_ip = 'localhost'):
        self._send_q = multiprocessing.Queue()
        self._receive_q = multiprocessing.Queue()
        self.host_ip = host_ip
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
    
    def get_nowait(self):
        try:
            message = self._receive_q.get_nowait()
            return message
        except queue.Empty:
            return None

    def put_message(self, message):
        message = Message(message=message)
        self._send_q.put(message.dump)
        
    def get_message(self):
        dump = self._receive_q.get()
        message = JSONMessage(dump=dump)
        return self.get_message_process(message)
    
    def get_message_nowait(self):
        try:
            dump = self._receive_q.get_nowait()
            message = JSONMessage(dump=dump)
            return self.get_message_process(message)
        except queue.Empty:
            return None
    
    def get_message_process(self, message):
        if message.type == 'message':
            return message.message
        elif message.type == 'system':
            logger.debug(f"Received SystemMessage: {message.message}")
            return None
        
    def put_system_message(self, message):
        system_message = SystemMessage(message=message)
        self._send_q.put(system_message.dump)

    def receive_stream_message(self):
        system_message = SystemMessage(message='stream start')
        self._send_q.put(system_message.dump)
        keepReceiving = True
        while keepReceiving:
            dump = self._receive_q.get()
            message = JSONMessage(dump=dump)
            logger.debug(f'received: {message}')
            if message.type == 'system' and message.message == 'stream stop':
                keepReceiving = False
        logger.debug('Receive stream ended')


    
    def start_server(self):
        self.server = BetterServer(self.host_ip, self._send_q, self._receive_q)
        self.server.run()

    def start_client(self):
        self.client = BetterClient(self.host_ip, self._send_q, self._receive_q)
        self.client.run()


class BetterServer(Server):
    def __init__(self, host_ip, send_q, receive_q):
        super().__init__(host_ip)
        self.send_q = send_q
        self.receive_q = receive_q
    
    async def process_input(self, input):
        self.receive_q.put(input)
        return True

    async def send(self):
        try:
            message = self.send_q.get_nowait()
            return message
        except queue.Empty:
            await asyncio.sleep(0.1)

class BetterClient(Client):
    def __init__(self, host_ip, send_q, receive_q):
        super().__init__(host_ip)
        self.send_q = send_q
        self.receive_q = receive_q

    async def process_input(self, input):
        self.receive_q.put(input)
        return True

    async def send(self):
        try:
            message = self.send_q.get_nowait()
            return message
        except queue.Empty:
            await asyncio.sleep(0.1)