from fy6800 import FY6800, dBm, MHz, kHz, Hz


g = FY6800()

#    _
#  -/-\_---->
up = [v << 3 for v in range(2**11)]
high = [2**14 - 1] * 2**11
down = [v << 3 for v in range(2**11-1, -1, -1)]
low = [0] * 2**11

g.arb(1, up+high+down+low)

g.req('WMW00')
g.a(1, dBm(0))
g.f(1, MHz(1)+kHz(456))
