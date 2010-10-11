import os, os.path as op
from time import time
from glob import glob
import re
import sys
import numpy as np
import pickle
import nibabel
import math
import networkx as nx

################################################################################
def DTB__load_endpoints_from_trk(fib, hdr):
    """ 
    Function
    ----------
    Get the endpoints and the length from each fibers
        
    Inputs
    ----------
    fib: the fibers data
    hdr: the header of the fibers.trk
    
    Outputs
    ----------
    endpoints: matrix of size [#fibers, 2, 3] containing for each fiber the
               index of its first and last point
    length   : array of size [#fibers] containing the length (euclidian) of each fiber
    
    Date
    ----------
    2010-08-20
    
    Major modifications
    ----------
    2010-10-11
    
    Authors
    ----------
    Christophe Chenes, Stephan Gerhard
    """

    log.info("============================")
    log.info("DTB__load_endpoints_from_trk")
    
    # Init
    n         = len(fib)
    endpoints = np.zeros( (n, 2, 3) )
    length    = np.zeros( (n) )
    pc        = -1

    # Computation for each fiber
    for i, fi in enumerate(fib):
    
        # Percent counter
        pcN = int(round( float(100*i)/n ))
        if pcN > pc and pcN%1 == 0:	
            pc = pcN
            print '\t\t%4.0f%%' % (pc)

        f = fi[0]
    
        # store startpoint
        endpoints[i,0,:] = f[0,:]
        # store endpoint
        endpoints[i,1,:] = f[-1,:]
        
        # calculate length: euclidian distance over the points
        l = 0.0
        for j in xrange(1, f.shape[0]):
            a = f[j-1,:]
            b = f[j,:]
            l += np.linalg.norm(a-b)
        length[i] = l	  
            
        # Translate from mm to index
        endpoints[i,0,0] = int( endpoints[i,0,0] / float(hdr['voxel_size'][0]))
        endpoints[i,0,1] = int( endpoints[i,0,1] / float(hdr['voxel_size'][1]))
        endpoints[i,0,2] = int( endpoints[i,0,2] / float(hdr['voxel_size'][2]))
        endpoints[i,1,0] = int( endpoints[i,1,0] / float(hdr['voxel_size'][0]))
        endpoints[i,1,1] = int( endpoints[i,1,1] / float(hdr['voxel_size'][1]))
        endpoints[i,1,2] = int( endpoints[i,1,2] / float(hdr['voxel_size'][2]))
		
    # Return the matrices  
    return endpoints, length  
	
    log.info("done")
    log.info("============================")
    print '\n###################################################################\n'
################################################################################


################################################################################
def DTB__cmat(fib, hdr): 
    """ 
    Function
    ----------
    Create the connection matrix for each resolution using fibers and ROIs.
        
    Inputs
    ----------
    fib: the fibers data
    hdr: the header of the fibers.trk
    
    Output
    ----------
    cmat.dat: the connection matrix
    
    Date
    ----------
    2010-09-10
    
    Major modifications:
    ----------
    2010-10-11
    
    Authors
    ----------
    Christophe Chenes, Stephan Gerhard 
    """
    
    log.info("=========")
    log.info("DTB__cmat")	
          	
    # Get the endpoints for each fibers
    log.info("-------------")
    log.info("Get endpoints")
    en_fname  = op.join(gconf.get_cmt_fibers4subject(sid), 'TEMP_endpoints.npy')
    ep_fname  = op.join(gconf.get_cmt_fibers4subject(sid), 'TEMP_epLen.npy')
    if    not os.path.isfile(en_fname) or not os.path.isfile(ep_fname):
        log.info('computing endpoints')
        endpoints, epLen = DTB__load_endpoints_from_trk(fib, hdr)
        log.info('saving endpoints')
        np.save(en_fname, endpoints)
        np.save(ep_fname, epLen)
    else:
        log.info('loading endpoints')
        endpoints = np.load(en_fname)
        epLen     = np.load(ep_fname)
    log.info("-------------")
	
    # For each resolution
    log.info("--------------------")
    log.info("Resolution treatment")
    resolution = gconf.parcellation.keys()
    cmat = {} # NEW matrix
    for r in resolution:
        log.info("\tresolution = "+r)
      
        # Open the corresponding ROI
        log.info("\tOpen the corresponding ROI")
        roi_fname = op.join(gconf.get_cmt_fsout4subject(sid), 'registered', 'HR__registered-T0-b0', r, 'ROI_HR_th.nii')
        roi       = nibabel.load(roi_fname)
        roiData   = roi.get_data()
        roiHeader = roi.get_header()
      
        # Create the matrix
        log.info("\tCreate and init the connection matrix")
        nROIs = roiData.max()
        G     = nx.Graph()
        G.add_nodes_from( range(1, nROIs+1) )
        dis = 0
        
        # For each endpoints
        for i in range(endpoints.shape[0]):
    
            # ROI start => ROI end
            startROI = roiData[endpoints[i, 0, 0], endpoints[i, 0, 1], endpoints[i, 0, 2]]
            endROI   = roiData[endpoints[i, 1, 0], endpoints[i, 1, 1], endpoints[i, 1, 2]]
            
            # Filter
            if startROI == 0 or endROI == 0:
                dis += 1
                continue
                
            # Add edge to graph
            if G.has_edge(startROI, endROI):
                G.edge[startROI][endROI]['fiblist'].append(i)
                G.edge[startROI][endROI]['fiblength'].append(epLen[i])
            else:
                G.add_edge(startROI, endROI, fiblist   = [i])
                G.add_edge(startROI, endROI, fiblength = [epLen[i]])   
        
        # Add the number of fiber per edge
        for ed in G.edges_iter(data=True):
            G.edge[ed[0]][ed[1]]['weight'] = len(ed[2]['fiblist'])   
        
        # Add all in the current resolution
        cmat.update({r: {'filename': roi_fname, 'graph': G}})  
        
    log.info("--------------------")
    
    # Save the connection matrix
    nx.write_gpickle(cmat, op.join(gconf.get_cmt_matrices4subject(sid), 'cmat.pickle'))
    
    log.info("done")
    log.info("=========")							
################################################################################

################################################################################
def run(conf, subject_tuple):
    """ 
    Run the connection matrix module
        
    Parameters
    ----------
    conf : PipelineConfiguration object
    subject_tuple : tuple, (subject_id, timepoint)
      Process the given subject
      
    Functions
    ----------
    DTB__cmat: create the connection matrix
    DTB__cmat_shape: get some shape informations about each fibers (length)
    DTB__cmat_scalar: get some scalar informations about each fibers (gfa)
        
    Date
    ----------
    2010-09-10
    
    Authors
    ----------
    Christophe Chenes, Stephan Gerhard 
       
    """
        
    # setting the global configuration variable
    globals()['gconf'] = conf
    globals()['sid']   = subject_tuple
    start              = time()
    globals()['log']   = conf.get_logger4subject(subject_tuple)
    
    log.info("########################")
    log.info("Connection matrix module")
    
    # Read the fibers one and for all
    log.info("===============")
    log.info("Read the fibers")
    fibFilename = op.join(gconf.get_cmt_fibers4subject(sid), 'streamline.trk')
    fib, hdr    = nibabel.trackvis.read(fibFilename, False)
    log.info("done")
    log.info("===============")
    
    # Call
#    DTB__cmat_shape(fib, hdr)
#    DTB__cmat_scalar(fib, hdr)
    DTB__cmat(fib, hdr)
    
    log.info("Connection matrix module took %s seconds to process" % (time()-start))
    log.info("########################")
################################################################################
