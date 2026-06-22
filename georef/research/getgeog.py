from math import *
from pyproj import Proj, transform
import sys

#print sys.argv
zone = sys.argv[1]
aspStr = sys.argv[2]
x = float(sys.argv[3])
y = float(sys.argv[4])
projStr = '+proj=utm +zone={0} +ellps=clrk80'.format(zone)
print projStr
p = Proj(projStr)
lo, la = p(x, y, inverse=True)
print('Longitude={0:6.2f}; Latitude={1:6.2f}'.format(lo, la))
