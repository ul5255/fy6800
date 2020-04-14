import math, serial, serial.tools.list_ports


ch = {1: 'M', 2: 'F'}
def dBm(v): return math.sqrt(math.pow(10.0, v/10.0)/2.5)*2.0
def MHz(v): return 1000*kHz(v)
def kHz(v): return 1000*Hz(v)
def Hz(v): return 1000*mHz(v)
def mHz(v): return 1000*uHz(v)
def uHz(v): return v

class FY6800(object):
    def req(self, cmd): self.port.write((cmd+'\n').encode())
    def resp(self): return self.port.readall().decode().rstrip('\n')

    def __init__(self):
        self.port = None
        for p in serial.tools.list_ports.grep('1A86'):
            self.port = serial.Serial(port=p.device, baudrate=115200, timeout=0.7)
            self.req('UMO')
            if self.resp().startswith('FY6800'): break
            self.port.close()
            self.port = None
        assert(self.port is not None)

    def a(self, n, v): self.req(f"W{ch[n]}A{v:02.4f}")

    def f(self, n, frq): self.req(f"W{ch[n]}F{frq:014d}")

    def arb(self, i, one_period):
        assert(i in range(1, 65))
        assert(len(one_period) == 2**13)
        # byte n: lower 8bit, byte n+1: upper 6bit
        seq = bytearray([])
        for v in one_period: seq += bytearray([v & 255, (v >> 8) & 63])
        self.req(f"DDS_WAVE{i:d}")
        assert(self.resp() == 'W')
        chunk_size = 2**8
        for j in range(0, len(seq), chunk_size): self.port.write(seq[j:j+chunk_size])
        assert(self.resp() == 'HN')
