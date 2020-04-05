"""Main module."""
import math
import serial
import serial.tools.list_ports
import time

device = [_ for _ in serial.tools.list_ports.grep('1A86')][0].device
#port = serial.Serial(port=device, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, rtscts=False, dsrdtr=False, xonxoff=False, timeout=0.7, write_timeout=0.7)
port = serial.Serial(port=device, baudrate=115200, timeout=0.7)

req = lambda cmd: port.write((cmd+'\n').encode())
raw = lambda bytes: port.write(bytes)
resp = lambda: port.readall().decode().rstrip('\n')

req('UMO')
assert(resp().startswith("FY6800"))

# Vpp on FY6800 is assuming open output
# we divide by 2 since we terminate into 50Ohms
# mW = lambda vpp: 2.5 * (vpp/2)**2
# dBm = lambda vpp: 10.0 * math.log10(mW(vpp))
dBm = lambda val: math.sqrt(math.pow(10.0, val / 10.0) / 2.5)*2.0
ampl_1 = lambda v: req(f"WMA{v:02.4f}")
ampl_2 = lambda v: req(f"WFA{v:02.4f}")

MHz = lambda v: 1000 * kHz(v)
kHz = lambda v: 1000 * Hz(v)
Hz  = lambda v: 1000 * mHz(v)
mHz = lambda v: 1000 * uHz(v)
uHz = lambda v: v
freq_1 = lambda frq: req(f"WMF{frq:014d}")
freq_2 = lambda frq: req(f"WFF{frq:014d}")

def load_awf(i, one_period):
    assert(i in range(1,17))
    assert(len(one_period) == 2**13)
    # byte n:   lower 8bit, byte n+1: upper 6bit
    seq = []
    for v in one_period: seq += [v&255, (v>>8)&255]
    seq = bytearray(seq)
    req(f"DDS_WAVE{chr(i-1 + ord('1'))}")
    assert(resp() == 'W')
    chunk_size = 2**8
    for j in range(0, len(seq), chunk_size): raw(seq[j:j+chunk_size])
    assert(resp() == 'HN')


#  _
#-/-\_---->
up =  [v<<3 for v in range(2**11)]
down = [v<<3 for v in range(2**11-1, -1, -1)]

ramp = []
ramp += up
ramp += [2**14 - 1] * 2**11
ramp += down
ramp += [0] * 2**11

load_awf(1, ramp)
req('WMW00') # ARB waveform #1
ampl_1(dBm(0))
freq_1(MHz(1)+kHz(456))

port.close()
