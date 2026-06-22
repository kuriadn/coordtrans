from math import *
from pyproj import Proj, transform
import numpy as nm
import sys, getopt
from numpy.linalg import inv
from anglemanip import AngleManip
from casstables import CassTable

def getProjStrCass(phi0, lam0):
  projStr ='+proj=cass +lat_0={0} +lon_0={1} +a=20926348 +b=20855233 +units=m +no_defs'.format(phi0, lam0)
  return projStr
#print sys.argv

def getCM(l):
  if ((l + 1)/2.0 - floor((l + 1)/2.0)) > 0.01: 
    lam0 = l + 1
  else: lam0 = l 
  return lam0

f=open('cassall1.asc','r')
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
TX = []
TY = []
TLo = []
TLa = []
#fo = open('cass_comp.asc','w')
CT = CassTable()
for i in range(0, len(lo)):
  l = floor(lo[i])
  lam0 = getCM(l)
  #print lam0
  csStr = getProjStrCass(phi0, lam0)
  cPrj = Proj(csStr)
  x, y = cPrj(lo[i], la[i])
  CX.append(x)
  CY.append(y)
  x, y = CT.computeCass(lo[i], la[i] , lam0)
  TX.append(x)
  TY.append(y)
  lon, lat = CT.computeGeog(cx[i], cy[i], lam0)
  TLo.append(lon)
  TLa.append(lat)

for i in range(0, len(lo)):
  # print ('Eastings: ', CX[i], TX[i], cx[i], abs(CX[i] - TX[i]))
  # print ('Northings:', CY[i], TY[i], cy[i], abs(CX[i] - TX[i]))
  # print ('Long:', TLo[i], lo[i], AngleManip().degMinSec(TLo[i] - lo[i]))
  # print ('Lat:', TLa[i], la[i], AngleManip().degMinSec(TLa[i] - la[i]))
  # lam0 = getCM(lo[i])
  # print ('Long: ', CX[i] - TX[i], cx[i] - TX[i], AngleManip().degMinSec(TLo[i] - lo[i]), (lo[i] - lam0) / 0.25)
  # print ('Lat:', CY[i] - TY[i], cy[i] - TY[i], AngleManip().degMinSec(TLa[i] - la[i]), la[i] / 0.25)
  lam0 = getCM(floor(lo[i]))
  print ('{0:10.2f}, {1:10.2f}, {2:7.4f}, {3:10.2f}, {4:10.2f}, {5:9.4f}, {6:8.5f}, {7}, {8:8.5f}, {9}, {10:5.2f}, {11:5.2f}'.format(CX[i], cx[i], abs(cx[i] - CX[i]), CY[i], cy[i], abs(cy[i] - CY[i]), AngleManip().degMinSec(TLo[i] - lo[i])[2], abs(lo[i] - lam0) / 0.25, AngleManip().degMinSec(TLa[i] - la[i])[2], abs(la[i] / 0.25), lo[i], la[i]))
#  fo.write('{0:9.1f}, {1:9.1f}, {2:9.1f}, {3:9.1f}\n'.format(cx[i],CX[i], cy[i], CY[i]))
#  print ('Long={0:6.2f}; Lat={1:6.2f}; origX={2:9.1f}; origY={3:9.1f}; compX={4:9.1f}; compY={5:9.1f}'.format(lo[i],la[i],cx[i], cy[i], x, y))
#fo.close()

