"""Classes to control Hittite signal generators.

Note:

    Hittite SCPI commands can be found here:

        https://www.analog.com/media/en/technical-documentation/user-guides/hmc-t2200_family_programmers_guide_131547.pdf

"""

import os
import socket
import sys
import time


class Hittite:
    """Control a Hittite signal generator.

    Note:

        This has only been tested with a HMC-T2240 signal generator. Some of
        the commands may differ for other models.

    Args:
        ip_address (string): IP address of the Hittite signal generator, e.g.,
            ``ip_address='192.168.0.159'``
        port (int, optional, default is 5025): the port set for Ethernet
            communication on the Hittite signal generator

    """

    # TODO: Add power sweep ability
    # TODO: Add frequency sweep
    #     Start Continuous Sweep:
    #     freq:star 1e9;stop 2e9;step 100e6;mode swe
    #     swe:dwel 0.1
    #     init:cont on
    #     <let sweep run>
    #     init:cont off

    def __init__(self, ip_address, port=5025):

        # Create socket
        try:
            self._skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            print('Error creating socket: %s' % e)
            sys.exit(1)

        # Connect to signal generator
        try:
            self._skt.connect((ip_address, port))
        except socket.gaierror as e:
            print('Address-related error connecting to instrument: %s' % e)
            sys.exit(1)
        except socket.error as e:
            print('Error connecting to socket on instrument: %s' % e)
            sys.exit(1)

    def close(self):
        """Close connection to instrument."""

        self._skt.close()

    def get_id(self):
        """Get identity of signal generator."""

        self._send('*IDN?')
        return self._receive()

    def set_frequency(self, freq, units='GHz'):
        """Set frequency.

        Args:
            freq (float): Frequency to set
            units (string, optional, default is 'GHz'): units for frequency

        """

        msg = 'FREQ {} {}'.format(float(freq), units)
        self._send(msg)

    def get_frequency(self, units='GHz'):
        """Get frequency of signal generator.

        Args:
            units (string, optional, default is 'GHz'): units for the returned
                frequency value

        Returns:
            float: frequency of signal generator

        """

        msg = 'FREQ?'
        self._send(msg)
        freq = float(self._receive())

        return freq / _frequency_units(units)

    def set_power(self, power, units='dBm'):
        """Set power.

        Args:
            power (float): Power to set
            units (string, optional, default is 'dBm'): units for power

        """

        assert units.lower() == 'dbm', "Only dBm supported."

        msg = 'POW {} {}'.format(float(power), units)
        self._send(msg)

    def get_power(self):
        """Get power from signal generator.

        Returns:
            float: output power from signal generator

        """

        msg = 'POW?'
        self._send(msg)
        power = float(self._receive())

        return power

    def power_off(self):
        """Turn off output power."""

        msg = 'OUTP 0'
        self._send(msg)

    def power_on(self):
        """Turn on output power."""

        msg = 'OUTP 1'
        self._send(msg)

    # Helper functions -------------------------------------------------------
    
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


class SignalGenerator(Hittite):
    """For backwards compatibility with Bob's code...
    
    Bob uses camelCase for all of his method names (see below).

    """

    def setFreq(self, freq):
        """Set frequency in GHz.

        Args:
            freq (float): frequency in GHz

        """

        self.set_frequency(freq, units='GHz')

    def getFreq(self):
        """Get frequency in GHz.

        Returns:
            float: frequency in GHz

        """

        return self.get_frequency(units='GHz')

    def setPower(self, power):
        """Set power in dBm.

        Args:
            power (float): power in dBm

        """

        self.set_power(power, units='dBm')

    def getPower(self):
        """Get power in dBm.

        Returns:
            float: power in dBm

        """

        return self.get_power()

    def powerOff(self):
        """Turn off output power."""

        self.power_off()

    def powerOn(self):
        """Turn on output power."""

        self.power_on()


# Helper functions -----------------------------------------------------------

def _frequency_units(units):
    """Get frequency multiplier."""
    freq_units = {'ghz': 1e9, 'mhz': 1e6, 'khz': 1e3, 'hz': 1}
    try:
        return freq_units[units.lower()]
    except KeyError as e:
        print('Error: Frequency units must be one of: GHz, MHz, kHz or Hz')
        raise e


# Main -----------------------------------------------------------------------

if __name__ == "__main__":

    sg = Hittite('192.168.0.159')
    sg.set_frequency(5, 'GHz')
    sg.set_power(-38, 'dBm')
    sg.power_off()

