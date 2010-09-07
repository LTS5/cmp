import logging as log
import subprocess
import os
import re
import sys
import numpy
import pickle
import trackvis
import struct

#global gconf
#global subject_dir

#7) Create connection matrices (MATLAB way)
log.info("STEP7: Create connection matrices")

# $MY_MATLAB "DTB__create_connection_matrix( '${DATA_path}/${MY_SUBJECT}/${MY_TP}/4__CMT' ); exit"

# XXX -> create a nipype matlab node

# CHRISTOPHE WORK #
# NOT DONE #

################################################################################
# name     : DTB__load_endpoints_from_trk
# function : Get the endpoints from each fibers
# date     : 2010-08-20
# author   : Christophe Chenes
#
# input    : fibers.trk file
# outputs  : endpoints, length
################################################################################
def DTB__load_endpoints_from_trk(fibersFile):
	fib, hdr = trackvis.serial_open(fibersFile)
	endpoints = numpy.ndarray((hdr['n_count'],2),'object')
	epLen = numpy.zeros((hdr['n_count'],1))
	pc = -1
	for n in range(0, hdr['n_count']):
		pcN = int(round( float(100*n)/hdr['n_count'] ))
		if pcN > pc :#and pcN%10 == 0:	
			pc = pcN
			print '\t\t%4.0f%%' % (pc)
		M = struct.unpack('<i', fib.read(4))[0]
		data = numpy.zeros((3,M))
		for m in range(0, M):
			data[0,m] = struct.unpack('<f', fib.read(4))[0]
			data[1,m] = struct.unpack('<f', fib.read(4))[0]
			data[2,m] = struct.unpack('<f', fib.read(4))[0]
			
			# scalars treatment
			if hdr['n_scalars'] != 0:
				print '\tscalars...'
				for i in range(0,hdr['n_scalars']):
					tmp = fib.read(4)
			
		# keep only first and last
		data = data[:,[0,M-1]]
		
		v = numpy.zeros((3,2))
		v[0,0] = int(round( data[0,0] / hdr['voxel_size'][0] - 0.5 )) + 1
		v[1,0] = int(round( data[1,0] / hdr['voxel_size'][1] - 0.5 )) + 1
		v[2,0] = int(round( data[2,0] / hdr['voxel_size'][2] - 0.5 )) + 1
		v[0,1] = int(round( data[0,1] / hdr['voxel_size'][0] - 0.5 )) + 1
		v[1,1] = int(round( data[1,1] / hdr['voxel_size'][1] - 0.5 )) + 1
		v[2,1] = int(round( data[2,1] / hdr['voxel_size'][2] - 0.5 )) + 1
		
		v[v<1] = 1
		if v[0,0]>hdr['dim'][0]:
			v[0,0] = hdr['dim'][0]
		if v[1,0]>hdr['dim'][1]:
			v[1,0] = hdr['dim'][1]
		if v[2,0]>hdr['dim'][2]:
			v[2,0] = hdr['dim'][2]
		if v[0,1]>hdr['dim'][0]:
			v[0,1] = hdr['dim'][0]
		if v[1,1]>hdr['dim'][1]:
			v[1,1] = hdr['dim'][1]
		if v[2,1]>hdr['dim'][2]:
			v[2,1] = hdr['dim'][2]
			
		first = {'v1':v[0,0]-1, 'v2':v[1,0]-1, 'v3':v[2,0]-1}
		last = {'v1':v[0,1]-1, 'v2':v[1,1]-1, 'v3':v[2,1]-1}
		endpoints[n, 0] = first
		endpoints[n, 1] = last
		epLen[n] = M-1
		
		# properties treatment
		if hdr['n_properties'] != 0:
			print '\tproperies...'
			for i in range(0,hdr['n_properties']):
				tmp = fib.read(4)
		
	return endpoints, epLen
################################################################################

################################################################################
# name     : DTB__cmat_shape
# function : Get the shape informations from the fibers
# date     : 2010-08-20
# author   : Christophe Chenes
#
# inputs   : inPath
# outputs  : TEMP_matrix_shape.dat
#
# infos    : length
# nInfos   : 1
################################################################################
def DTB__cmat_shape(inPath):

	print '\n###################################################################\r'
	print '# DTB__cmat_shape.py                                              #\r'
	print '###################################################################\n'

	# Useful shape informations
	# Add here every new informations
	infos    = ['length'] 
	stepSize = 0.5

	# Check arg and get fibers filename
#	nArgv = numpy.array(sys.argv).size
#	if nArgv != 3:
#		print 'ERROR - Wrong number of arguments: '+str(nArgv-1)+' given when 2 expected.'
#		sys.exit()
#	inPath = sys.argv[1]
#	fibFilename = inPath+sys.argv[2]

	# Check if the corresponding file exist
	fibFilename = inPath+'fibers/Control_004__streamlines.trk'
	if not os.path.isfile(fibFilename):
		print 'ERROR - The file: '+fibFilename+' doesn\'t exist.'
		sys.exit()
	
	# Get the fibers endpoints
	print '#-----------------------------------------------------------------#\r'
	print '# Loading fibers endpoints...                                     #\r'
	endpoints, epLen = DTB__load_endpoints_from_trk(fibFilename)
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

################################################################################
# file     : DTB__cmat_scalar.py
# function : Get some scalar informations from the fibers
# date     : 2010-09-05
# author   : Christophe Chenes
#
# inputs   : inPath
# outputs  : TEMP_matrix_scalar1.dat, ..., TEMP_matrix_scalarN.nii
################################################################################
def DTB__cmat_scalar(inPath):
	print '\n###################################################################\r'
	print '# DTB__cmat_scalar.py                                             #\r'
	print '###################################################################'

	# Check if the corresponding file exist
	fibFilename = inPath+'fibers/Control_004__streamlines.trk'
	if not os.path.isfile(fibFilename):
		print 'ERROR - The file: '+fibFilename+' doesn\'t exist.'
		sys.exit()

	# For each file in the scalar dir
	scalarDir = inPath+'scalar/'
	scalarFiles = numpy.array(os.listdir(scalarDir))
	nbScalar = scalarFiles.size
	print '\tScalar informations:'
	for i in range(0,nbScalar):
		if (scalarFiles[i] != '.' and scalarFiles[i] != '..' and scalarFiles[i] != '.svn') :
			crtName = re.search('[a-z,0-9,A-Z]*.nii',scalarFiles[i]).group(0)
			crtName = re.sub('.nii','',crtName)
			print '\t\t#'+str(i+1)+' = '+crtName

			# Open the fibers
			fib, hdr = trackvis.serial_open(fibFilename)
			for j in range(0, hdr['n_count']):
				pass
				
		
	print '###################################################################\n'
################################################################################

# END CHRISTOPHE WORK

def run(subDir):#conf, subject_tuple):
    """ Run the connection matrix step
    
    Parameters
    ----------
    conf : PipelineConfiguration object
    subject_tuple : tuple, (subject_id, timepoint)
        Process the given subject
        
    """
    # setting the global configuration variable
    #gconf = conf
    #subject_dir = gconf[subject_tuple]['workingdir']
#    DTB__cmat_shape(subDir)
    DTB__cmat_scalar(subDir)

run(sys.argv[1])
log.info("[ DONE ]")
