"""Generic instrument classes.

Can be used on their own or inherited.

"""


import socket
import telnetlib
import time

import pyvisa as visa
import vxi11


class GenericInstrument:
    """Control an instrument over LAN using SCPI commands.

    Args:
        ip_address (string): IP address of the instrument, e.g.,
            ``ip_address='192.168.0.3'``
        port (int, optional, default is 5025): the port set for Ethernet
            communication

    """

    def __init__(self, ip_address, port=5025, timeout=None, verbose=False):

        # Create socket
        try:
            self._inst = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if timeout:
                self._inst.settimeout(timeout)
        except socket.error as e:
            print('Error creating socket: %s' % e)
            sys.exit(1)

        # Connect to instrument
        try:
            self._inst.connect((ip_address, port))
        except socket.gaierror as e:
            print('Address-related error connecting to instrument: %s' % e)
            sys.exit(1)
        except socket.error as e:
            print('Error connecting to socket on instrument: %s' % e)
            sys.exit(1)

        # Get information about instrument
        self._id_str = self.get_id()
        self.verbose = verbose
        if self.verbose:
            print(f"Instrument: {self._id_str}")

    def close(self):
        """Close connection to instrument."""

        self._inst.close()

    def get_id(self):
        """Get instrument identity information."""

        self._send('*IDN?')
        return self._receive().replace(',', ' ').strip()

    def reset(self):
        """Reset instrument."""

        self._send("*RST")
    
    def _send(self, msg):
        """Send command to instrument.

        Args:
            msg (string): command to send

        """

        msg = msg + '\n'
        self._inst.send(msg.encode('ASCII'))

    def _receive(self):
        """Receive message from instrument.

        Returns:
            string: output from instrument

        """

        msg = self._inst.recv(1024).decode('ASCII')
        return msg.strip()

    def _receive_all(self):
        """Receive large messages from the instrument.

        Returns:
            string: output from instrument

        """

        BUFF_SIZE = 1024
        data = b''
        while True:
            time.sleep(0.01)
            part = self._inst.recv(1024)
            data += part
            if len(part) < 1024:
                break
        return data.decode('ASCII')

    def _query(self, msg):
        """Send message and then receive message from the instrument

        Returns:
            string: output from instrument

        """

        self._send(msg)
        return self._receive()

    
class GenericInstrumentVX11(GenericInstrument):
    """Control an instrument over LAN using SCPI commands using the VXI-11
    protocol.

    Args:
        ip_address (string): IP address of the instrument, e.g.,
            ``ip_address='192.168.0.3'``

    """

    def __init__(self, ip_address):

        # Connect to instrument
        self._inst = vxi11.Instrument(ip_address)

        # Get information about instrument
        self._id_str.get_id()


class GenericInstrumentTelnet:
    """Control an instrument using Telnet.

    Args:
        ip_address (string): IP address of the instrument, e.g.,
            ``ip_address='192.168.0.159'``

    """

    def __init__(self, ip_address):

        self._tn = telnetlib.Telnet(host=ip_address, port=23, timeout=3)
    
    def _write(self, msg):
        """Write via Telnet."""

        msg = msg + "\r\n"
        self._tn.write(msg.encode('ASCII'))

    def _query(self, msg):
        """Query via Telnet."""

        msg = msg + "\r\n"
        self._tn.write(msg.encode('ASCII'))
        results = self._tn.read_some().decode("utf-8")
        return results.replace('>', '').strip()

    def close(self):
        """Close connection."""

        self._tn.close()
