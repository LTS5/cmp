import os, os.path as op
from time import time
import logging
log = logging.getLogger()
from glob import glob
import subprocess

import re
import sys
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
    index = np.zeros(3)
    index[0] = int(round( mm3[0] / hdrStreamline['voxel_size'][0] - 0.5 ))
    index[1] = int(round( mm3[1] / hdrStreamline['voxel_size'][1] - 0.5 ))
    index[2] = int(round( mm3[2] / hdrStreamline['voxel_size'][2] - 0.5 ))
    index[index<0] = 0
    if index[0]>hdrStreamline['dim'][0]:
        index[0] = hdrStreamline['dim'][0]
    if index[1]>hdrStreamline['dim'][1]:
        index[1] = hdrStreamline['dim'][1]
    if index[2]>hdrStreamline['dim'][2]:
        index[2] = hdrStreamline['dim'][2]
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
    return val     
################################################################################


################################################################################
# name     : DTB__load_endpoints_from_trk
# function : Get the endpoints from each fibers
# date     : 2010-08-20
# author   : Christophe Chenes, Stephan Gerhard
#
# input    : fib, hdr
# outputs  : endpoints.npy, length.npy
################################################################################
def DTB__load_endpoints_from_trk(fib, hdr, inPath):
    print '\n###################################################################\r'
    print '# DTB__load_endpoints_from_trk                                    #\r'
    print '###################################################################\r'
    
    # Init
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
    np.save(op.join(inPath, 'TEMP_endpoints.npy'), endpoints)
    np.save(op.join(inPath, 'TEMP_epLen.npy'), epLen)
	
    print '\n###################################################################\n'
################################################################################


################################################################################
# name     : DTB__cmat_shape
# function : Get the shape informations from the fibers
# date     : 2010-08-20
# author   : Christophe Chenes
#
# inputs   : 
# outputs  : cmat_shape.npy
#
# infos    : length
# nbInfos  : 1
################################################################################
def DTB__cmat_shape():
    print '###################################################################\r'
    print '# DTB__cmat_shape                                                 #\r'
    print '###################################################################\n'

    # Read the fibers
    print '#-----------------------------------------------------------------#\r'
    print '# Read the fibers...                                              #\r'
    fibFilename = op.join(gconf.get_cmt_fibers4subject(sid), 'streamline.trk')
    fib, hdr    = nibabel.trackvis.read(fibFilename, False)
    print '#-----------------------------------------------------------------#\r'
       	
    # Check if endpoints are already computed
    if    not os.path.isfile(op.join(gconf.get_cmt_fibers4subject(sid), 'TEMP_endpoints.npy')) \
       or not os.path.isfile(op.join(gconf.get_cmt_fibers4subject(sid), 'TEMP_epLen.npy')):
        inPath = gconf.get_cmt_fibers4subject(sid)
        DTB__load_endpoints_from_trk(fib, hdr, inPath)
      
	# Get the fibers endpoints
    print '#-----------------------------------------------------------------#\r'
    print '# Loading fibers endpoints...                                     #\r'
    en_fname  = op.join(gconf.get_cmt_fibers4subject(sid), 'TEMP_endpoints.npy')
    ep_fname  = op.join(gconf.get_cmt_fibers4subject(sid), 'TEMP_epLen.npy')
    endpoints = np.load(en_fname)
    epLen     = np.load(ep_fname)
    print '#-----------------------------------------------------------------#\n'

	# Used shape informations
    # TODO Where should I get this to avoid hardcoded variable ?
    infos    = ['length'] 
    nbInfos  = 1
    stepSize = 0.5
    
    # Get the shape's informations
    print '#-----------------------------------------------------------------#\r'
    print '# Shape informations...                                           #\r'
    vxDim = hdr['voxel_size'][0]

    # Output shape
    out_mat = np.zeros((endpoints.shape[0], nbInfos))

    # For each fibers
    for f in range(0, endpoints.shape[0]):

        # Length
        out_mat[f,0] = (epLen[f]-1)*stepSize*vxDim;
	
    # Save the matrix
    # TODO add in configuration.py a function get_cmt_matrices4subject()
    filepath = gconf.get_cmt_fibers4subject(sid)
    np.save(op.join(filepath, 'matrices/cmat_shape.npy'), out_mat)
    print '#-----------------------------------------------------------------#\n'
    print '###################################################################\n'
