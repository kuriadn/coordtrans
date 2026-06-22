from math import *
from anglemanip import AngleManip

class CassTable():

  def getIndex(self, val, arr):
    for i in range(0, len(arr)):
      #print ('Array[{0}] = {1}; Val = {2}'.format(i, arr[i], val))
      if arr[i] > val: break
    return i - 1

  def getAsp(self, val):
    asp = 1
    if val < 0: asp = -1
    return asp

  def getDiff(self, arr, idx):
    if idx > 0 and idx < len(arr):
      return arr[idx + 1] - arr[idx]
    elif idx <= 0: return arr[1] - arr[0]
    else:return arr[len(arr) - 1] - arr[len(arr) - 2]  

  def getLog(self, val):
    return float('{0:10.7f}'.format(val))

  def generateTables(self):
    phi = []
    ph = []
    rho = []
    nu = []
    rhonu2 = []
   
    for i in range(0, 6):
      ang = i
      for j in range(0, 6):
        mins = j * 10
        phi.append([ang, mins])
        ph.append(AngleManip().decDeg(ang, mins))
        rho.append(0)
        nu.append(0)
        rhonu2.append(0)

    roffset = 2.003
    noffset = 2.006
    rnoffset = 0.3749

    r = [3115, 3116, 3117, 3119,3121, 3125, 3129, 3134, 3139, 3145, 3153, 3160, 3169, 3178, 3188, 3199, 3211, 3223, 3236, 3250, 3265, 3280, 3296, 3313, 3330, 3349, 3368, 3387, 3408, 3429, 3451]
    n = [2683,2683, 2684, 2684, 2685, 2686, 2688, 2689, 2691, 2693, 2696,2698, 2701, 2704, 2707, 2711, 2715, 2719, 2723, 2728, 2733, 2738, 2743, 2749, 2755, 2761, 2767, 2774, 2781, 2788, 2795]
    mer = [0.0, 60459.2, 120918.5, 181377.8, 241837.1, 302296.5, 362755.9, 425215.3, 483674.9, 544154.5, 604594.2, 665054.0, 725514.0, 785974.1, 846434.5, 906894.6, 967355.1, 1027815.8, 1088276.6, 1148737.6, 1209198.8, 1269660.2, 1330121.9, 1390583.8, 1451045.9, 1511508.3, 1571970.9, 1632433.8, 1692897.0, 1753360.5, 1813824.2]
    rn = [65, 65, 65, 65, 64, 64, 63, 63, 62, 61, 60, 59, 58, 57, 55, 54, 52, 51, 49, 47, 45, 43, 41, 39, 36, 34, 31, 29, 26, 23, 20]

    for i in range(0, len(r)):
      rho[i] = roffset + r[i] * 10e-8
      nu[i] = noffset + n[i] * 10e-8
      rhonu2[i] = -10 + rnoffset + rn[i] * 10e-7
    return phi, ph, rho, nu, mer, rhonu2

  def computeGeog(self, x, y, cm):
    aspY = self.getAsp(y)
    Y = abs(y)
    aspX = self.getAsp(x)
    X = abs(x)
    phi, ph, rho, nu, mer, rhonu2 = self.generateTables()
    i = self.getIndex(Y, mer)
    #print ('index = {0}; value = {1}, diffMer = {2}'.format(i, mer[i], diffMer[i - 1]))
    diffY = Y - mer[i]
    #print ('Del Y: {0}'.format(diffMerY))
    delAng = diffY
    diff = self.getDiff(mer, i)

    if diff > 0: fract = diffY / diff
    else: fract = diffY / (mer[1] - mer[0])
    delAng = fract * 600
    delAng = float('{0:10.4f}'.format(delAng))
    #print ('Del Ang: {0}; \nang: {1},{2}'.format(delAng, phi[i][0], phi[i][1]))
    angle = phi[i][0] + phi[i][1]/60. + delAng/3600.
    #print angle
    ang = angle/180. * pi
    logtan = log10(tan(ang))
    #print ('Angle: {0}, \nLog(tan): {1}, \n2Log(tan): {2}'.format(angle, 1-logtan, 2+logtan))
    logx = log10(X)
    xlog2 = logx * 2
    logsin1sec = log10(sin(1./3600*pi/180.))
    n = nu[i] + fract * self.getDiff(nu, i)
    r = rho[i] + fract * self.getDiff(rho, i)
    rnu = -(n + r - logsin1sec + log10(2.))
    logn = xlog2 + logtan + rnu
    #print('Logx: {0}, \n2Logx: {1}, \n2rhoNuInv: {2}, \nLogn: {3}'.format(logx, xlog2,rnu, 1+logn))

    nn = 10 ** logn
    #print (angle, n, degMinSec(angle))
    lat = angle - nn/3600.
    lat = lat * aspY
    #print (angle)
    #print('Sin 1": {0}'.format(logsin1sec), rnu, rhonu2[i])

    #print degMinSec(angle)

    logsec = log10(1./cos(angle/180. * pi))
    #print(logsec)
    logdh = logx + logsec - n
    dh = 10 ** logdh
    #print (logdh, dh)
    #cm = 35.
    lon = cm + dh/3600. * aspX
    #print(degMinSec(lon))
    #print ('Aspects: {0}, {1}'.format(aspX, aspY))
    return lon, lat

  # ---------------------------------
  def computeCass(self, lon, lat, cm):
    phi, ph, rho, nu, mer, rhonu2 = self.generateTables()
    aspY = self.getAsp(lat)
    lt = abs(lat)
    if lt < 1e-10: i = 0
    else: i = self.getIndex(lt, ph)
    if lt < 1e-10: lt = 1e-10
    #print('Index: {0}, lat: {1}, lat0: {2}'.format(i, lat, ph[i]))
    yp = mer[i]
    delAng = lt - ph[i]
    diff = self.getDiff(mer, i)
    if i > 0: dy = delAng * 3600. * diff/600.
    else: dy = delAng * 3600. * (mer[1]-mer[0])/600.
    # print (yp, degMinSec(delAng), dy, delAng)
    fract = dy / diff
    #print ('Longitude: {0}'.format(lon))
    dh = (lon - cm) * 3600.
    aspX = self.getAsp(dh)
    #print ('DLong: {0}; \nAspect: {1}'.format(dh, aspX))
    dh = abs(dh)
    if dh<1e-10: dh = 1e-10
    logdh = log10(dh)
    logcos = log10(cos(lt * pi / 180.))
    logcos2 = 2. * logcos
    #print ('LogDlong: {0}, \nDlong: {1}, \nLogCos: {2}, \n2LogCos: {3}, '.format(logdh, dh, 1+logcos, 3+logcos2))
    logdh2 = logdh * 2
    logtan = log10(tan(lt * pi / 180.))
    n = nu[i] + self.getDiff(nu, i) * fract
    loghalf = log10(0.5)
    logsin = log10(sin(pi/(3600. * 180.)))
    #print ('2LogDlong: {0}, \nLogTan: {1}, \n nu: {2}, \nLogHalf: {3}, \nLogSin1Sec: {4}, \n2LogCos: {5}'.format(logdh2, 3+logtan, n, 1+loghalf, 6+logsin, 3+logcos2))
    logn = logdh2 + logcos2 + logtan + logsin + loghalf + n
    #print logn, 10**logn

    y = (yp + dy + 10 ** logn)  * aspY
    #print y

    logx = logdh + logcos + n
    #print (logx, 10 ** logx)
    x = 10 ** logx * aspX
    #print ('Aspects: {0}, {1}'.format(aspX, aspY))
    return x, y

CT = CassTable()
AM = AngleManip()

x = 359483.7; y = 235476.2

# 36.25, -1.25, 
x = -274132.0; y = -454129.2

# lon1 = decDeg(35,59,3.5492); lat1 = decDeg(0,38,56.5272)
#lon1 = 36.25; lat1 = -1.25 

lon = 34.25; lat = -0.25 
x0 = -273951.9; y0 = -90658.1
x = -273951.9; y = -90658.1
lon1 = 34.25; lat1 = -0.25 
#lon1 = decDeg(35,59,3.5492); lat1 = decDeg(0,38,56.5272)

#lon, lat = CT.computeGeog(x, y, 35)
#print (AM.degMinSec(lon), AM.degMinSec(lat))

x, y = CT.computeCass(lon, lat , 35)
print ('{0:9.2f} ft; {1:9.2f} ft'.format(x, y))

lon, lat = CT.computeGeog(x0, y0, 35)
print (AM.degMinSec(lon), AM.degMinSec(lat))

print(x-x0, y - y0, AM.degMinSec(lon-lon1)[2], AM.degMinSec(lat-lat1)[2])


