"""Class to control Keithley power supplies.

Keithley SCPI commands can be found here:

    https://doc.xdevs.com/doc/Keithley/2280/077085501_2280_Reference_Manual.pdf

"""

import vxi11
import pyvisa as visa

from labinstruments.generic import GenericInstrumentVX11


class Keithley2280(GenericInstrumentVX11):
    """Control a Keithley 2280 power supply.

    Args:
        ip_address (string): IP address of the power supply, e.g.,
            "192.168.0.117"

    """

    def __init__(self, ip_address):

        super(self.__class__, self).__init__(ip_address)

        # Ask if output is on
        output = self._inst.ask(':OUTP?')
        self.output = output == '1'

    def set_voltage(self, voltage):
        """Set voltage.

        Args:
            voltage (float): voltage in units 'V'

        """

        self._inst.write(f':VOLT {voltage:.3f}')
        if self.output:
            _ = self.get_voltage()

    def set_voltage_limit(self, voltage):
        """Set voltage limit.

        Args:
            voltage (float): voltage limit in units 'V'

        """

        self._inst.write(f':VOLT:LIM {voltage:.3f}')
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

        self._inst.write(f':CURR {current:.3f}')
        if self.output:
            _ = self.get_current()

    def set_current_limit(self, current):
        """Set current limit.

        Args:
            current (float): current limit in units 'A'

        """

        self._inst.write(f':CURR:LIM {current:.3f}')
        if self.output:
            _ = self.get_current()

    def get_current(self):
        """Get current.

        Returns:
            float: current in units 'A'

        """

        self._inst.write(":FORM:ELEM \"READ\"")
        return self._inst.ask(':MEAS:CURR?')

    def power_on(self):
        """Turn on output power."""

        self._inst.write(':OUTP ON')
        self.output = True

    def power_off(self):
        """Turn off output power."""

        self._inst.write(':OUTP OFF')
        self.output = False

    def output_on(self):
        """Turn on output power."""

        self.power_on()

    def output_off(self):
        """Turn off output poewr."""

        self.power_off()


class Keithley2602:
    """Control a Keithley 2602 SourceMeter.

    Args:
        ip_address (string): IP address of the power supply, e.g.,
            "192.168.0.117"

    """

    def __init__(self, ip_address):

        rm = visa.ResourceManager()
        address = f"TCPIP0::{ip_address}::inst0::INSTR"
        self._inst = rm.open_resource(address)

        # Measurement speed
        self._write("smua.measure.nplc = 0.5")
        self._write("smub.measure.nplc = 0.5")

    def _write(self, command):

        self._inst.write(command)

    def _query(self, command):

        self._write("x = " + command)
        result = self._inst.query("print(x)")
        return float(result)

    def get_id(self):
        """Get identity of signal generator."""

        return self._inst.query("print([[Keithley Instruments Inc., Model]]..localnode.model..[[, ]]..localnode.serialno..[[, ]]..localnode.revision)").replace(', ', ' ').strip()

    def reset(self):
        """Reset instrument."""

        # Reset
        self._inst.write("smua.reset()")
        self._inst.write("smub.reset()")

    def set_voltage_limit1(self, voltage):
        """Set voltage limit.

        Args:
            voltage (float): voltage limit in units 'V'

        """

        self._write(f"smua.source.limitv = {voltage}")

    def set_voltage_limit2(self, voltage):
        """Set voltage limit.

        Args:
            voltage (float): voltage limit in units 'V'

        """

        self._write(f"smub.source.limitv = {voltage}")

    def get_voltage1(self):
        """Get voltage.

        Returns:
            float: voltage in units 'V'

        """

        # self._inst.write(":FORM:ELEM \"READ\"")
        return self._query("smua.measure.v()")

    def get_voltage2(self):
        """Get voltage.

        Returns:
            float: voltage in units 'V'

        """

        # self._inst.write(":FORM:ELEM \"READ\"")
        return self._query("smub.measure.v()")

    def set_current1(self, current, current_limit=0.150):
        """Set current.

        Args:
            current (float): current in units 'A'

        """

        if current > current_limit:
            print(f"Current too high! Limiting to {current_limit} A")
            current = current_limit

        self._write(f"smua.source.leveli = {current}")

    def set_current2(self, current, current_limit=0.150):
        """Set current.

        Args:
            current (float): current in units 'A'

        """

        if current > current_limit:
            print(f"Current too high! Limiting to {current_limit} A")
            current = current_limit
        
        self._write(f"smub.source.leveli = {current}")

    def get_current1(self):
        """Get current.

        Returns:
            float: current in units 'A'

        """

        return self._query("smua.source.leveli")

    def get_current2(self):
        """Get current.

        Returns:
            float: current in units 'A'

        """

        return self._query("smub.source.leveli")

    def output1_off(self):
        """Turn off output power (channel A)."""

        self._inst.write("smua.source.output = smua.OUTPUT_OFF")

    def output2_off(self):
        """Turn off output power (channel B)."""

        self._inst.write("smub.source.output = smub.OUTPUT_OFF")

    def output1_on(self):
        """Turn off output power (channel A)."""

        self._inst.write("smua.source.output = smua.OUTPUT_ON")

    def output2_on(self):
        """Turn off output power (channel B)."""

        self._inst.write("smub.source.output = smub.OUTPUT_ON")


# Main -----------------------------------------------------------------------

if __name__ == "__main__":

    # ps = Keithley2280('192.168.0.117')
    # ps.reset()
    # print(ps.get_id())

    # ps.output_on()
    # ps.set_voltage_limit(12)
    # ps.set_current(0.1)
    # ps.set_voltage(10)

    ps = Keithley2602("192.168.1.20")
    print(ps.get_id())
    ps.output1_off()
    ps.output2_off()
    ps.set_current1(0.005)
    ps.set_current2(0.010)
    ps.set_voltage_limit1(1.5)
    ps.set_voltage_limit2(1.5)
    print(ps.get_voltage1())
    print(ps.get_voltage2())
    print(ps.get_current1())
    print(ps.get_current2())
    ps.close()
