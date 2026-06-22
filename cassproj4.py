# +proj=cass +lat_0=22.31213333333334 +lon_0=114.1785555555556 +x_0=40243.57775604237 
# +y_0=19069.93351512578 +a=6378293.645208759 +b=6356617.987679838 +units=m +no_defs

# +proj=utm +zone=37 +south +a=6378249.145 +b=6356514.96582849 +towgs84=-160,-6,-302,0,0,0,0 
# +units=m +no_defs
from math import *
from pyproj import Proj, transform
from anglemanip import AngleManip

# a = 6378293.645 * 3.28084
# b = 6356617.988
# a = 20926160.922261797
# b = 20855046.55974992

class Cassini():

  def __init__(self, a, b):
    self.a = a
    self.b = b

  def getProjStrCass(self, phi0, lam0):
    projStr ='+proj=cass +lat_0={0} +lon_0={1} +a={2} +b={3} +units=m +no_defs'.format(phi0, lam0, self.a, self.b)
    return projStr

  def getCM(self, l):
    if ((l + 1)/2.0 - floor((l + 1)/2.0)) > 0.01: 
      lam0 = l + 1
    else: lam0 = l 
    return lam0

  def getCoords(self, lon, lat, lam0):
#    lam0 = self.getCM(floor(lon))
    csStr = self.getProjStrCass(0, lam0)
    cProj = Proj(csStr)
    cx, cy = cProj(lon, lat)
    return cx, cy

  def getGeog(self, x, y, lam0):
    csStr = self.getProjStrCass(0, lam0)
    print (csStr)
    cProj = Proj(csStr)
    lon, lat = cProj(x, y, inverse=True)
    return lon, lat
   
a = 20926348 
b = 20855233

CS = Cassini(a, b)
AM = AngleManip()

# lon = 34.25; lat = -0.25 
# x0 = -273951.9; y0 = -90658.1
# x = -273951.9; y = -90658.1
# lon1 = 34.25; lat1 = -0.25 

lon = 35.25; lat = 1.0
x = -306.2; y = 362084.3
x = 90995.6; y = 362094.9
#lat = 0.3989310882562347/3600.; lon = 34.+29./60.+59.70860143397431/3600.
#x0 = 359483.7; y0 = -235476.2
x0 = x; y0 = y
lon1 = lon; lat1 = lat 

x, y = CS.getCoords(lon, lat, 35)
lon, lat = CS.getGeog(x0, y0, 35)

print ('{0:9.2f} ft; {1:9.2f} ft'.format(x, y))

print (AM.degMinSec(lon), AM.degMinSec(lat))

print(x-x0, y - y0, AM.degMinSec(lon-lon1)[2], AM.degMinSec(lat-lat1)[2])

x, y = CS.getCoords(lon1, lat1, 35)
print ('{0:9.2f} ft; {1:9.2f} ft'.format(x, y))


