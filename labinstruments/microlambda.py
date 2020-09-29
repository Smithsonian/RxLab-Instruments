"""Classes to control the Micro Lambda Wireless, Inc. YIG filter.

Note:

    It communicates over Ethernet via Telnet.

    It also uses it's own set of instructions (not SCPI).

"""

import telnetlib

FREQ_UNIT = {'hz': 1e-6, 'khz': 1e-3, 'mhz': 1, 'ghz': 1e3}


class YigFilter:
    """Control the YIG filter from Micro Lambda Wireless (MLBF series).

    Note: 

        Uses Telnet.
        
        This has only been tested on an MLBF series bench test filter.

    Args:
        ip_address (string): IP address of the Yig filter, e.g.,
            ``ip_address='192.168.0.159'``

    """

    def __init__(self, ip_address):

        self._tn = telnetlib.Telnet(ip_address)
    
    def _write(self, msg):
        """Write via Telnet."""

        msg = msg + "\r\n"
        self._tn.write(msg.encode('ASCII'))

    def set_frequency(self, freq, units='GHz'):
        """Set frequency.

        Args:
            freq (float): Frequency to set
            units (string, optional, default is 'GHz'): units for frequency

        """

        freq = freq * FREQ_UNIT[units.lower()]
        msg = 'F{:.5f}'.format(float(freq))

        self._write(msg)

    def close(self):
        """Close connection."""

        self._tn.close()
