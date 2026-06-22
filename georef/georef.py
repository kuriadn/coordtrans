# Code developed by the NLIMS Directorate, National Land Commission
# This is free software to support Affine Transformation
# This is for the Cassini-Soldner to UTM transformations

# Prerequisites to running the code:
# 1. Python translation engine - python
# 2. Numpy for Matrix and array processing
# 3. Read write access on the machine it is to run on and the target output directory

import numpy as nm
import sys, getopt
from numpy.linalg import inv
from utilities import genCoeffMatrix, compute

def formatPrint(orig, trans):
# This function prepares the results for output by matching the original and transformed coordinates
  n = len(orig)
  out = []
  for i in range(0, n/2):
  	tmp = []
  	tmp.append(orig[2 * i])
  	tmp.append(orig[2 * i + 1])
  	tmp.append(trans[2 * i])
  	tmp.append(trans[2 * i + 1])
  	out.append(tmp)
  return nm.array(out)

def readData(src):
# This function reads the input file and prepares the various vectors required in subsequent 
# computations
  file = open(src, 'r')
  
  fro = []
  to = []
  conv = []

  for line in file:
    data = line.split(",")
    if len(data) > 3:
      fro.append(float(data[0]))
      fro.append(float(data[1]))
      to.append(float(data[2]))
      to.append(float(data[3]))
    else:
      conv.append(float(data[0]))
      conv.append(float(data[1]))
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
if ver: print ('{0:8.5f}, {1:12.8f}, {2:12.2f}, {3:12.2f}'.format(coeff[0], coeff[1],coeff[2],coeff[3]))
if outF: of.write('{0:8.5f}, {1:12.8f}, {2:12.2f}, {3:12.2f} {4}'.format(coeff[0], coeff[1],coeff[2],coeff[3],'\n'))
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

