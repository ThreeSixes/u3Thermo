u3Thermo is a python script does continuous readings from a thermocouple attached to a LabJack U3 via a LJTA-InAmp. It can be used from the command line or as a class.

Help message:

usage: u3Thermo.py [-h] [--cold] [--unit {c,C,f,F,k,K}] [--volts]
                   [--voffset VOFFSET] [--gain GAIN] [--channel CHANNEL]
                   [--tctype {C,B,E,D,G,IrRh 40-0,M,K,J,PtMo 5-0.1,N,P,S,R,Au-Pt,T,Pt-Pd,PtRh 40-20,AuFe 0.07}]
                   [--debug]

Thermocouple monitor

usage: u3Thermo.py [-h] [--cold] [--unit {c,C,f,F,k,K}] [--volts]
                   [--voffset VOFFSET] [--gain GAIN] [--channel CHANNEL]
                   [--tctype {C,B,E,D,G,IrRh 40-0,M,K,J,PtMo 5-0.1,N,P,S,R,Au-Pt,T,Pt-Pd,PtRh 40-20,AuFe 0.07}]
                   [--log] [--ofile OFILE] [--sid] [--interval INTERVAL]
                   [--debug]

Thermocouple monitor

optional arguments:
  -h, --help            show this help message and exit
  --cold                Display cold junction temperature.
  --unit {c,C,f,F,k,K}  Display temperatures in this unit. Defaults to Celsius
                        (C).
  --volts               Show thermocouple voltage?
  --voffset VOFFSET     Specify thermocouple offset voltage. Should be around
                        0.4 or 1.25, defaults to 0.4.
  --gain GAIN           Gain configured on the LabJack LJTick-InAmp. Defaults
                        to 51.
  --channel CHANNEL     Channel number with LabJack LJTick-InAmp attached to
                        it. Defaults to 0.
  --tctype {C,B,E,D,G,IrRh 40-0,M,K,J,PtMo 5-0.1,N,P,S,R,Au-Pt,T,Pt-Pd,PtRh 40-20,AuFe 0.07}
                        Type of thermocouple attached to LabJack LJTick-InAmp.
                        Defaults to type K.
  --log                 Activate data logging in Sqlite3 databases.
  --ofile OFILE         Output log filename. Defaults to log-yyyymmdd-
                        hhmmss.sqlite3 where yyyymmdd-hhmmss is the start time
                        when --log is asserted.
  --sid                 Display the sample ID while taking readings. The
                        default is to not display the sample ID.
  --interval INTERVAL   Interval at which to take readings in seconds.
                        Defaults to 1.0.
  --debug               Debug.

Requires a LabJack U3 device with a thermocouple attached to a LJTick-Inamp.
This software has only been tested against a LabJack U3-LV using its internal
temperature sensor as a cold junction thermometer.

Requirements:
- LabJack U3 and LJTick-InAmp device.
- Themocouple (must be supported by thermocouples_reference.)
- LabJack exodriver installed (https://github.com/labjack/exodriver)
- LabJack U3 driver installed (https://github.com/labjack/LabJackPython)
- thermocouples_reference installed (available via pip)
- Python Sqlite3 library for logging.
