import os, os.path as op
from time import time
import logging
log = logging.getLogger()
from glob import glob
<<<<<<< HEAD:cmt/modules/connectionmatrix/raw_step7.py
=======
import subprocess

import logging as log
>>>>>>> 125a308f8e3b21c9f77bf29a321d89a32576bc4e:cmt/modules/connectionmatrix/step7.py
import subprocess

import re
import sys
<<<<<<< HEAD:cmt/modules/connectionmatrix/raw_step7.py
=======
import numpy
>>>>>>> 125a308f8e3b21c9f77bf29a321d89a32576bc4e:cmt/modules/connectionmatrix/step7.py
import numpy as np
import pickle

import struct
import math
import nibabel


################################################################################
# name     : mm2index
# function : Translate mm to index
# date     : 2010-09-10
# author   : Christophe Chenes
#
# input    : mm3, hdrStreamline
# outputs  : index
################################################################################
def mm2index(mm3, hdrStreamline):
<<<<<<< HEAD:cmt/modules/connectionmatrix/raw_step7.py
    index = np.zeros(3)
=======
    index = numpy.zeros(3)
>>>>>>> 125a308f8e3b21c9f77bf29a321d89a32576bc4e:cmt/modules/connectionmatrix/step7.py
    index[0] = int(round( mm3[0] / hdrStreamline['voxel_size'][0] - 0.5 ))
    index[1] = int(round( mm3[1] / hdrStreamline['voxel_size'][1] - 0.5 ))
    index[2] = int(round( mm3[2] / hdrStreamline['voxel_size'][2] - 0.5 ))
    index[index<0] = 0
    if index[0]>hdrStreamline['dim'][0]:
<<<<<<< HEAD:cmt/modules/connectionmatrix/raw_step7.py
        index[0] = hdrStreamline['dim'][0]
    if index[1]>hdrStreamline['dim'][1]:
        index[1] = hdrStreamline['dim'][1]
    if index[2]>hdrStreamline['dim'][2]:
        index[2] = hdrStreamline['dim'][2]
=======
       index[0] = hdrStreamline['dim'][0]
    if index[1]>hdrStreamline['dim'][1]:
       index[1] = hdrStreamline['dim'][1]
    if index[2]>hdrStreamline['dim'][2]:
       index[2] = hdrStreamline['dim'][2]
>>>>>>> 125a308f8e3b21c9f77bf29a321d89a32576bc4e:cmt/modules/connectionmatrix/step7.py
    return index
################################################################################


################################################################################
# name     : getValFromScalarMap
# function : get the value from the scalar map 
# date     : 2010-09-13
# author   : Christophe Chenes
#
# input    : mm3, scalar, hdr
# outputs  : val
################################################################################
def getValFromScalarMap(mm3, scalar, hdr):
    # TODO check the hdr from scalar and fibers
    index = mm2index(mm3, hdr)
    val = scalar.get_data()[index[0], index[1], index[2]]
<<<<<<< HEAD:cmt/modules/connectionmatrix/raw_step7.py
    return val     
=======
    return val
>>>>>>> 125a308f8e3b21c9f77bf29a321d89a32576bc4e:cmt/modules/connectionmatrix/step7.py
################################################################################


################################################################################
# name     : DTB__load_endpoints_from_trk
# function : Get the endpoints from each fibers
<<<<<<< HEAD:cmt/modules/connectionmatrix/raw_step7.py
# date     : 2010-08-20
=======
# date     : 2010-09-19
>>>>>>> 125a308f8e3b21c9f77bf29a321d89a32576bc4e:cmt/modules/connectionmatrix/step7.py
# author   : Christophe Chenes, Stephan Gerhard
#
# input    : fib, hdr
# outputs  : endpoints.npy, length.npy
################################################################################
<<<<<<< HEAD:cmt/modules/connectionmatrix/raw_step7.py
def DTB__load_endpoints_from_trk(fib, hdr, inPath):
    print '\n###################################################################\r'
    print '# DTB__load_endpoints_from_trk                                    #\r'
    print '###################################################################\n'
    
    # Init
    start     = time()
    endpoints = np.zeros( (hdr['n_count'], 2, 3) )
    epLen     = []
    pc        = -1

    # Computation for each fiber
    for n in range(0, hdr['n_count']):
    
        # Percent counter
        pcN = int(round( float(100*n)/hdr['n_count'] ))
        if pcN > pc and pcN%10 == 0:	
            pc = pcN
            print '\t\t%4.0f%%' % (pc)

        # Get the first and last point for the current fiber
        dataFiber = np.array(fib[n][0])
        dataFirst = dataFiber[0]
        dataLast  = dataFiber[dataFiber.shape[0]-1]		      
		
        # Translate from mm to index
        endpoints[n,0,:] = mm2index(dataFirst, hdr)	
        endpoints[n,1,:] = mm2index(dataLast, hdr)		    
        epLen.append(dataFiber.shape[0]-1)
		
    # Save the matrices
    outPath = inPath+'fibers/'
    np.save(outPath+'TEMP_endpoints.npy', endpoints)
    np.save(outPath+'TEMP_epLen.npy', epLen)
	
    print 'END'+str(time()-start)
    print '\n###################################################################\r'
