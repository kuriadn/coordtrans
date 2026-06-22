# +proj=cass +lat_0=22.31213333333334 +lon_0=114.1785555555556 +x_0=40243.57775604237 
# +y_0=19069.93351512578 +a=6378293.645208759 +b=6356617.987679838 +units=m +no_defs

# +proj=utm +zone=37 +south +a=6378249.145 +b=6356514.96582849 +towgs84=-160,-6,-302,0,0,0,0 
# +units=m +no_defs
from math import *
from pyproj import Proj, transform

def getProjStrUTM(zone, n_or_s):
  aspStr = '+north'
  if n_or_s in ('s', 'S', 'south', 'South'):
  	aspStr = '+south'
  projStr = '+proj=utm +zone={0} {1} +ellps=clrk80'.format(zone, aspStr)
  return projStr
  
def getProjStrCass(phi0, lam0):
  projStr ='+proj=cass +lat_0={0} +lon_0={1} +a=6378293.645 +b=6356617.988 +units=m +no_defs'.format(phi0, lam0)
  return projStr

def printZone(phi1,phi2,lam1,lam2, fl):
  phi0 = 0.
  #lam0 = 33

  f = open(fl, 'w')
  for i in range(lam1,lam2):
    if i < 36: zone = 36
    else: zone = 37
    if ((i+1)/2.0 - floor((i+1)/2)) > 0:lam0 = i+1 
    print ('lam0={0}'.format(lam0))
    for k in range (phi1,phi2):
      asp = 'n'
      if k<0: asp = 's'
      for j in range(0,4):
        if (i/2.0 - floor(i/2)) > 0:lam0 = i 
        lam = i + j/60.*15.0
        fc = open('cas{0}.asc'.format(lam0),'a')
      #print 'cas{0}_{1}.asc'.format(i, asp)
        csStr = getProjStrCass(phi0, lam0)
        csProj = Proj(csStr)
        for l in range (0,4):
          phi = k + l/60.*15.0
          utmStr = getProjStrUTM(zone, asp)
          utmProj = Proj(utmStr)
          print ('lam={0}'.format(lam))
        #print ('i={0}, j={1}, lam={2}, phi={3}, lam0={4}'.format(i+1, j+1, lam, phi, lam0))
          cx, cy = csProj(lam, phi)
          ux, uy = utmProj(lam, phi)
          #print ('long={0:10.6f}; lat={1:10.6f}; UTM: x={2:10.2f}; y={3:10.2f}; Cassini: x={4:10.2f}; y={5:10.2f}'.format(lam, phi, ux, uy, cx, cy))
          #print ('{0:10.6f}; {1:10.6f}; {2:10.2f}; {3:10.2f}; {4:10.2f}; {5:10.2f}'.format(lam, phi, ux, uy, cx, cy))
          f.write ('{0:10.6f}; {1:10.6f}; {2:10.2f}; {3:10.2f}\n'.format(lam, phi, ux, uy))
          fc.write ('{0:10.6f}; {1:10.6f}; {2:10.2f}; {3:10.2f}\n'.format(lam, phi, cx, cy))
      fc.close()
  f.close()

#Zone 36 South
printZone(-5, 0, 32, 36, 'utm36s.asc')
#Zone 37 South
printZone(-5, 0, 36, 42, 'utm37s.asc')
#Zone 36 North
printZone(0, 6, 32, 36, 'utm36n.asc')
#Zone 37 North
printZone(0, 6, 36, 42, 'utm37n.asc')

