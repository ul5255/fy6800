import math
import serial
import serial.tools.list_ports

device = [_ for _ in serial.tools.list_ports.grep('1A86')][0].device
port = serial.Serial(port=device, baudrate=115200, timeout=0.7)


def req(cmd): port.write((cmd+'\n').encode())
def raw(bytes): port.write(bytes)
def resp(): port.readall().decode().rstrip('\n')


req('UMO')
assert(resp().startswith("FY6800"))

# Vpp on FY6800 is assuming open output
# we divide by 2 since we terminate into 50Ohms
# mW = lambda vpp: 2.5 * (vpp/2)**2
# dBm = lambda vpp: 10.0 * math.log10(mW(vpp))


def dBm(val): math.sqrt(math.pow(10.0, val/10.0)/2.5)*2.0
def ampl_1(v): req(f"WMA{v:02.4f}")
def ampl_2(v): req(f"WFA{v:02.4f}")
def MHz(v): 1000*kHz(v)
def kHz(v): 1000*Hz(v)
def Hz(v): 1000*mHz(v)
def mHz(v): 1000*uHz(v)
def uHz(v): v
def freq_1(frq): req(f"WMF{frq:014d}")
def freq_2(frq): req(f"WFF{frq:014d}")


def load_awf(i, one_period):
    assert(i in range(1, 17))
    assert(len(one_period) == 2**13)
    # byte n:   lower 8bit, byte n+1: upper 6bit
    seq = []
    for v in one_period: seq += [v & 255, (v >> 8) & 255]
    seq = bytearray(seq)
    req(f"DDS_WAVE{chr(i-1 + ord('1'))}")
    assert(resp() == 'W')
    chunk_size = 2**8
    for j in range(0, len(seq), chunk_size): raw(seq[j:j+chunk_size])
    assert(resp() == 'HN')


#   _
#  -/-\_---->
up = [v << 3 for v in range(2**11)]
down = [v << 3 for v in range(2**11-1, -1, -1)]

ramp = []
ramp += up
ramp += [2**14 - 1] * 2**11
ramp += down
ramp += [0] * 2**11

load_awf(1, ramp)
req('WMW00')  # ARB waveform #1
ampl_1(dBm(0))
freq_1(MHz(1)+kHz(456))

port.close()