=======
def DTB__load_endpoints_from_trk(fib, hdr):
    
    endpoints = numpy.zeros( (1, 2, 3) )
    epLen = []

    for i, fis in enumerate(fib):
        fi = fis[0]
        w = np.zeros( (1,2,3) )
        w[0,0,:] = mm2index(fi[0], hdr)
        w[0,1,:] = mm2index(fi[-1], hdr)
        endpoints = numpy.vstack( (endpoints, w) )
        epLen.append(len(fi))
        print "On fiber ", i
        		
	# Save the matrices
	outPath = gconf.get_cmt_fibers4subject(sid)
	numpy.save(op.join(outPath, 'TEMP_endpoints.npy'), endpoints[1:,:,:])
	numpy.save(op.join(outPath, 'TEMP_epLen.npy'), numpy.array(epLen))
    
>>>>>>> 125a308f8e3b21c9f77bf29a321d89a32576bc4e:cmt/modules/connectionmatrix/step7.py
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
	
	# Read the fibers
<<<<<<< HEAD:cmt/modules/connectionmatrix/raw_step7.py
    print '#-----------------------------------------------------------------#\r'
    print '# Read the fibers...                                              #\r'
    fibFilename = inPath+'fibers/streamline.trk'
    fib, hdr = nibabel.trackvis.read(fibFilenameTrue) # second argument to true makes it as generator
    print '#-----------------------------------------------------------------#\n'
   	
	# Get the fibers endpoints
    print '#-----------------------------------------------------------------#\r'
    print '# Loading fibers endpoints...                                     #\r'
    endpoints = np.load(inPath+'/fibers/TEMP_endpoints.npy')
    epLen     = np.load(inPath+'/fibers/TEMP_epLen.npy')
    print '#-----------------------------------------------------------------#\n'
=======
   print '#-----------------------------------------------------------------#\r'
   print '# Read the fibers...                                              #\r'
   fibFilename = inPath+'fibers/streamline.trk'
   fib, hdr = nibabel.trackvis.read(fibFilename, True) # second argument to true makes it as generator
   print '#-----------------------------------------------------------------#\n'
   	
	# Get the fibers endpoints
   print '#-----------------------------------------------------------------#\r'
   print '# Loading fibers endpoints...                                     #\r'
   if not os.path.isfile(inPath+'/fibers/TEMP_endpoints.npy') or not os.path.isfile(inPath+'/fibers/TEMP_epLen.npy'):
      DTB__load_endpoints_from_trk(fib, hdr)
   endpoints = numpy.load(inPath+'/fibers/TEMP_endpoints.npy')
   epLen = numpy.load(inPath+'/fibers/TEMP_epLen.npy')
   print '#-----------------------------------------------------------------#\n'
>>>>>>> 125a308f8e3b21c9f77bf29a321d89a32576bc4e:cmt/modules/connectionmatrix/step7.py
	
    # Get the shape's informations
    print '#-----------------------------------------------------------------#\r'
    print '# Shape informations...                                           #\r'
    vxDim = hdr['voxel_size'][0]

    # Output shape
    length_mat = np.zeros((endpoints.shape[0], 1))

	# For each fibers
    for f in range(0, endpoints.shape[0]):

		# Length
       length_mat[f,0] = (epLen[f]-1)*stepSize*vxDim;
	
    # Save the matrix
    filename = 'TEMP_shape.dat'
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

    # Read fibers
    print '#-----------------------------------------------------------------#\r'
    print '# Read the fibers...                                              #\r'
    fibFilename = inPath+'fibers/streamline.trk'
    fib, hdr    = nibabel.trackvis.read(fibFilename)
    print '#-----------------------------------------------------------------#\n'

    # For each file in the scalar dir
    print '#-----------------------------------------------------------------#\r'
    print '# Scalar informations:                                            #\r'
    scalarDir   = inPath+'scalar/'
    scalarFiles = np.array(os.listdir(scalarDir))
    nbScalar    = scalarFiles.size
    for i in range(0,nbScalar):
        if (scalarFiles[i] != '.' and scalarFiles[i] != '..' and scalarFiles[i] != '.svn') :
            crtName = re.search('[a-z,0-9,A-Z]*.nii',scalarFiles[i]).group(0)
            crtName = re.sub('.nii','',crtName)
            print '\t#'+str(i+1)+' = '+crtName
			
            # Open the file
            scalar = nibabel.load(scalarDir+scalarFiles[i])

            # Open the fibers
            #fib, hdr = trackvis.serial_open(fibFilename)
			
		    # Create the matrix
            fMatrix = np.zeros((hdr['n_count'],nInfo))
			
			# For each fiber
            for j in range(0, hdr['n_count']):
			
				# Get the data
                data = np.array(fib[j][0])#np.array(trackvis.serial_read(fib,hdr)[0])
				
				# Init measures
                fMean = 0
                fMin = sys.maxint
                fMax = -fMin
				
				# For each point compute the mean and max/min
                for j in range (0, data.shape[0]):
                    val = getValFromScalarMap(data[j], scalar, hdr) # TRANSLATION FROM MM TO VOXEL
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
            filename = 'TEMP_'+crtName+'.npy'
            filepath = inPath+'/fibers/temp_matrices'
            try:
               os.mkdir(filepath)
            except OSError:
               pass
            np.save(filepath+filename, fMatrix)		
    print '#-----------------------------------------------------------------#\n'						
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
<<<<<<< HEAD:cmt/modules/connectionmatrix/raw_step7.py
#    log.info("Create connection matrices")
#    log.info("==========================")
=======
    log.info("Create connection matrices")
    log.info("==========================")
