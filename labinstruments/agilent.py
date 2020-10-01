"""Control Agilent instruments.

Supported models:

    Agilent 34410A/11A/L4411A 6.5 digit multimeters
    Agilent E8257D PSG analog signal generators

Agilent SCPI instructions: 

    "Agilent 34410A/11A/L4411A 6.5 Digit Multimeter Programmer's Reference"
    "SCPI Command Reference, Agilent Technologies, E8257D/67D PSG Signal Generators"

"""

import os
import socket
import sys
import time


class Agilent34411A:
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

    def __init__(self, ip_address, port=5025):

        # Create socket
        try:
            self._skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            print('Error creating socket: %s' % e)
            sys.exit(1)

        # Connect to multimeter
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
        """Get identity of multimeter."""

        self._send('*IDN?')
        return self._receive()

    def reset(self):
        """Reset multimeter."""

        self._send("*RST")

    def measure_dc_voltage(self, units="V"):
        """Measure DC voltage.

        Args:
            units (str): units for voltage measurement

        Returns:
            float: DC voltage

        """

        msg = 'MEAS:VOLT:DC?'
        self._send(msg)
        dc_voltage = float(self._receive()) / _voltage_units(units)

        return dc_voltage

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


class AgilentE8257D:
    """Class to control an Agilent signal generator.

    This has only been tested with an E8257D PSG analog signal generator, but
    it should also work for the E8267D model.

    Args:
        ip_address (string): IP address of the Agilent signal generator, e.g.,
            ``ip_address='192.168.0.3'``
        port (int, optional, default is 5025): the port set for Ethernet
            communication

    """

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
        """Get identity of multimeter."""

        self._send('*IDN?')
        return self._receive()

    def reset(self):
        """Reset multimeter."""

        self._send("*RST")

    def set_frequency(self, value, units="GHz"):
        """Set CW frequency in given units.

        Args:
            value (float): frequency
            units (str): frequency units, default is "GHz"

        """

        msg = ':FREQ {}{}'.format(value, units)
        self._send(msg)

    def set_power(self, value, units="dBm"):
        """Set output power in given units.

        Args:
            value (float): power level 
            units (str): power units, default is "dBm"

        """

        msg = ":POW {}{}".format(value, units)
        self._send(msg)

    def rf_power(self, state="off"):
        """Toggle RF power on or off.

        Args:
            state (str): "on" or "off" (or 1 or 0)

        """

        msg = ":OUTP {}".format(state)
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

# Helper functions -----------------------------------------------------------

def _voltage_units(units):
    """Get voltage multiplier."""
    voltage_units = {'mv': 1e-3, 'uv': 1e-6, 'v': 1}
    try:
        return voltage_units[units.lower()]
    except KeyError as e:
        print('Error: Voltage units must be one of: V, mV, or uV')
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
