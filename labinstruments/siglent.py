import socket
import os
import sys
import time

class Siglent:

    def __init__(self):

        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.skt.connect(('192.168.0.10', 5025))

    def _send(self, msg):

        msg = msg + '\n'
        self.skt.send(msg.encode('ASCII'))

    def _receive(self):

        msg = self.skt.recv(1024).decode('ASCII')
        return msg.strip()

    def get_idn(self):

        self._send('*IDN?')
        return self._receive()

if __name__ == "__main__":

    osc = Siglent()
    print(osc.get_idn())

