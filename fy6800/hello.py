from fy6800 import FY6800, dBm, MHz, kHz, Hz

g = FY6800()
g.disable(1)
g.disable(2)

#
#  ^   ___
#  |  /   \
#  +-/-----\----->
#  |/       \___
#
up = [v << 3 for v in range(2**11)]
high = [2**14 - 1] * 2**11
down = [v << 3 for v in range(2**11-1, -1, -1)]
low = [0] * 2**11

g.store_waveform(61, up+high+down+low)

g.cmd('WMW00')
g.amplitude(1, dBm(0))
g.frequency(1, MHz(1)+kHz(456))
g.enable(1)
