Receiver Lab Instruments
========================

Control various instruments in the Receiver Lab over LAN.

Installation
------------

To install via ``pip``:

```bash
# From the GitHub repo (latest version)
python3 -m pip install git+https://github.com/Smithsonian/RxLab-Instruments.git

# From PyPI (latest stable release)
python3 -m pip install RxLab-Instruments
```

To use Keithley instruments, you need to install the ``vxi11`` package:

```bash
python3 -m pip install git+https://github.com/python-ivi/python-vxi11.git
```

To use Rohde & Schwarz instruments, you need to install the ``pyvisa`` package:

```bash
python3 -m pip install -U pyvisa
```

**Note:** I have not added these packages to the requirements in ``setup.py`` because this allows you to decide which packages you want/need to install. For example, if you only want to use the Hittite module, you don't need to install ``vxi11`` or ``pyvisa``.

Supported Instruments
---------------------

- Agilent 34410A/11A/L4411A 6.5 Digit Multimeter
- Agilent E8257D/67D PSG Analog Signal Generator
- Hittite HMC-T2240 Signal Generator
- Keithley 2280 Power Supply
- Keithley 2602 Source Meter
- Micro Lambda Wireless (MLBF series) YIG Tuned Filters
- Micro Lambda Wireless YIG Tuned Synthesizers
- Rohde & Schwarz FSVA40 Spectrum Analyzer
- Siglent SDS-1104X-E Oscilloscope

This package will probably also work with closely related instruments, but I have only tested this package with the instruments listed above.

Example
-------

```python
from labinstruments.agilent import Agilent34411A, AgilentE8257D
from labinstruments.hittite import Hittite
from labinstruments.keithley import Keithley2280
from labinstruments.microlambda import YigFilter

# Agilent multimeter
dmm = Agilent34411A("192.168.0.3")
print("DC voltage: {:.2f} V".format(dmm.measure_dc_voltage('V')))
dmm.close()

# Agilent signal generator
sig = AgilentE8257D("192.168.0.31")
sig.set_frequency(15, "GHz")
sig.set_power(-20, "dBm")
sig.power_on()
sig.close()

# Connect to Hittite signal generator
sg = Hittite('192.168.0.159')
sg.set_power(-40, 'dBm')
sg.set_frequency(5, 'GHz')
sg.power_on()
sg.close()

# Connect to Keithley power supply
ps = Keithley2280('192.168.0.117')
ps.reset()
ps.output_on()
ps.set_voltage_limit(12)
ps.set_voltage(2)
ps.set_current(0.1)
ps.power_on()
ps.close()

# Connect to Micro Lambda YIG filter
yig = YigFilter('192.168.0.3')
yig.set_frequency(5, 'GHz')
yig.close()
```

References
----------

["System Power Supply Programming Using SCPI Commands"](https://www.keysight.com/us/en/assets/7018-06572/white-papers/5992-3841.pdf) from Keysight

["Control a Siglent oscilloscope with Python"](https://ktln2.org/2018/02/20/control-siglent-oscilloscope/)
