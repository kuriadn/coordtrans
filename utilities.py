# Code developed by the NLIMS Directorate, National Land Commission
# This is free software to support Affine Transformation
# This is for the Cassini-Soldner to UTM transformations

# Prerequisites to running the code:
# 1. Python translation engine - python
# 2. Numpy for Matrix and array processing
# 3. Read write access on the machine it is to run on and the target output directory

from math import *
import numpy as nm
import sys, getopt
from numpy.linalg import inv
from pyproj import Proj, transform

def genCoeffMatrix(x):
# This function prepares the Matrix of Coefficients given an input vector
  n = len(x)
  j = 0
  mat = []
  for i in range(0, n//2):
  	tmp = []
  	tmp.append(x[j * 2 ])
  	tmp.append(-x[j * 2 +1])
  	tmp.append(1)
  	tmp.append(0)
  	mat.append(tmp)
  	tmp = []
  	tmp.append(x[j * 2 + 1])
  	tmp.append(x[j * 2])
  	tmp.append(0)
  	tmp.append(1)
  	mat.append(tmp)
  	j += 1
  return nm.array(mat)

def compute(x,l):
# This function computes the transformation parameters
# Matrix of coefficients
  A = genCoeffMatrix(x)

  L=l
  L=nm.transpose(L)
 
# Prepare system of equations
  AT=nm.transpose(A)
  ATA=nm.dot(AT, A)
  ATL=nm.dot(AT, L)
  ATAInv = inv(ATA)

# The solution
  x=nm.dot(ATAInv, ATL)
  L1 = nm.dot(A, x)

# The computation errors
  er=L1-L
  return x, er, ATAInv

def computeCass(lng0, lng, lat, inv='False'):
# Given geographic coordinates and the Central Meridian of the particular panel, computes 
# corresponding Cassini-Soldner coordinates 
  a = 6378293.645 /.3048
  f = 294.26 
  b = round(a - a / f, 3)

  lat0 = 0
  
  projStr = '+proj=cass +lat_0=' + str(lat0) + ' +lon_0=' + str(lng0) + ' +a=' + str(a) + ' +b=' + str(b) + ' +no_defs'

  p = Proj(projStr)
  if not inv:
    x, y = p(lng, lat, inverse = False)
    return round(x,2), round(y,2)
  else:
    lo, la = p(lng, lat, inverse=True)
    return lo, la

def decDeg(deg,min=0,sec=0):
  sgn = 1
  if deg < 0: sgn = -1
  dg = abs(deg)
  return (dg + min/60. + sec/3600.) * sgn

def degMinSec(deg):
  sgn = 1
  if deg < 0: sgn = -1
  dg = abs(deg)
  d = int(floor(dg))
  min = (dg - d)*60.
  m = int(floor(min))
  s = (min - m)*60.
  return [sgn * d, m, s] 

def deg2rad(deg):
  return deg * pi / 180.

def rad2deg(rad):
  return rad * 180. / pi

def getSgn(val):
  sgn = 1
  if val < 0:
    sgn = -1
  return sgn 
