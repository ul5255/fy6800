import math, serial, serial.tools.list_ports

ch = {1: 'M', 2: 'F'}
def dBm(v): return math.sqrt(math.pow(10.0, v/10.0)/2.5)*2.0
def MHz(v): return 1000*kHz(v)
def kHz(v): return 1000*Hz(v)
def Hz(v): return 1000*mHz(v)
def mHz(v): return 1000*uHz(v)
def uHz(v): return v

class FY6800(object):
    def w(self, chars): self.port.write((chars+'\n').encode())
    def r(self): return self.port.readall().decode().rstrip('\n')
    def cmd(self, chars): self.w(chars); return self.r()

    def __init__(self):
        self.port = None
        for p in serial.tools.list_ports.grep('1A86'):
            self.port = serial.Serial(port=p.device, baudrate=115200, timeout=0.7)
            if self.cmd('UMO').startswith('FY6800'): break
            self.port.close()
            self.port = None
        assert(self.port is not None)

    def amplitude(self, n, v): self.cmd(f"W{ch[n]}A{v:02.4f}")
    def frequency(self, n, frq): self.cmd(f"W{ch[n]}F{frq:014d}")
    def disable(self, n): self.cmd(f"W{ch[n]}N0")
    def enable(self, n): self.cmd(f"W{ch[n]}N1")

    def store_waveform(self, i, one_period):
        assert(i in range(1, 65))
        assert(len(one_period) == 2**13)
        assert(self.cmd(f"DDS_WAVE{i:d}") == 'W')
        # byte n: lower 8bit, byte n+1: upper 6bit
        for v in one_period: self.port.write(bytearray([v & 255, (v >> 8) & 63]))
        assert(self.r() == 'HN')
