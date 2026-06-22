from math import *
from pyproj import Proj, transform
import numpy as nm
import sys, getopt
from numpy.linalg import inv
from anglemanip import AngleManip

def getProjStrCass(phi0, lam0):
  projStr ='+proj=cass +lat_0={0} +lon_0={1} +a=20926348 +b=20855233 +units=m +no_defs'.format(phi0, lam0)
  return projStr
#print sys.argv
f=open('Cass_obs.asc','r')
lo = []
la = []
cx = []
cy = []
for line in f:
  data = line.split(',')
  if len(data) > 0:
    lo.append(float(data[0]))
    la.append(float(data[1]))
    cx.append(float(data[2]))
    cy.append(float(data[3]))
f.close()
phi0 = 0.0
CX = []
CY = []
fo = open('cass_comp.asc','w')
for i in range(0, len(lo)):
  l = floor(lo[i])
  if ((l + 1)/2.0 - floor((l + 1)/2.0)) > 0.01: 
  	lam0 = l + 1
  else: lam0 = l 
  print (lam0)
  csStr = getProjStrCass(phi0, lam0)
  cPrj = Proj(csStr)
  x, y = cPrj(lo[i], la[i])
  CX.append(x)
  CY.append(y)
  fo.write('{0:9.1f}, {1:9.1f}, {2:9.1f}, {3:9.1f}\n'.format(cx[i],CX[i], cy[i], CY[i]))
  print ('Long={0:6.2f}; Lat={1:6.2f}; origX={2:9.1f}; origY={3:9.1f}; compX={4:9.1f}; compY={5:9.1f}'.format(lo[i],la[i],cx[i], cy[i], x, y))
fo.close()

mat = []
obs = []
for i in range(0, len(lo)):
  tmp = []
  tmp.append(1)
  tmp.append(CX[i])
  #tmp.append(AngleManip().deg2rad(lo[i]))
  tmp.append(0)
  tmp.append(0)
  mat.append(tmp)
  tmp = []
  tmp.append(0)
  tmp.append(0)
  tmp.append(1)
  tmp.append(CY[i])
  #tmp.append(AngleManip().deg2rad(lo[i]))
  mat.append(tmp)
  obs.append(cx[i])
  obs.append(cy[i])

mat = nm.array(mat)
print ('Coefficient matrix')
print (mat)
L = nm.array(obs)
L = nm.transpose(L)
print ('Observations')
print (L)
AT = nm.transpose(mat)
ATL = nm.dot(AT, L)
ATA = nm.dot(AT, mat)
print ('ATA')
print (ATA)
ATAInv = inv(ATA)
print ('ATAInv')
print (ATAInv)

X = nm.dot(ATAInv, ATL)
print ('Coefficients')
print (X)
L1 = nm.dot(mat,X)
er = L1 - L
print ('Computed values')
print (L1)
print ('errors')
print (er)
for i in range(0,len(L)):
  print ('{0:9.1f}, {1:9.1f}'.format(L[i], L1[i]))
