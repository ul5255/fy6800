import math
import serial
import serial.tools.list_ports


__port = None
def req(cmd): __port.write((cmd+'\n').encode())
def raw(bytes): __port.write(bytes)
def resp(): return __port.readall().decode().rstrip('\n')
def ch(i): return ['M', 'F'][i-1]

def open():
    global __port
    for p in serial.tools.list_ports.grep('1A86'):
        __port = serial.Serial(port=p.device, baudrate=115200, timeout=0.7)
        req('UMO')
        if resp().startswith('FY6800'): break
        __port.close()
        __port = None
    assert(__port is not None)

def dBm(v): math.sqrt(math.pow(10.0, v/10.0)/2.5)*2.0
def a(n, v): req(f"W{ch(n)}A{v:02.4f}")

def MHz(v): 1000*kHz(v)
def kHz(v): 1000*Hz(v)
def Hz(v): 1000*mHz(v)
def mHz(v): 1000*uHz(v)
def uHz(v): v
def f(n, frq): return f"W{ch(n)}F{frq:014d}"

def arb(i, one_period):
    assert(i in range(1, 17))
    assert(len(one_period) == 2**13)
    # byte n: lower 8bit, byte n+1: upper 6bit
    seq = []
    for v in one_period: seq += [v & 255, (v >> 8) & 63]
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

open()

arb(1, ramp)
req('WMW00')
a(1, dBm(0))
f(1, MHz(1)+kHz(456))

__port.close()