>>>>>>> 125a308f8e3b21c9f77bf29a321d89a32576bc4e:cmt/modules/connectionmatrix/step7.py
    
    print '\n###################################################################\r'
    print '# DTB__cmat                                                       #\r'
    print '# Compute the connection matrix                                   #\r'
    print '###################################################################'	
<<<<<<< HEAD:cmt/modules/connectionmatrix/raw_step7.py
   
    # Read the fibers
    print '#-----------------------------------------------------------------#\r'
    print '# Read the fibers...                                              #\r'
    fibFilename = inPath+'fibers/streamline.trk'
    fib, hdr = nibabel.trackvis.read(fibFilename) #, False)
    print '#-----------------------------------------------------------------#\n'
   	
    # Check if endpoints are already computed
    if not os.path.isfile(inPath+'/fibers/TEMP_endpoints.npy') or not os.path.isfile(inPath+'/fibers/TEMP_epLen.npy'):
        DTB__load_endpoints_from_trk(fib, hdr, inPath)
      
	# Get the fibers endpoints
    print '#-----------------------------------------------------------------#\r'
    print '# Loading fibers endpoints...                                     #\r'
    en_fname  = inPath+'fibers/TEMP_endpoints.npy' #op.join(gconf.get_cmt_fibers4subject(sid), 'TEMP_endpoints.npy')
    ep_fname  = inPath+'fibers/TEMP_epLen.npy' #op.join(gconf.get_cmt_fibers4subject(sid), 'TEMP_epLen.npy')
    endpoints = np.load(en_fname)
    epLen     = np.load(ep_fname)
    print '#-----------------------------------------------------------------#\n'
	
    # For each resolution
    # TODO We have to give each ROI filepath and it'll compute for it
#    resolution = [33] #gconf.parcellation.keys()
#    for r in resolution:
#        print '\t r = '+str(r)+'\r'
#      
#        # Open the corresponding ROI
#        roi_fname = inPath+'fs_output/registred/HR__registred/scale'+str(r)+'/ROI_HR_th.nii' #op.join(gconf.get_cmt_fsout4subject(sid), 'registred', 'HR__registered-TO-b0', str(r), 'ROI_HR_th.nii')
#        roi       = nibabel.load(roi_fname)
#        roiData   = roi.get_data()
#      
#        # Create the matrix
#        #matrix = np.ndarray((r,r), 'object')
#        n = roiData.max()
#        print '\tn = '+str(n)+'\r'
#        matrix = np.zeros((n,n))
#      
#        # Open the shape matrix
#        f = open(inPath+'fibers/TEMP_shape.npy', 'r')
#        shape = pickle.load(f)
#        f.close()
#        shapeInfo = np.array(shape.keys())
#        nShapeInfo = shapeInfo.size
            
        # For each fiber
#        for i in range(0, hdr['n_count']):
#         
#            # TEMP Add in the corresponding cell the number of fibersFile
#            roiF = roiData[endpoints[i, 0, 0], endpoints[i, 0, 1], endpoints[i, 0, 2]]
#            roiL = roiData[endpoints[i, 1, 0], endpoints[i, 1, 1], endpoints[i, 1, 2]]
#            matrix[roiF-1, roiL-1] += 1
            
