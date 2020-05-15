"""Class to read data from Siglent oscilloscopes.

Supported models:

    ...

Siglent SCPI instructions: 

    "Digital Oscilloscopes, Programming Guide, PG01-E02C"

"""

import os
import socket
import sys
import time


class Siglent:
    """Class to read data from Siglent oscilloscopes.

    Note:

        This has only been tested with an SDS1104X-E oscilloscope.

    Args:
        ip_address (string): IP address of the Siglent oscilloscope, e.g.,
            ``ip_address='192.168.0.10'``
        port (int, optional, default is 5025): the port set for Ethernet
            communication

    """

    def __init__(self, ip_address='192.168.0.10', port=5025):

        # Create socket
        try:
            self._skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            print('Error creating socket: %s' % e)
            sys.exit(1)

        # Connect to oscilloscope
        try:
            self._skt.connect((ip_address, port))
        except socket.gaierror as e:
            print('Address-related error connecting to instrument: %s' % e)
            sys.exit(1)
        except socket.error as e:
            print('Error connecting to socket on instrument: %s' % e)
            sys.exit(1)

    def _send(self, msg):
        """Send command to instrument.

        Args:
            msg (string): command to send

        """

        msg = msg + '\n'
        self._skt.send(msg.encode('ASCII'))

    def _receive(self):
        """Receive message from instrument.

        Returns:
            string: output from instrument

        """

        msg = self._skt.recv(1024).decode('ASCII')
        return msg.strip()
        
    def close(self):
        """Close connection to instrument."""

        self._skt.close()

    def get_id(self):
        """Get identity of oscilloscope."""

        self._send('*IDN?')
        return self._receive()

    def reset(self):
        """Reset oscilloscope."""

        self._send("*RST")

    def measure_rms_voltage(self, channel=1):
        """Measure RMS voltage.

        Args:
            units (str): units for voltage measurement

        Returns:
            float: DC voltage

        """

        # Set mode
        msg = 'PACU RMS,C{}'
        self._send(msg.format(channel))

        time.sleep(0.2)

        # Read RMS voltage
        msg = "C{}:PAVA? RMS"
        self._send(msg.format(channel))
        value = self._receive()

        return float(value.split(',')[-1][:-1])


if __name__ == "__main__":

    osc = Siglent()
    print(osc.get_id())