################################################################################


################################################################################
# name     : DTB__cmat_scalar.py
# function : Get some scalar informations from the fibers
# date     : 2010-09-05
# author   : Christophe Chenes
#
# inputs   : 
# outputs  : cmat_scalar1.dat, ..., cmat_scalarN.nii
################################################################################
def DTB__cmat_scalar():
    print '\n###################################################################\r'
    print '# DTB__cmat_scalar                                                #\r'
    print '###################################################################'

    # Number of informations: mean max min std
    nInfo = 4
    inPath = gconf.get_cmt_fibers4subject(sid)
    
    # Read the fibers
    print '#-----------------------------------------------------------------#\r'
    print '# Read the fibers...                                              #\r'
    fibFilename = op.join(inPath, 'streamline.trk')
    fib, hdr    = nibabel.trackvis.read(fibFilename, False)
    print '#-----------------------------------------------------------------#\r'

    # For each file in the scalar dir
    # TODO Change the method to get scalarfiles
    # TODO Add in configuration.py a function get_cmt_scalars4subject()
    print '#-----------------------------------------------------------------#\r'
    print '# Scalar informations:                                            #\r'
    scalarDir   = op.join(gconf.get_cmt4subject(sid), 'scalars/')
    scalarFiles = np.array(os.listdir(scalarDir))
    nbScalar    = scalarFiles.size
    print nbScalar
    for i in range(0, nbScalar):
        if (scalarFiles[i] != '.' and scalarFiles[i] != '..' and scalarFiles[i] != '.svn') :
            crtName = re.search('[a-z,0-9,A-Z]*.nii',scalarFiles[i]).group(0)
            crtName = re.sub('.nii','',crtName)
            print '\t#'+str(i+1)+' = '+crtName
			
            # Open the file
            scalar = nibabel.load(scalarDir+scalarFiles[i])
			
		    # Create the matrix
            fMatrix = np.zeros((hdr['n_count'],nInfo))
			
            # For each fiber
            # TODO This function is really slow !!
            for j in range(0, hdr['n_count']):
			
				# Get the XYZ in mm
                data = np.array(fib[j][0])
                
                # Get the scalar value from XYZ in mm
                for k in range (0, data.shape[0]):
                    val = getValFromScalarMap(data[k], scalar, hdr)
				
				# Store these informations		
                fMatrix[j, 0] = val.mean() 	
                fMatrix[j, 1] = val.min()				
                fMatrix[j, 2] = val.max()			
                fMatrix[j, 3] = val.std()
				
			# Save the matrix in a file
            print '\tSave'
            filename = 'cmat_'+crtName+'.npy'
            filepath = inPath #gconf.get_cmt_fibers4subject(sid)
            np.save(op.join(filepath, 'matrices/', filename), fMatrix)
    print '#-----------------------------------------------------------------#\n'						
    print '###################################################################\n'
################################################################################


