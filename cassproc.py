from math import *
from pyproj import Proj, transform
import numpy as nm
from numpy.linalg import inv
import sys
from utilities import genCoeffMatrix, compute, computeCass, degMinSec, decDeg, getSgn

def getLng0(geog,cass):
  lng0 = floor(geog)
  if lng0 // 2 == lng0 / 2: lng0 += 1
  if abs(cass) > 1000 and cass > 0 and geog < lng0: lng0 -= 2
  return lng0

def readData(src):
# This function reads the input file and prepares the various vectors required in subsequent 
# computations
  file = open(src, 'r')
  
  geog = []
  cass = []

  for line in file:
    data = line.split(",")
    if len(data) > 3 and data[4].find('117') >= 0:
      geog.append(float(data[0]))
      geog.append(float(data[1]))
      cass.append(float(data[2]))
      cass.append(float(data[3]))
  file.close()
  geog = nm.array(geog)
  cass = nm.array(cass)
  return geog, cass

geog, cass = readData('cassall.asc')

# fl = open('cassproc.asc', 'w')

n = len(geog)

dAng = []
dDist = []
X = []
sgned = []

for i in range(0,n//2):
  lng0 = getLng0(geog[2*i], cass[2*i])

  cx, cy = computeCass(lng0, geog[2*i], geog[2*i+1], False)
  lo, la = computeCass(lng0, cass[2*i], cass[2*i+1], True)
 
  dln = getSgn(geog[2*i]-lo) 
  dlt = getSgn(geog[2*i+1]-la)
  sgned.append(dln)
  sgned.append(dlt)
 
  dlng = dln * round(degMinSec(geog[2*i]-lo)[2],3)
  dlat = dlt * round(degMinSec(geog[2*i+1]-la)[2],3)
  dAng.append(dlng)
  dAng.append(dlat)

  dx = cass[2*i] - cx
  dy = cass[2*i+1] - cy
  dDist.append(dx)
  dDist.append(dy)

  X.append(geog[2*i] - lng0)
  X.append(geog[2*i+1])

  print ('[{0}, {1}]; [{2}, {3}]; [{4}, {5}]; [{6}, {7}]'.format(geog[2*i], geog[2*i+1], 
    cass[2*i], cass[2*i+1], dlng, dlat, dx, dy))

dAng = nm.array(dAng)
dDist = nm.array(dDist)
X = nm.array(X)

coeff, er, ATAInv = compute(X,dAng)

B = genCoeffMatrix(X)
dAngC = nm.dot(B, coeff)

coeff, er, ATAInv = compute(X,dDist)

B = genCoeffMatrix(X)
dDistC = nm.dot(B, coeff)

for i in range(0, n//2):
  lng0 = getLng0(geog[2*i], cass[2*i])
  nlng = geog[2*i] - decDeg(0,0,dAngC[2*i]) * sgned[2*i] 
  nlat = geog[2*i+1] - decDeg(0,0,dAngC[2*i+1])  * sgned[2*i+1]
  cx, cy = computeCass(lng0, nlng, nlat, False)
  dlng = round(-er[2*i],2)
  dlat = round(-er[2*i+1],2)

  print ('{0}, {1}, {2}, {3}, {4}, {5}'.format(cx, cy, round(cass[2*i]-cx,2), 
    dlng, round(cass[2*i+1]-cy,2), dlat))

ver = False; outF = False 

if ver: print ('Transformation Parameters')
if outF: of.write('Transformation Parameters\n')
if ver: print ('{0:8.5f}, {1:12.8f}, {2:12.2f}, {3:12.2f}'.format(coeff[0], coeff[1],
  coeff[2],coeff[3]))
if outF: of.write('{0:8.5f}, {1:12.8f}, {2:12.2f}, {3:12.2f} {4}'.format(coeff[0], 
  coeff[1],coeff[2],coeff[3],'\n'))
if ver: print ('Transformation Errors')
if outF: of.write('\nTransformation Errors\n')
for i in range(0, len(er)):
  if ver: print ('{0:6.3f}'.format(er[i]))
  if outF: of.write('{0:6.3f} {1}'.format(er[i], '\n'))
if ver: print ("Inv(A'A)")
if outF: of.write("\nInv(A'A)\n")
if ver: print(ATAInv)
if outF: 
  for i in range(0, len(ATAInv)):
  	tmp = ATAInv[i]
  	of.write('{0} {1} {2} {3}\n'.format(tmp[0], tmp[1], tmp[2], tmp[3]))



