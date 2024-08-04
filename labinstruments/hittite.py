"""Classes to control Hittite signal generators.

Hittite SCPI commands can be found here:

    https://www.analog.com/media/en/technical-documentation/user-guides/hmc-t2200_family_programmers_guide_131547.pdf

"""

import os
import socket
import sys
import time

from labinstruments.generic import GenericInstrument

FREQ_UNIT_GHZ = {'hz': 1e-9, 'khz': 1e-6, 'mhz': 1e-3, 'ghz': 1}


class Hittite(GenericInstrument):
    """Control a Hittite signal generator.

    Note:

        This has only been tested with a HMC-T2240 signal generator. Some of
        the commands may differ for other models.

    Args:
        ip_address (string): IP address of the Hittite signal generator, e.g.,
            ``ip_address='192.168.0.159'``
        port (int, optional, default is 5025): the port set for Ethernet
            communication on the Hittite signal generator
        verbose (bool): verbosity

    """

    # TODO: Add power sweep ability
    # TODO: Add frequency sweep
    #     Start Continuous Sweep:
    #     freq:star 1e9;stop 2e9;step 100e6;mode swe
    #     swe:dwel 0.1
    #     init:cont on
    #     <let sweep run>
    #     init:cont off

    def set_frequency(self, freq, units='GHz'):
        """Set frequency.

        Args:
            freq (float): Frequency to set
            units (string, optional, default is 'GHz'): units for frequency

        """

        # Frequency in GHz
        freq_ghz = freq * FREQ_UNIT_GHZ[units.lower()]

        self._send(f'FREQ {freq_ghz:.9f} GHZ')

        if self.verbose:
            print(f"Signal generator: set frequency to {freq:.3f} {units}")

    def get_frequency(self, units='GHz'):
        """Get frequency of signal generator.

        Args:
            units (string, optional, default is 'GHz'): units for the returned
                frequency value

        Returns:
            float: frequency of signal generator

        """

        return float(self._query('FREQ?')) / _frequency_units(units)

    def set_power(self, power, units='dBm'):
        """Set power.

        Args:
            power (float): Power to set
            units (string, optional, default is 'dBm'): units for power

        """

        power = float(power)
        assert units.lower() == 'dbm', "Only dBm supported."
        
        self._send(f'POW {power} {units}')

        if self.verbose:
            print(f"Signal generator: set power to {power:.3f} {units}")

    def get_power(self):
        """Get power from signal generator.

        Returns:
            float: output power from signal generator

        """

        return float(self._query('POW?'))

    def power_off(self):
        """Turn off output power."""

        self._send('OUTP 0')

        if self.verbose:
            print("Signal generator: power off")

    def power_on(self):
        """Turn on output power."""

        self._send('OUTP 1')

        if self.verbose:
            print("Signal generator: power on")

    def get_output_state(self):
        """Get output on/off state from signal generator.

        Returns:
            float: output state (0/1) from signal generator

        """

        return int(self._query('OUTP:STAT?'))

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