################################################################################
# name     : DTB__cmat.py
# function : Create the connection matrix 
# date     : 2010-09-10
# author   : Christophe Chenes
#
# inputs   : 
# outputs  : cmat_res1.npy, ..., cmat_resN.npy
################################################################################
def DTB__cmat(): 
    log.info("Create connection matrices")
    log.info("==========================")
    
    print '\n###################################################################\r'
    print '# DTB__cmat                                                       #\r'
    print '# Compute the connection matrix                                   #\r'
    print '###################################################################\n'	
   
    # Read the fibers
    print '#-----------------------------------------------------------------#\r'
    print '# Read the fibers...                                              #\r'
    fibFilename = op.join(gconf.get_cmt_fibers4subject(sid), 'streamline.trk')
    fib, hdr    = nibabel.trackvis.read(fibFilename, False)
    print '#-----------------------------------------------------------------#\r'
       	
    # Check if endpoints are already computed
    if    not os.path.isfile(op.join(gconf.get_cmt_fibers4subject(sid), 'TEMP_endpoints.npy')) \
       or not os.path.isfile(op.join(gconf.get_cmt_fibers4subject(sid), 'TEMP_epLen.npy')):
        inPath = gconf.get_cmt_fibers4subject(sid)
        DTB__load_endpoints_from_trk(fib, hdr, inPath)
      
	# Get the fibers endpoints
    print '#-----------------------------------------------------------------#\r'
    print '# Loading fibers endpoints...                                     #\r'
    en_fname  = op.join(gconf.get_cmt_fibers4subject(sid), 'TEMP_endpoints.npy')
    ep_fname  = op.join(gconf.get_cmt_fibers4subject(sid), 'TEMP_epLen.npy')
    endpoints = np.load(en_fname)
    epLen     = np.load(ep_fname)
    print '#-----------------------------------------------------------------#\n'
	
    # For each resolution
    # TODO We have to give each ROI filepath and it'll compute for it
    print '#-----------------------------------------------------------------#\r'
    print '# Each resolution treatment...                                    #\r'
    resolution = gconf.parcellation.keys()
    for r in resolution:
        print '\t r = '+r+'\r'
      
        # Open the corresponding ROI
        print '\t open the ROI\r'
        roi_fname = op.join(gconf.get_cmt_fsout4subject(sid), 'registered', 'HR__registered-T0-b0', r, 'ROI_HR_th.nii')
        roi       = nibabel.load(roi_fname)
        roiData   = roi.get_data()
      
        # Create the matrix
        print '\t create the big matrix\r'
        # TODO Create the matrix without any dictionnary, use a 4 or 5 dimension matrix  
        # TODO and find a way to add everything inside (or the mean)
#        #matrix = np.ndarray((r,r), 'object')
#        n = roiData.max()
#        print '\tn = '+str(n)+'\r'
#        matrix = np.zeros((n,n))
      
        # Open the shape matrix
#        f = open(inPath+'fibers/TEMP_shape.npy', 'r')
#        shape = pickle.load(f)
#        f.close()
#        shapeInfo = np.array(shape.keys())
#        nShapeInfo = shapeInfo.size
            
        # For each fiber
#        for i in range(0, hdr['n_count']):
#         
            # TEMP Add in the corresponding cell the number of fibersFile
#            roiF = roiData[endpoints[i, 0, 0], endpoints[i, 0, 1], endpoints[i, 0, 2]]
#            roiL = roiData[endpoints[i, 1, 0], endpoints[i, 1, 1], endpoints[i, 1, 2]]
#            matrix[roiF-1, roiL-1] += 1
            
        # Save the matrix
#        filename = subName[0]+'_'+subName[1]+'__cmat_'+str(r)+'.npy'
#        filepath = inPath+'fibers/matrices/'+filename #op.join(gconf.get_cmt_fibers4subject(sid), 'matrices', filename)
#        np.save(filepath, matrix)
    print '#-----------------------------------------------------------------#\n'
							
    print '###################################################################\r'
################################################################################


################################################################################
# TESTING
def run(conf, subject_tuple):
    """ Run the connection matrix step
    
    Parameters
    ----------
    conf : PipelineConfiguration object
    subject_tuple : tuple, (subject_id, timepoint)
      Process the given subject
       
    """
    # setting the global configuration variable
    globals()['gconf'] = conf
    globals()['sid']   = subject_tuple
    start              = time()
    
    # Call
#    DTB__cmat_shape()
#    DTB__cmat_scalar()
    DTB__cmat()
    
    log.info("Connection matrix module took %s seconds to process." % (time()-start))
################################################################################
################################################################################
