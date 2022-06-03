"""Control Rohde & Schwarz instruments.

Supported models:
    
    FSVA-40

SCPI documentation: 

    
    https://scdn.rohde-schwarz.com/ur/pws/dl_downloads/dl_common_library/dl_manuals/gb_1/f/fsv_1/FSVA_FSV_UserManual_en_13.pdf

"""

import os
import socket
import sys
import time

import numpy as np


class RohdeSchwarzFSVA40:
    """Class to read data from a Rohde & Schwarz FSVA-40 spectrum analyzer.

    Args:
        ip_address (string): IP address, e.g., ``ip_address='192.168.0.3'``
        port (int, optional, default is 5025): the port set for Ethernet communication

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
        return self._receive().replace(',', ' ')

    def reset(self):
        """Reset multimeter."""

        self._send("*RST")

    # Settings ---------------------------------------------------------------

    def _set_frequency_value(self, command, f, units):

        self._send(f"{command} {f:.6f} {units.upper()}")

    def set_min_frequency(self, f, units='ghz'):

        self._set_frequency_value("FREQ:STAR", f, units)

    def set_max_frequency(self, f, units='ghz'):

        self._set_frequency_value("FREQ:STOP", f, units)

    def set_center_frequency(self, f, units='ghz'):

        self._set_frequency_value("FREQ:CENT", f, units)

    def set_span(self, f, units='ghz'):

        self._set_frequency_value("FREQ:SPAN", f, units)

    def set_rbw(self, f, units='mhz'):

        self._set_frequency_value("BAND:RES", f, units)

    def set_vbw(self, f, units='mhz'):

        self._set_frequency_value("BAND:VID", f, units)

    def set_vbw_auto(self, state="ON"):

        self._send(f"BAND:VID:AUTO {state}")

    def set_rbw_auto(self, state="ON"):

        self._send(f"BAND:RES:AUTO {state}")

    def set_bw_ratio(self, ratio=30):

        self._send(f"BAND:VID:RAT {1/ratio:.2f}")

    # Sweep ------------------------------------------------------------------

    def single_sweep(self):

        self._send("SWE:CONT OFF")

    def continuous_sweep(self):

        self._send("SWE:CONT ON")

    def start_and_wait(self):

        self._send("INIT")
        self._send("SYST:DISP:UPD ON")
        self.wait_for_completion()

    def wait_for_completion(self):

        self._query("*OPC?")

    # Averaging --------------------------------------------------------------

    def averaging_state(self, state="ON", n_trace=1):

        self._send(f"AVER:STAT{n_trace:d} {state.upper()}")

    def averaging(self, averaging=40):

        self._send(f"AVER:COUN {averaging:d}")

    def averaging_type(self, avg_type="power"):

        self._send(f"AVER:TYPE {avg_type.upper()}")

    # Marker -----------------------------------------------------------------

    def marker_state(self, state="ON", n_marker=1):

        self._send(f"CALC:MARK{n_marker:d} {state.upper()}")

    def marker_frequency(self, f_ghz, n_marker=1):

        self._send(f"CALC:MARK{n_marker:d}:X {f_ghz*1000:.6f}MHz")

    def marker_value(self, n_marker=1):

        return self._query(f"CALC:MARK{n_marker:d}:Y?")

    def marker_peak_search(self, state='on', n_marker=1):

        self._send(f"CALC:MARK{n_marker:d}:MAX:AUTO {state.upper()}")

    # Trace ------------------------------------------------------------------

    def get_trace(self):

        self._send("TRAC:DATA:X? TRACE1")
        x = np.array([float(val) for val in self._receive_all().split(',')])
        self._send("TRAC:DATA? TRACE1")
        y = np.array([float(val) for val in self._receive_all().split(',')])
        
        return x, y

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

    def _receive_all(self):

        BUFF_SIZE = 1024
        data = b''
        while True:
            time.sleep(0.01)
            part = self._skt.recv(1024)
            data += part
            if len(part) < 1024:
                break
        return data.decode('ASCII')

    def _query(self, msg):

        self._send(msg)
        return self._receive()


if __name__ == "__main__":

    import matplotlib.pyplot as plt 
    plt.style.use(['science', 'notebook'])

    # Connect to instrument
    speca = RohdeSchwarzFSVA40("192.168.1.40")
    print("\n" + speca.get_id())

    # Frequency range
    speca.set_center_frequency(7, 'ghz')
    speca.set_span(10, 'mhz')

    # Averaging
    speca.averaging(100)
    speca.averaging_state("on")

    # Resolution / video bandwidth
    speca.set_rbw_auto("off")
    speca.set_vbw_auto("off")
    speca.set_bw_ratio(3)
    speca.set_rbw(0.010)

    # Run sweep (wait for completion)
    speca.single_sweep()
    speca.start_and_wait()

    # Set marker
    speca.marker_state("on", 1)
    speca.marker_peak_search("on", 1)
    time.sleep(0.1)
    speca.marker_peak_search("off", 1)
    time.sleep(0.1)

    # Measure power at marker frequency
    print("\n\tPower: " + speca.marker_value() + " dBm")

    # Grab entire trace
    trace_x, trace_y = speca.get_trace()
    plt.figure()
    plt.plot(trace_x / 1e9, trace_y)
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Power (dBm)")
    plt.show()

    print("")
    speca.continuous_sweep()
    speca.close()
