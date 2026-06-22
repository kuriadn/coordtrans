from math import *
from anglemanip import AngleManip

class CassFormula():

  def __init__(self, a, b):
    self.a = a
    self.b = b
    self.f = (a - b) / a
    self.e = (2 * self.f - self.f ** 2.) ** 0.5
    self.n = self.f / (2. - self.f)

  def getCoeffs(self):
    n = self.n
    a0 = 1. + n **2./4. + n ** 4. / 64.
    a2 = 3. / 2. * (n - n ** 3. / 8)
    a4 = 15. / 16. * (n ** 2. - n **4. / 4.)
    a6 = 35. / 48. * n ** 3.
    a8 = 315. / 512. * n ** 4.
    return a0, a2, a4, a6, a8

  def computeM(self, phi):
    a = self.a
    e = self.e
    M = a *((1 - e**2/4 - 3*e**4/64 - 5*e**6/256)* phi - (3*e**2/8 + 3*e**4/32 + 45*e**6/1024)*sin(2*phi) + (15*e**4/256 + 45*e**6/1024)*sin(4*phi) - (35*e**6/3072)*sin(6*phi))
    return M  

  def compMerDist(self, phi):
    n = self.n
    a = self.a
    a0, a2, a4, a6, a8 = self.getCoeffs()
    s = a * (a0 * phi - a2 * sin(2. * phi) + a4 * sin(4. * phi) - a6 * sin(6. * phi) + a8 * sin(8. * phi)) / (1. + n)
    return s

  def computeN(self, phi):
    a = self.a
    e = self.e 
    N = a / (1. - e ** 2. * sin(phi) ** 2.) ** 0.5
    return N

  def compMerLat(a, f, phi):
    a = self.a
    n = self.n
    a0, a2, a4, a6, a8 = self.getCoeffs()
    v = a * (a0  - a2 * 2. * cos(2. * phi) + a4 * 4. * cos(4. * phi) - a6 * 6. * cos(6. * phi) + a8 * 8. * cos(8. * phi)) / (1. + n)	
    return v

  def computePhiP(self, y):
    e = self.e
    a = self.a
    e1 = (1. - (1. - e**2.)**0.5)/(1. + (1. - e**2.)**0.5)
    M0 = self.computeM(0.)
    M1 = M0 + y
    mu1 = M1/(a*(1 - e**2/4 - 3*e**4/64 - 5*e**6/256))
    phiP = mu1 + (3*e1/2 - 27*e1**3/32)*sin(2*mu1) + (21*e1**2/16 - 55*e1**4/32)*sin(4*mu1) + (151*e1**3/96)*sin(6*mu1) + (1097*e1**4/512)*sin(8*mu1)
    return phiP

  def compCoords(self, ln, lt, cent):
    am = AngleManip()
    lat = am.deg2rad(lt)
    lon = am.deg2rad(ln)
    cm = am.deg2rad(cent)

    s = self.computeM(lat)
    v = self.computeN(lat)
    dlong = lon - cm
    dlcoslat = dlong * cos(lat)
    Y = s + v / 2. * (dlcoslat) ** 2. * tan(lat) + v / 24. * (dlcoslat) ** 4. * tan(lat) * (5 * v / s - tan(lat) ** 2.)
    X = v * dlcoslat - v / 6. * dlcoslat ** 3. * tan(lat) ** 2. + v / 120. * dlcoslat ** 5. * (tan(lat) ** 5. - 8. * tan(lat) ** 2.)
    return X, Y

  def compGeog(self, x, y, cent):
    cm = AngleManip().deg2rad(cent)
    #phi = compFootPtLat(a, f, y)
    phi = self.computePhiP(y)
    s = self.computeM(phi)
    v = self.computeN(phi)

    cubeTanPhi = 1. + 3. * tan(phi) ** 2.
    dphi = x ** 2. * tan(phi) / (s * v) - x ** 4. * tan(phi) * cubeTanPhi / (24. * s * v ** 3.)
    lat = (dphi + phi) * 180. / pi

    dlon = x / (v * cos(phi)) - x ** 3. * tan(phi) / (3. * v ** 3 * cos(phi)) + x ** 5 * tan(phi) ** 2. * cubeTanPhi / (15. * v ** 5. * cos(phi)) 
    lon = (cm + dlon) * 180. /pi 
    return lon, lat 

AM = AngleManip()
# 34.25, -0.25, -273951.9, -90658.1
a = 6378249.145 * 3.28
b = 6356514.966 * 3.28
CF = CassFormula(a, b)

# lon = AM.decDeg(37,11,54.8142)
# lat = AM.decDeg(3,15,44.4688)
lon = 34.25; lat = -0.25 

# lat = -0.25
# lon = 34.25
cm = 35
x, y = CF.compCoords(lon, lat, cm)
print x, y

#x = 21948.25
#y = -140572.25

lon, lat = CF.compGeog(x, y, cm)
lon = AM.degMinSec(lon)
lat = AM.degMinSec(lat)
print (lon, lat)



  