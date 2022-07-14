"""Control Rohde & Schwarz instruments.

Supported models:
    
    FSVA-40: spectrum analyzer

SCPI documentation: 
    
    https://scdn.rohde-schwarz.com/ur/pws/dl_downloads/dl_common_library/dl_manuals/gb_1/f/fsv_1/FSVA_FSV_UserManual_en_13.pdf

"""

import time

import numpy as np

from labinstruments.generic import GenericInstrument


class RohdeSchwarzFSVA40(GenericInstrument):
    """Class to control a Rohde & Schwarz FSVA-40 spectrum analyzer.

    Args:
        ip_address (string): IP address, e.g., ``ip_address='192.168.0.3'``
        port (int, optional, default is 5025): the port set for Ethernet communication

    """

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

    def set_reference_level(self, level=0, units="dBm"):

        if isinstance(level, float) or isinstance(level, int):
            self._send(f"DISP:TRAC:Y:RLEV {level:.0f}{units}")
        elif level.lower() == "auto":
            self._send("ADJ:LEV")

    def set_attenuation(self, attenuation):

        if isinstance(attenuation, float) or isinstance(attenuation, int):
            self._send(f"INP:ATT {attenuation:.0f}dB")
        elif attenuation.lower() == "auto":
            self._send("INP:ATT:AUTO ON")

    # Sweep ------------------------------------------------------------------

    def single_sweep(self):

        self._send("SWE:CONT OFF")
        self._send("INIT")

    def continuous_sweep(self):

        self._send("SWE:CONT ON")
        self._send("INIT")

    def sweep(self, count=1, wait=True, verbose=False):

        self._send(f"SWE:COUN {count:d}")
        self._send("SWE:CONT OFF")
        self._send("SYST:DISP:UPD ON")
        self._send("INIT")
        if wait:
            return self.wait(count=count, verbose=verbose)
        else:
            pass

    def wait(self, count=1, verbose=False):

        if verbose:
            print("\t\tWaiting for sweep...")
        start_time = time.time()
        time.sleep(0.1)
        current_count = 0
        while current_count < count:
            current_count = self.get_count()
            time.sleep(0.01)
        total_time = time.time() - start_time
        if verbose:
            print(f"\t\t-> sweep time: {total_time:.2f} s")
        return count

    def set_sweep_points(self, n_pts):

        self._send(f"SWE:POIN {n_pts}")

    def set_sweep_time(self, sweep_time):

        if isinstance(sweep_time, str) and sweep_time.lower() == 'auto':
            self._send(f"SWE:TIME:AUTO ON")
        else:
            self._send(f"SWE:TIME:AUTO OFF")
            self._send(f"SWE:TIME {sweep_time:.3f}s")

    def set_sweep_type(self, sweep_type="auto"):

        self._send(f"SWE:TYPE {sweep_type.upper()}")

    def get_count(self):

        return int(self._query("SWE:COUN:CURR?"))

    # Averaging --------------------------------------------------------------

    def set_averaging_state(self, state="ON", n_trace=1):

        self._send(f"AVER:STAT{n_trace:d} {state.upper()}")

    def set_averaging(self, averaging=40):

        self._send(f"AVER:COUN {averaging:d}")

    def set_averaging_type(self, avg_type="power"):

        self._send(f"AVER:TYPE {avg_type.upper()}")

    # Marker -----------------------------------------------------------------

    def set_marker_state(self, state="ON", n_marker=1):

        self._send(f"CALC:MARK{n_marker:d} {state.upper()}")

    def set_marker_frequency(self, freq, units="GHz", n_marker=1):

        self._send(f"CALC:MARK{n_marker:d}:X {freq:.6f}{units}")

    def get_marker_value(self, n_marker=1):

        return self._query(f"CALC:MARK{n_marker:d}:Y?")

    def set_marker_peak_search(self, state='on', n_marker=1):

        self._send(f"CALC:MARK{n_marker:d}:MAX:AUTO {state.upper()}")

    # Trace ------------------------------------------------------------------

    def get_trace(self):

        self._send("TRAC:DATA:X? TRACE1")
        x = np.array([float(val) for val in self._receive_all().split(',')])
        self._send("TRAC:DATA? TRACE1")
        y = np.array([float(val) for val in self._receive_all().split(',')])
        
        return x, y

    # External mixer ---------------------------------------------------------

    def set_external_mixer_state(self, state="ON"):

        self._send(f"MIX {state.upper()}")

    def set_external_mixer_band(self, band="F"):

        self.set_external_mixer_state("ON")
        self._send(f"MIX:HARM:BAND {band.upper()}")

    def set_external_mixer_signal_detection(self, state="AUTO"):

        self.set_external_mixer_state("ON")
        self._send(f"MIX:SIGN {state.upper()}")


if __name__ == "__main__":

    import matplotlib.pyplot as plt
    import scipy.constants as sc 
    plt.style.use(['science', 'notebook'])

    khz, mhz, ghz = sc.kilo, sc.mega, sc.giga

    # Parameters
    fcenter_ghz = 7
    fspan_mhz = 10
    sweep_npts = 401
    rbw_khz = 100
    vbw_khz = rbw_khz / 30
    averaging = 100

    # Connect to instrument
    speca = RohdeSchwarzFSVA40("192.168.1.40")
    print("\n" + speca.get_id())

    # Frequency range
    speca.set_center_frequency(fcenter_ghz, 'ghz')
    speca.set_span(fspan_mhz, 'mhz')
    speca.set_sweep_points(sweep_npts)

    # Resolution / video bandwidth
    speca.set_rbw_auto("off")
    speca.set_rbw(rbw_khz, 'khz')
    speca.set_vbw_auto("off")
    speca.set_vbw(vbw_khz, 'khz')
    speca.set_sweep_time("auto")
    speca.set_sweep_type("fft")

    # Averaging
    speca.averaging(averaging)
    speca.averaging_state("on")

    # Run sweep (wait for completion)
    speca.sweep(count=averaging)

    # Set marker
    speca.marker_state("on", 1)
    speca.marker_frequency(fcenter_ghz, 'ghz')

    # Measure power at marker frequency
    p_peak = float(speca.marker_value())

    # Grab entire trace
    trace_x, trace_y = speca.get_trace()

    # Background
    temperature = 295  # K
    bg = 10 * np.log10(sc.k * temperature * rbw_khz * khz)  # dBm/RBW

    # Normalize
    norm = np.mean(trace_y[:75]) - bg

    print(f"\n\tPeak power:       {p_peak - norm:7.1f} dBm")
    print(f"\n\tBackground:       {bg:7.1f} dBm / {rbw_khz:.0f} kHz")
    print(f"\n\tSignal-to-noise:  {p_peak - norm - bg:7.1f} dB")
    print(f"\n\tConversion gain:  {norm:7.1f} dB")

    plt.figure()
    plt.plot(trace_x / ghz, trace_y - norm, label='Data')
    plt.plot(fcenter_ghz, p_peak - norm, 'r*', label=f"Peak: {p_peak - norm:.1f} dBm", ms=10)
    plt.axhline(bg, c='k', ls='--', label=f"BG: {bg:.1f} dBm/RBW")
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Power (dBm)")
    plt.legend(fontsize=12)
    plt.title(f"{fcenter_ghz:.1f} GHz, RBW = {rbw_khz:.0f} kHz, averaging = {averaging:d}")
    plt.show()

    print("")
    speca.continuous_sweep()
    speca.close()
