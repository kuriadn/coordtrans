from math import *

class AngleManip():

  def decDeg(self, deg, min=0, sec=0):
    sgn = 1
    if deg < 0: sgn = -1
    dg = abs(deg)
    return (dg + min/60. + sec/3600.) * sgn

  def degMinSec(self, deg):
    sgn = 1
    if deg < 0: sgn = -1
    dg = abs(deg)
    d = int(floor(dg))
    min = (dg - d)*60.
    m = int(floor(min))
    s = (min - m)*60.
    return [sgn * d, m, s] 

  def deg2rad(self, deg):
    return deg * pi / 180.

  def rad2deg(self, rad):
    return rad * 180. / pi

#  def computeUTM():

