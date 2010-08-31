#!/usr/bin/python

################################################################################
# file     : DTB__cmat_shape.py
# function : Get the shape informations from the fibers
# date     : 2010-08-20
# author   : Christophe Chenes
#
# inputs   : fibers.trk, inPath
# outputs  : TEMP_matrix_shape.dat
#
# infos    : length
# nInfos   : 1
################################################################################

import os
import sys
import numpy
import pickle
import trackvis
import DTB__load_endpoints_from_trk as EP_Loader

print '\n###################################################################\r'
print '# DTB__cmat_shape.py                                              #\r'
print '###################################################################\n'

# Useful shape informations
# Add here every new informations
infos    = ['length'] 
stepSize = 0.5

# Check arg and get fibers filename
nArgv = numpy.array(sys.argv).size
if nArgv != 3:
	print 'ERROR - Wrong number of arguments: '+str(nArgv-1)+' given when 2 expected.'
	sys.exit()
inPath = sys.argv[1]
fibFilename = inPath+sys.argv[2]

# Check if the corresponding file exist
if not os.path.isfile(fibFilename):
	print 'ERROR - The file: '+fibFilename+' doesn\'t exist.'
	sys.exit()
	
# Get the fibers endpoints
print '#-----------------------------------------------------------------#\r'
print '# Loading fibers endpoints...                                     #\r'
endpoints, epLen = EP_Loader.DTB__load_endpoints_from_trk(fibFilename)
print '#-----------------------------------------------------------------#\n'

# Get the shape's informations
print '#-----------------------------------------------------------------#\r'
print '# Shape informations...                                           #\r'
fib, hdr = trackvis.serial_open(fibFilename)
vxDim = hdr['voxel_size'][0]

# Output shape
length_mat = numpy.zeros((endpoints.shape[0], 1))

# For each fibers
for f in range(0, endpoints.shape[0]):

	# Length
	length_mat[f,0] = (epLen[f]-1)*stepSize*vxDim;
	
# Save the matrix
filename = 'TEMP_matrix_shape.dat'
filepath = inPath+'/fibers/temp_matrices'
out_matrix = {'length': length_mat}
try:
	os.mkdir(filepath)
except OSError:
	pass
f = open(filepath+'/'+filename, 'w+b')
pickle.dump(out_matrix,f)
f.close()
print '# saved in:                                                       #\r'
print filepath+'/'+filename
print '#-----------------------------------------------------------------#\n'
print '###################################################################\n'
################################################################################

