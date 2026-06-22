from math import *
from pyproj import Proj, transform
import sys

#print sys.argv
lng0 = sys.argv[1]
lng = sys.argv[2]
lat = sys.argv[3]

a = 6378293.645 /.3048

#a = 31706587.88
f = 294.26 #06764

b = round(a - a / f, 3)

lat0 = 0
projStr = '+proj=cass +lat_0=' + str(lat0) + ' +lon_0=' + lng0 + ' +a=' + str(a) + ' +b=' + str(b) + ' +no_defs'

print projStr

p = Proj(projStr)
x, y = p(lng, lat)
print('X={0:6.2f}m; Y={1:6.2f}m'.format(x, y))
