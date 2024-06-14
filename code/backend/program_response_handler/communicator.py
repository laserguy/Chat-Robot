# copied file from the main branch of speech_system

import socket
import time
import threading
import struct
import queue
from queue import SimpleQueue
from enum import Enum, auto

import logging
logger = logging.getLogger(__name__)


class SocketStatus(Enum):
    CONNECTED = auto()
    DISCONNECTED = auto()
    CONNECTING = auto()


class IOSocket:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(2)
        self.status = SocketStatus.DISCONNECTED
        self.input = InputClient(self.s)
        self.output = OutputClient(self.s)

    def stop(self):
        print(f'Try closing the socket ({self.ip}, {self.port}).')
        self.input.is_running = False
        self.output.is_running = False
        if self.input.is_alive():
            self.input.join()
        if self.output.is_alive():
            self.output.join()
        self.status = SocketStatus.DISCONNECTED
        self.s.close()
        print(f'Closed connection to socket ({self.ip}, {self.port}).')

    def send_message(self, msg):
        self.output.message_queue.put(msg, block=True)
        print(f'Send Message with {len(msg)} bytes to socket ({self.ip}, {self.port}): \n' + msg)

    def try_to_receive(self, timeout: float = None):
        try:
            msg = self.input.message_queue.get(block=True, timeout=timeout)
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        if msg != '':
            print(f'Received Message with {len(msg)} bytes from socket ({self.ip}, {self.port}): ' + str(msg))
        else:
            print(f'Received empty message from socket ({self.ip}, {self.port})')
            self.status = SocketStatus.DISCONNECTED
            self.stop()
        return msg

    def connect_blocking(self, attempts: int = None):
        self.status = SocketStatus.CONNECTING
        try:
            while True:
                print(f"Trying to connect to socket ({self.ip}, {self.port}).")
                if self.__try_connect():
                    print("Connection established.")
                    self.status = SocketStatus.CONNECTED
                    self.input.start()
                    self.output.start()
                    break
                time.sleep(2)
                if attempts:
                    attempts -= 1
                    if attempts < 1:
                        self.status = SocketStatus.DISCONNECTED
                        break
        except KeyboardInterrupt:
            print("Connection Attempt was interrupted.")
            raise RuntimeError("Connection Attempt was interrupted")

    def __try_connect(self) -> bool:
        try:
            address = (self.ip, self.port)
            self.s.connect(address)
            return True
        except (ConnectionRefusedError, socket.timeout):
            return False


class InputClient(threading.Thread):
    def __init__(self, s):
        threading.Thread.__init__(self)
        self.message_queue = SimpleQueue()
        self.s = s
        self.is_running = False

    def __del__(self):
        self.is_running = False

    def run(self):
        self.is_running = True
        while self.is_running:
            try:
                msg = self.__receive_message()
            except socket.timeout:
                continue
            if msg == '':
                self.is_running = False
            self.message_queue.put(msg, block=True)

    def __receive_message(self) -> str:
        try:
            byte_count = int.from_bytes(struct.unpack('q', self.s.recv(8)), "big")
            return self.s.recv(byte_count)
        except ConnectionResetError:
            return ''
        except struct.error:
            return ''


class OutputClient(threading.Thread):
    def __init__(self, s):
        threading.Thread.__init__(self)
        self.message_queue = SimpleQueue()
        self.s = s
        self.is_running = False

    def __del__(self):
        self.is_running = False

    def run(self):
        self.is_running = True
        while self.is_running:
            msg = self.__pull_message()
            if msg == '':
                break
            self.__send_message(msg)

    def __pull_message(self):
        msg = None
        while not msg:
            try:
                msg = self.message_queue.get(block=True, timeout=0.3)
            except queue.Empty:
                if not self.is_running:
                    return ''
                continue
        return msg

    def __send_message(self, msg: str):
        byte_count = len(msg)
        b = msg.encode()
        self.s.sendall(byte_count.to_bytes(4, 'big'))
        self.s.sendall(b)
        #print("Message sent: ", msg)
        logger.info("Message sent:", msg)
