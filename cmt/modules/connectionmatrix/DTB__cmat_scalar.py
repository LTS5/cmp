#!/usr/bin/python

################################################################################
# file     : DTB__cmat_scalar.py
# function : Get some scalar informations from the fibers
# date     : 2010-08-20
# author   : Christophe Chenes
#
# inputs   : inPath, fibers.trk, scalar1.nii, ..., scalarN.nii
# outputs  : TEMP_matrix_scalar1.dat, ..., TEMP_matrix_scalarN.nii
################################################################################

import os
import re
import sys
import numpy
import pickle
import trackvis

print '\n###################################################################\r'
print '# DTB__cmat_scalar.py                                             #\r'
print '###################################################################'

# Check arg and get fibers filename
nArgv = numpy.array(sys.argv).size
if nArgv < 4:
	print 'ERROR - Wrong number of arguments: '+str(nArgv-1)+\
	      ' given when at least 3 are expected.'
	sys.exit()
inPath = sys.argv[1]
fibFilename = inPath+sys.argv[2]

# Get the number and the names of each scalar provided
nbScalar = nArgv-3
print '\tScalar informations:'
for i in range(0,nbScalar):
	crtName = re.search('(?<=/)[a-z,0-9,A-Z]*.nii',sys.argv[3+i]).group(0)
	crtName = re.sub('.nii','',crtName)
	print '\t\t#'+str(i+1)+' = '+crtName
	
# Check if the corresponding file exist
if not os.path.isfile(fibFilename):
	print 'ERROR - The file: '+fibFilename+' doesn\'t exist.'
	sys.exit()
	
print '###################################################################\n'
################################################################################
