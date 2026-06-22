#! /Library/Frameworks/Python.framework/Versions/2.7/bin/python
# /usr/bin/python

from math import *
from pyproj import Proj, transform
from anglemanip import AngleManip

def computeGeog(a, e, phi0, x, y):
  phip = computePhiP(a, e, phi0, y)
  T1 = tan(phip)**2
  N1 = computeN(phip, a, e)
  R1 = a * (1 - e**2)/(1 - e**2 * sin(phip)**2)**1.5
  D = x/N1
  phi = phip - (N1*tan(phip)/R1)*(D**2/2 - (1 + 3*T1)*D**4/24)
  lam = lam0 + (D - T1*D**3/3 + (1 + 3*T1)*T1*D**5/15)/cos(phip)
  return [lam, phi]


def computePhi1(a, e, phi0, y):
  e1 = (1 - (1 - e**2)**0.5)/(1 + (1 - e**2)**0.5)
  M0 = computeM(phi0, a, e)
  M1 = M0 + y
  mu1 = M1/(a*(1 - e**2/4 - 3*e**4/64 - 5*e**6/256))
  phip = mu1 + (3*e1/2 - 27*e1**3/32)*sin(2*mu1) + (21*e1**2/16 - 55*e1**4/32)*sin(4*mu1) + (151*e1**3/96)*sin(6*mu1) + (1097*e1**4/512)*sin(8*mu1)
  return phip

def computeN(phi, a, e):
  N = a/(1-e**2 * sin(phi)**2)**0.5
  return N

def computeM(phi,a,e):
  M = a *((1 - e**2/4 - 3*e**4/64 - 5*e**6/256)* phi - (3*e**2/8 + 3*e**4/32 + 45*e**6/1024)*sin(2*phi) + (15*e**4/256 + 45*e**6/1024)*sin(4*phi) - (35*e**6/3072)*sin(6*phi))
  return M  

def computeCoords(a, e, phi, phi0, lam, lam0):
  N = computeN(phi, a, e)
  A = (lam - lam0) * cos(phi)
  T = tan(phi)**2
  C = e**2 * cos(phi)**2/(1 - e**2)
  M = computeM(phi,a,e)
  M0 = computeM(phi0,a,e)

  x = N * (A- T*A**3/6 -(8 - T + 8*C)*T*A**5/120)
  y = M - M0 + N * tan(phi)*(A**2/2 + (5 - T + 6*C)*A**4/24)
  return [x, y]

# Clarke 1858 ellipsoid parameters
# a = 6378293.645m; b = 6356617.988

# a = 20926348/3.28
# b = 20855233/3.28
a = 6378249.145 * 3.28
b = 6356514.966 * 3.28
# CF = CassFormula(a, b)

# lon = AM.decDeg(37,11,54.8142)
# lat = AM.decDeg(3,15,44.4688)
lam = 34.25; phi = -0.25 
x0 = -273951.9; y0 = -90658.1

AM = AngleManip()
lam0 = AM.deg2rad(35.)
lam = AM.deg2rad(lam)
phi = AM.deg2rad(phi)
#print (1/f)
e = ((a**2 - b**2)/a**2)**0.5
# phi0 = 0.182241463
# lam0 = -1.07046861
# lam = -1.08210414
# phi = 0.17453293

# y0 = 39.19
# x0 = -273955.3
# 34.25, -0.25, 

# lam0 = AM.deg2rad(AM.decDeg(37))
# lam = AM.deg2rad(AM.decDeg(37,11,54.8142))
# phi = AM.deg2rad(AM.decDeg(-1,15,44.4688))

#i = 0
phi0 = AM.deg2rad(AM.decDeg(0))
phi0 = phi0
projstr = '+proj=cass +lat_0=' + str(phi0*180/pi) + '0 +lon_0=' + str(lam0*180/pi) + ' +a=' + str(a) + ' +b=' + str(b) + ' +no_defs'

p=Proj(projstr)
x1,y1=p(AM.rad2deg(lam),AM.rad2deg(phi))
x,y = computeCoords(a, e, phi, phi0, lam, lam0)
#+x_0=-39.19 +y_0=39.19 
#projstr = '+proj=cass +lat_0=' + str(phi0*180/pi) + '0 +lon_0=' + str(lam0*180/pi) + ' +ellps=clrk80 +no_defs'
print(x1,y1)
print(x, y)

#lo,la = p(-273951.9,-90658.1,inverse=True)
#print(lo,la)
#print(degMinSec(lo),degMinSec(la))
#print(degMinSec(rad2deg(phi0)))
print (x0 - x, y0 - y)
