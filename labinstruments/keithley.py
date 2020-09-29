"""Class to control Keithley power supplies.

Keithley SCPI commands can be found here:

    https://doc.xdevs.com/doc/Keithley/2280/077085501_2280_Reference_Manual.pdf

"""

import vxi11


class Keithley2280:
    """Control a Keithley 2280 power supply.

    Args:
        ip_address (string): IP address of the power supply, e.g.,
            "192.168.0.117"

    """

    def __init__(self, ip_address):

        self._inst = vxi11.Instrument(ip_address)

        self.id = self.get_id()

        # Ask if output is on
        output = self._inst.ask(':OUTP?')
        self.output = output == '1'

    def close(self):
        """Close connection to instrument."""

        self._inst.close()

    def get_id(self):
        """Get identity of signal generator."""

        return self._inst.ask('*IDN?')

    def reset(self):
        """Reset instrument."""

        self._inst.write("*RST")

    def set_voltage(self, voltage):
        """Set voltage.

        Args:
            voltage (float): voltage in units 'V'

        """

        msg = ':VOLT {}'.format(float(voltage))
        self._inst.write(msg)
        if self.output:
            _ = self.get_voltage()

    def set_voltage_limit(self, voltage):
        """Set voltage limit.

        Args:
            voltage (float): voltage limit in units 'V'

        """

        msg = ':VOLT:LIM {}'.format(float(voltage))
        self._inst.write(msg)
        if self.output:
            _ = self.get_voltage()

    def get_voltage(self):
        """Get voltage.

        Returns:
            float: voltage in units 'V'

        """

        self._inst.write(":FORM:ELEM \"READ\"")
        return self._inst.ask(':MEAS:VOLT?')

    def set_current(self, current):
        """Set current.

        Args:
            current (float): current in units 'A'

        """

        msg = ':CURR {}'.format(float(current))
        self._inst.write(msg)
        if self.output:
            _ = self.get_current()

    def set_current_limit(self, current):
        """Set current limit.

        Args:
            current (float): current limit in units 'A'

        """

        msg = ':CURR:LIM {}'.format(float(current))
        self._inst.write(msg)
        if self.output:
            _ = self.get_current()

    def get_current(self):
        """Get current.

        Returns:
            float: current in units 'A'

        """

        self._inst.write(":FORM:ELEM \"READ\"")
        return self._inst.ask(':MEAS:CURR?')

    def power_off(self):
        """Turn off output power."""

        msg = ':OUTP OFF'
        self._inst.write(msg)
        self.output = False

    def output_off(self):
        """Turn off output poewr."""

        self.power_off()

    def power_on(self):
        """Turn on output power."""

        msg = ':OUTP ON'
        self._inst.write(msg)
        self.output = True

    def output_on(self):
        """Turn on output power."""

        self.power_on()


# Main -----------------------------------------------------------------------

if __name__ == "__main__":

    ps = Keithley2280('192.168.0.117')
    ps.reset()
    print(ps.get_id())

    ps.output_on()
    ps.set_voltage_limit(12)
    ps.set_current(0.1)
    ps.set_voltage(10)
