"""Control Agilent instruments.

Supported models:

    Agilent 34410A/11A/L4411A 6.5 digit multimeters
    Agilent E8257D PSG analog signal generators

Agilent SCPI instructions: 

    "Agilent 34410A/11A/L4411A 6.5 Digit Multimeter Programmer's Reference"
    "SCPI Command Reference, Agilent Technologies, E8257D/67D PSG Signal Generators"

"""

from labinstruments.generic import GenericInstrument


class Agilent34411A(GenericInstrument):
    """Class to read data from an Agilent multimeter.

    Note:

        This has only been tested with a 34411A multimeter. The commands 
        should work with all Agilent 34410A/11A/L4411A 6.5 Digit Multimeters.

    Args:
        ip_address (string): IP address of the Agilent multimeter, e.g.,
            ``ip_address='192.168.0.3'``
        port (int, optional, default is 5025): the port set for Ethernet
            communication

    """

    def measure_dc_voltage(self, units="V"):
        """Measure DC voltage.

        Args:
            units (str): units for voltage measurement

        Returns:
            float: DC voltage

        """

        msg = 'MEAS:VOLT:DC?'
        return float(self._query(msg)) / _voltage_units(units)


class AgilentE8257D(GenericInstrument):
    """Class to control an Agilent signal generator.

    This has only been tested with an E8257D PSG analog signal generator, but
    it should also work for the E8267D model.

    Args:
        ip_address (string): IP address of the Agilent signal generator, e.g.,
            ``ip_address='192.168.0.31'``
        port (int, optional, default is 5025): the port set for Ethernet
            communication

    """

    def set_frequency(self, value, units="GHz"):
        """Set CW frequency in given units.

        Args:
            value (float): frequency
            units (str): frequency units, default is "GHz"

        """

        msg = ':FREQ {}{}'.format(value, units)
        self._send(msg)

    def get_frequency(self, units="GHz"):
        """Get CW frequency in given units.

        Args:
            units (str): frequency units

        Returns:
            str: frequency in selected units

        """

        msg = ':FREQ?'
        return float(self._query(msg)) / _frequency_units(units)

    def set_power(self, value, units="dBm"):
        """Set output power in given units.

        Args:
            value (float): power level 
            units (str): power units, default is "dBm"

        """

        msg = ":POW {}{}".format(value, units)
        self._send(msg)

    def get_power(self, units="dBm"):
        """Get CW output power in given units.

        Args:
            units (str): power units, default is "dBm"

        Returns:
            float: power in given units

        """

        # Set power output units
        # :UNIT:POWer DBM|DBUV|DBUVEMF|V|VEMF|DB
        msg = ":UNIT:POW {}".format(units)
        self._send(msg)

        # Get power
        # [:SOURce]:POWer[:LEVel][:IMMediate][:AMPLitude]?
        msg = ":POW?"
        return float(self._query(msg))

    def rf_power(self, state="off"):
        """Toggle RF power on or off.

        Args:
            state (str): "on" or "off" (or 1 or 0)

        """

        print("\nWarning: rf_power is depracted.")
        print("Please use either power_on or power_off\n")

        msg = ":OUTP {}".format(state)
        self._send(msg)

    def power_on(self):
        """Turn RF power on."""

        msg = ":OUTP ON"
        self._send(msg)

    def power_off(self):
        """Turn RF power off."""

        msg = ":OUTP OFF"
        self._send(msg)


# Helper functions -----------------------------------------------------------

def _voltage_units(units):
    """Get voltage multiplier."""
    voltage_units = {'mv': 1e-3, 'uv': 1e-6, 'v': 1}
    try:
        return voltage_units[units.lower()]
    except KeyError as e:
        print('Error: Voltage units must be one of V, mV, or uV')
        raise e

def _frequency_units(units):
    """Get frequency multiplier."""
    frequency_units = {'ghz': 1e9, 'mhz': 1e6, 'khz': 1e3, 'hz': 1}
    try:
        return frequency_units[units.lower()]
    except KeyError as e:
        print('Error: Frequency units must be one of GHz, MHz, kHz, or Hz')
        raise e


# Main -----------------------------------------------------------------------

if __name__ == "__main__":

    # remember to set the ip addresses below
    
    # Test multimeter (comment out if not connected)
    dmm = Agilent34411A("192.168.0.3", 5025)
    print("Multimeter: ", dmm.get_id())
    print("DC voltage: {:.2f} V".format(dmm.measure_dc_voltage('V')))
    print("DC voltage: {:.2f} mV".format(dmm.measure_dc_voltage('mV')))
    print("DC voltage: {:.2f} uV".format(dmm.measure_dc_voltage('uV')))
    dmm.close()

    # Test signal generator (comment out if not connected)
    sig = AgilentE8257D("192.168.0.31")
    print("Sig. Gen.: ", sig.get_id())
    sig.set_frequency(15, "GHz")
    sig.set_power(-20, "dBm")
    sig.rf_power("on")
    sig.close()
