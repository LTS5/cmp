import logging as log
import subprocess
import os
import re
import sys
import numpy
import pickle
import trackvis
import struct
import math
import nibabel

#global gconf
#global subject_dir

#7) Create connection matrices (MATLAB way)
log.info("STEP7: Create connection matrices")

# $MY_MATLAB "DTB__create_connection_matrix( '${DATA_path}/${MY_SUBJECT}/${MY_TP}/4__CMT' ); exit"

# XXX -> create a nipype matlab node

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
		if pcN > pc and pcN%10 == 0:	
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
# inputs   : inPath, subName
# outputs  : TEMP_matrix_shape.dat
#
# infos    : length
# nInfos   : 1
################################################################################
def DTB__cmat_shape(inPath, subName):
   
	print '\n###################################################################\r'
	print '# DTB__cmat_shape                                                 #\r'
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
	fibFilename = inPath+'fibers/'+subName+'__streamlines.trk'
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
# name     : DTB__cmat_scalar.py
# function : Get some scalar informations from the fibers
# date     : 2010-09-05
# author   : Christophe Chenes
#
# inputs   : inPath, subName
# outputs  : TEMP_matrix_scalar1.dat, ..., TEMP_matrix_scalarN.nii
################################################################################
def DTB__cmat_scalar(inPath, subName):
	print '\n###################################################################\r'
	print '# DTB__cmat_scalar                                                #\r'
	print '###################################################################'

	# Number of informations: mean max min std
	nInfo = 4

	# Check if the corresponding file exist
	fibFilename = inPath+'fibers/'+subName+'__streamlines.trk'
   #fibFilename = inPath+'fibers/'+subName+'__streamlines.trk'
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
			
			# Open the file
			scalar = nibabel.load(scalarDir+scalarFiles[i])

			# Open the fibers
			fib, hdr = trackvis.serial_open(fibFilename)
			
			# Create the matrix
			fMatrix = numpy.zeros((hdr['n_count'],nInfo))
			
			# For each fiber
			for j in range(0, hdr['n_count']):
			
				# Get the data
				data = numpy.array(trackvis.serial_read(fib,hdr)[0])
				
				# Init measures
				fMean = 0
				fMin = sys.maxint
				fMax = -fMin
				
				# For each point compute the mean and max/min
				for j in range (0, data.shape[0]):
					#val = getValFromScalarMap(data[j], scalar)
					val = 0
					fMean += val
					if val < fMin:
						fMin = val
					elif val > fMax:
						fMax = val
				fMean = fMean / data.shape[0]
				
				# For each point compute the standard deviation
				fStdSum = 0
				for j in range (0, data.shape[0]):
					#val = getValFromScalarMap(data[j])
					val = 0
					val = (val-fMean)**2
					fStdSum += val
				fStd = math.sqrt(fStdSum / data.shape[0])
				
				# Store these informations		
				fMatrix[i, 0] = fMean		 	
				fMatrix[i, 1] = fMin				
				fMatrix[i, 2] = fMax			
				fMatrix[i, 3] = fStd
				
			# Save the matrix in a file
			filename = 'TEMP_matrix_scalar_'+crtName+'.npy'
			filepath = inPath+'fibers/temp_matrices/'
			numpy.save(filepath+filename, fMatrix)								
	print '###################################################################\n'
################################################################################

################################################################################
# name     : DTB__cmat.py
# function : Create the connection matrix 
# date     : 2010-09-10
# author   : Christophe Chenes
#
# inputs   : inPath, subName
# outputs  : cmat_res1.dat, ..., cmat_resN.dat
################################################################################
def DTB__cmat(inPath, subName):
   print '\n###################################################################\r'
   print '# DTB__cmat                                                       #\r'
   print '# Compute the connection matrix                                   #\r'
   print '###################################################################'	
   
   # Open the fibers
   fibFilename = inPath+'fibers/'+subName+'__streamlines.trk'
   fib, hdr = trackvis.serial_open(fibFilename)
   
   # Read endpoints
   print '#-----------------------------------------------------------------#\r'
   print '# Loading fibers endpoints...                                     #\r'
   endpoints, epLen = DTB__load_endpoints_from_trk(fibFilename)
   print '#-----------------------------------------------------------------#\n'
	
   # For each resolution
   resolution = numpy.array([33, 60, 125, 250, 500])
   for r in resolution:
      print '\t r = '+str(r)+'\r'
      # Open the corresponding ROI
      roi = nibabel.load(inPath+'fs_output/registred/HR__registred_T0_b0/scale'+str(r)+'/ROI_HR_th.nii')
      roiData = roi.get_data()
      
      # Create the matrix
      #matrix = numpy.ndarray((r,r), 'object')
      n = roiData.max()
      print '\tn = '+str(n)+'\r'
      matrix = numpy.zeros((n,n))
      
      # For each fiber
      for i in range(0, hdr['n_count']):
         
         # TEMP Add in the corresponding cell the number of fibersFile
         roiF = roiData[endpoints[i, 0]['v1']][endpoints[i, 0]['v2']][endpoints[i, 0]['v3']]
         roiL = roiData[endpoints[i, 1]['v1']][endpoints[i, 1]['v2']][endpoints[i, 1]['v3']]
         matrix[roiF-1, roiL-1] += 1
      
      # Save the matrix
      filename = subName+'__cmat_'+str(r)+'.dat'
      filepath = inPath+'/fibers/matrices/'
#      f = open(filepath+filename, 'w')
#      f.close()
      numpy.save(filepath+filename,matrix)
							
   print '###################################################################\n'
################################################################################

def run(subDir, subName):#conf, subject_tuple):
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
#   DTB__cmat_shape(subDir, subName)
#   DTB__cmat_scalar(subDir, subName)
   DTB__cmat(subDir, subName)

run(sys.argv[1], sys.argv[2])
log.info("[ DONE ]")
