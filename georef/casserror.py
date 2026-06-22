# Code developed by the NLIMS Directorate, National Land Commission
# This is free software to support Affine Transformation
# This is for the Cassini-Soldner to UTM transformations

# Prerequisites to running the code:
# 1. Python translation engine - python
# 2. Numpy for Matrix and array processing
# 3. Read write access on the machine it is to run on and the target output directory

import numpy as nm
import sys, getopt
from math import *
from numpy.linalg import inv

def genCoeffMatrix(x):
# This function prepares the Matrix of Coefficients given an input vector
  n = len(x)
  j = 0
  mat = []
  for i in range(0,n/2):
    tmp = []
    tmp.append(x[j * 2 ] * pi / 180.)
    tmp.append(x[j * 2 +1]  * pi / 180.)
    tmp.append(1)
    tmp.append(0)
    tmp.append(0)
    tmp.append(0)
    mat.append(tmp)
    tmp = []
    tmp.append(0)
    tmp.append(0)
    tmp.append(0)
    tmp.append(x[j * 2]  * pi / 180.)
    tmp.append(x[j * 2 + 1]  * pi / 180.)
    tmp.append(1)
    mat.append(tmp)
    j += 1
  return nm.array(mat)

def formatPrint(orig, trans):
# This function prepares the results for output by matching the original and transformed coordinates
  n = len(orig)
  out = []
  for i in range(0,n/2):
  	tmp = []
  	tmp.append(orig[2 * i])
  	tmp.append(orig[2 * i + 1])
  	tmp.append(trans[2 * i])
  	tmp.append(trans[2 * i + 1])
  	out.append(tmp)
  return nm.array(out)

def compute(x,l):
# This function computes the transformation parameters
# Matrix of coefficients
  A = genCoeffMatrix(x)

  L=l
  L=nm.transpose(L)
 
# Prepare system of equations
  AT=nm.transpose(A)
  ATA=nm.dot(AT,A)
  ATL=nm.dot(AT,L)
  ATAInv = inv(ATA)

# The solution
  x=nm.dot(ATAInv,ATL)
  L1 = nm.dot(A,x)

# The computation errors
  er=L1-L
  return x, er, ATAInv

def readData(src):
# This function reads the input file and prepares the various vectors required in subsequent 
# computations
  file = open(src, 'r')
  
  fro = []
  to = []
  conv = []

  for line in file:
    data = line.split("\r")
    for i in range(0, len(data)):
      dt = data[i].split(",")
      #print dt
      if len(dt) > 3:
        fro.append(float(dt[0]))
        fro.append(float(dt[1]))
        to.append(float(dt[2]))
        to.append(float(dt[3]))
      else:
        conv.append(float(dt[0]))
        conv.append(float(dt[1]))
  file.close()
  fro = nm.array(fro)
  to = nm.array(to)
  conv = nm.array(conv)
  return fro, to, conv

def usage(fl):
  print ('This is a coordinate transformation solution using the Affine Transformation Approach')
  print ('To use this commandline tool the following options are available:')
  print ('1. Without requiring an output file use')
  print ('	python {0} -i source_file'.format(fl))
  print ('2. When requiring an output file use')
  print ('	python {0} -i source_file -o output_file'.format(fl))
  print ('3. Show screen output, provide the -v switch')
  print ('	python {0} -v -i source_file or,'.format(fl))
  print ('	python {0} -v -i source_file -o output_file'.format(fl))


# This is the entry point into the actual program
# Initial settings  
outF = False
ver = False
inf = ''
fl = sys.argv[0]
try:
  opts, args = getopt.getopt(sys.argv[1:], "vi:o:")

except getopt.GetoptError:
  usage(fl)
  sys.exit()
for opt, arg in opts:
  if opt == '-i':
  	inf = arg
  elif opt == '-o':
  	of = open(arg, 'w')
  	outF = True
  elif opt == '-v':
  	ver = True
  else:
    usage(fl)
    sys.exit()

if len(inf) == 0: 
  usage(fl)
  sys.exit()

# All is in order at this stage and so we can roll on
x,l, dat = readData(inf)

# Perform the computations
coeff, er, ATAInv = compute(x,l)

# Compute transformed coordinates
if ver: print ('Transformation Parameters')
if outF: of.write('Transformation Parameters\n')
if ver: print ('{0:10.5f}, {1:10.5f}, {2:10.5f}, {3:10.5f}, {4:10.5f}, {5:10.5f}'.format(coeff[0], coeff[1],coeff[2],coeff[3], coeff[4], coeff[5]))
if outF: of.write('{0:8.5f}, {1:12.8f}, {2:12.2f}, {3:12.2f} {4}\n'.format(coeff[0], coeff[1],coeff[2],coeff[3], coeff[4], coeff[5]))
if ver: print ('Transformation Errors')
if outF: of.write('\nTransformation Errors\n')
for i in range(0, len(er)):
  if ver: print ('{0:6.3f}, {1:6.4f}'.format(er[i], l[i]))
  if outF: of.write('{0:6.3f} {1}'.format(er[i], '\n'))
if ver: print ("Inv(A'A)")
if outF: of.write("\nInv(A'A)\n")
if ver: print(ATAInv)
if outF: 
  for i in range(0, len(ATAInv)):
  	tmp = ATAInv[i]
  	of.write('{0} {1} {2} {3} {4} {5}\n'.format(tmp[0], tmp[1], tmp[2], tmp[3]))
 
if len(dat) > 0:
  # Generate the matrix of coefficients to drive our transformation
  B = genCoeffMatrix(dat)

  # Compute the transformed coordinates
  trans = nm.dot(B, coeff)

  # Prepare the outputs for display and saving into chosen file (if provided)
  forP = formatPrint(dat, trans)
  if ver: print ('Transformed Coordinates: Original vs Transformed list')
  if outF: of.write('\nTransformed Coordinates: Original vs Transformed list\n')
  for i in range(0,len(forP)):
    tmp = forP[i]
    if ver: print ('{0:12.2f}, {1:12.2f}, {2:12.2f}, {3:12.2f}'.format(tmp[0], tmp[1], tmp[2], tmp[3]))
    if outF: of.write('{0:12.2f}, {1:12.2f}, {2:12.2f}, {3:12.2f} {4}'.format(tmp[0], tmp[1], tmp[2], tmp[3],'\n'))

if outF: of.close()

