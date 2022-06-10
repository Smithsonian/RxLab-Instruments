"""Class to read data from Siglent oscilloscopes.

Supported models:

    SDS 1104X-E

Siglent SCPI instructions: 

    "Digital Oscilloscopes, Programming Guide, PG01-E02C"

"""

import os
import socket
import sys
import time

from labinstruments.generic import GenericInstrument


class SiglentSDS1104XE(GenericInstrument):
    """Class to read data from Siglent oscilloscopes.

    Supported models (confirmed):

        SDS 1104X-E

    Args:
        ip_address (string): IP address of the Siglent oscilloscope, e.g.,
            ``'ip_address='192.168.0.10'``
        port (int, optional, default is 5025): the port set for Ethernet
            communication

    """

    def measure_rms_voltage(self, channel=1, average=1):
        """Measure rms voltage.

        Args:
            channel (int): channel
            average (int): averaging

        Returns:
            float: rms voltage

        """

        # Set mode
        msg = 'PACU RMS,C{}'
        self._send(msg.format(channel))

        time.sleep(0.2)

        # Read RMS voltage
        rms_voltage = 0
        msg = "C{}:PAVA? RMS"
        for _ in range(average):
            self._send(msg.format(channel))
            value = self._receive()
            rms_voltage += float(value.split(',')[-1][:-1])

        return rms_voltage / average


if __name__ == "__main__":

    osc = SiglentSDS1104XE()
    print(osc.get_id())
    print(osc.measure_rms_voltage(channel=1, average=10))
