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
    def __init__(self, host_ip = 'localhost', host_port = 8765):
        self._send_q = multiprocessing.Queue()
        self._receive_q = multiprocessing.Queue()
        self.host_ip = host_ip
        self.host_port = host_port
        self.stop_event = multiprocessing.Event()
    
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
            if message.message == 'closeconnection':
                logger.debug('Received Close Connection request')
                self.stop_event.set()
            else:
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

    def close_connection(self):
        self.put_system_message('closeconnection')


class ServerPipeSocket(PipeSocket):
    def __init__(self, host_ip = 'localhost', host_port = 8765):
        super().__init__(host_ip, host_port)
        self._process = multiprocessing.Process(target=self.start_server)
        self._process.start()

    def start_server(self):
        self.server = Server(self.host_ip, self.host_port, self._send_q, self._receive_q, self.stop_event)
        self.server.run()
        

class ClientPipeSocket(PipeSocket):
    def __init__(self, host_ip = 'localhost', host_port = 8765):
            super().__init__(host_ip, host_port)
            self._process = multiprocessing.Process(target=self.start_client)
            self._process.start()   
    
    def start_client(self):
        self.client = Client(self.host_ip, self.host_port, self._send_q, self._receive_q, self.stop_event)
        self.client.run()