#        # Save the matrix
#        filename = subName[0]+'_'+subName[1]+'__cmat_'+str(r)+'.npy'
#        filepath = inPath+'fibers/matrices/'+filename #op.join(gconf.get_cmt_fibers4subject(sid), 'matrices', filename)
#        np.save(filepath, matrix)
							
=======
    
    # Read the fibers
    print '#-----------------------------------------------------------------#\r'
    print '# Read the fibers...                                              #\r'
    fibFilename = op.join(gconf.get_cmt_fibers4subject(sid), 'streamline.trk')
    fib, hdr = nibabel.trackvis.read(fibFilename, False)
    print '#-----------------------------------------------------------------#\n'
    	
    # Get the fibers endpoints
    print '#-----------------------------------------------------------------#\r'
    print '# Loading fibers endpoints...                                     #\r'
    en_fname = op.join(gconf.get_cmt_fibers4subject(sid), 'TEMP_endpoints.npy')
    ep_fname = op.join(gconf.get_cmt_fibers4subject(sid), 'TEMP_epLen.npy')
    if not os.path.isfile(en_fname) or not os.path.isfile(ep_fname):
       DTB__load_endpoints_from_trk(fib, hdr)
       
    endpoints = numpy.load(en_fname)
    epLen = numpy.load(ep_fname)
    print '#-----------------------------------------------------------------#\n'
    
    # For each resolution
    resolution = gconf.parcellation.keys()
    for r in resolution:
        print '\t r = '+str(r)+'\r'
        
        # Open the corresponding ROI
        roi_fname = op.join(gconf.get_cmt_fsout4subject(sid), 'registred', 'HR__registered-TO-b0', str(r), 'ROI_HR_th.nii')
        roi = nibabel.load(roi_fname)
        roiData = roi.get_data()
        
        # Create the matrix
        #matrix = numpy.ndarray((r,r), 'object')
        n = roiData.max()
        print '\tn = '+str(n)+'\r'
        matrix = numpy.zeros((n,n))
        
        # Open the shape matrix
        #      f = open(inPath+'fibers/TEMP_shape.npy', 'r')
        #      shape = pickle.load(f)
        #      f.close()
        #      shapeInfo = numpy.array(shape.keys())
        #      nShapeInfo = shapeInfo.size
              
        # For each fiber
        for i in range(0, hdr['n_count']):
            
            # TEMP Add in the corresponding cell the number of fibersFile
            roiF = roiData[endpoints[i, 0, 0], endpoints[i, 0, 1], endpoints[i, 0, 2]]
            roiL = roiData[endpoints[i, 1, 0], endpoints[i, 1, 1], endpoints[i, 1, 2]]
            matrix[roiF-1, roiL-1] += 1
              
        # Save the matrix
        filename = '__cmat_'+str(r)+'.npy'
        filepath = op.join(gconf.get_cmt_fibers4subject(sid), 'matrices', filename)
        numpy.save(filepath, matrix)
    						
>>>>>>> 125a308f8e3b21c9f77bf29a321d89a32576bc4e:cmt/modules/connectionmatrix/step7.py
    print '###################################################################\n'
################################################################################


<<<<<<< HEAD:cmt/modules/connectionmatrix/raw_step7.py
################################################################################
# TESTING
def run():#conf, subject_tuple):
=======
def run(conf, subject_tuple):
>>>>>>> 125a308f8e3b21c9f77bf29a321d89a32576bc4e:cmt/modules/connectionmatrix/step7.py
    """ Run the connection matrix step
    
    Parameters
    ----------
    conf : PipelineConfiguration object
    subject_tuple : tuple, (subject_id, timepoint)
      Process the given subject
       
    """
    # setting the global configuration variable
<<<<<<< HEAD:cmt/modules/connectionmatrix/raw_step7.py
#    globals()['gconf'] = conf
#    globals()['sid'] = subject_tuple
    start = time()
    
    # FOR TESTING
    subDir = '/home/cwis/Subjects/'#subDir = gconf.get_cmt4subject(sid)
    subName = ['Control_004', 'tp01'] #sid
    in01 = subDir+subName[0]+'/'+subName[1]+'/'
    DTB__cmat_scalar(in01, subName)
#    DTB__cmat(in01, subName)
    
    print 'TIME = '+str(time()-start)#log.info("Connection matrix module took %s seconds to process." % (time()-start))
################################################################################
################################################################################

run()
=======
    globals()['gconf'] = conf
    globals()['sid'] = subject_tuple
    start = time()
    
    subDir = gconf.get_cmt4subject(sid)
    subName = sid
    
    DTB__cmat(subDir, subName)
    
    log.info("Module took %s seconds to process." % (time()-start))
>>>>>>> 125a308f8e3b21c9f77bf29a321d89a32576bc4e:cmt/modules/connectionmatrix/step7.py
