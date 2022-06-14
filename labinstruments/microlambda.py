"""Classes to control the Micro Lambda Wireless, Inc. YIG filter.

Note:

    It communicates over Ethernet via Telnet.

    It also uses it's own set of instructions (not SCPI).

"""

from labinstruments.generic import GenericInstrumentTelnet

FREQ_UNIT = {'hz': 1e-6, 'khz': 1e-3, 'mhz': 1, 'ghz': 1e3}


class YigFilter(GenericInstrumentTelnet):
    """Control the YIG filter from Micro Lambda Wireless (MLBF series).

    Note: 

        Uses Telnet.
        
        This has only been tested on an MLBF series bench test filter.

    Args:
        ip_address (string): IP address of the Yig filter, e.g.,
            ``ip_address='192.168.0.159'``

    """

    def __init__(self, ip_address):

        super(self.__class__, self).__init__(ip_address)

        self._freq_string = "F{:.3f}"

        # Read start up lines
        msg1 = self._tn.read_some()
        msg2 = self._tn.read_some()
        msg3 = self._tn.read_some()
        msg4 = self._tn.read_some()

    def get_id(self):

        fmin_ghz = float(self._query("R0003")) / 1000
        fmax_ghz = float(self._query("R0004")) / 1000

        return "Micro Lambda Wireless Inc. " + \
               self._query("R0000") + " " + \
               self._query("R0001") + " " + \
               self._query("R0002") + \
               f" ({fmin_ghz:.0f} to {fmax_ghz:.0f} GHz)"

    def set_frequency(self, freq, units='GHz'):
        """Set frequency.

        Args:
            freq (float): Frequency to set
            units (string, optional, default is 'GHz'): units for frequency

        """

        # Frequency in MHz
        freq = freq * FREQ_UNIT[units.lower()]

        # Message to instrument
        msg = self._freq_string.format(float(freq))
        self._write(msg)


class YigSynthesizer(YigFilter):

    def __init__(self, ip_address):

        super(self.__class__, self).__init__(ip_address)

        self._freq_string = "F{:.6f}"


if __name__ == "__main__":

    yig_filter = YigFilter("192.168.1.12")
    print(yig_filter.get_id())