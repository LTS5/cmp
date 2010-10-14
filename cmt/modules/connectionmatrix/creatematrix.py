import os, os.path as op
from time import time
from glob import glob
import numpy as np
import nibabel
import networkx as nx


################################################################################
def load_endpoints_from_trk(fib, hdr):
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

    log.info("========================")
    log.info("load_endpoints_from_trk")
    
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
    log.info("========================")
    print '\n###################################################################\n'
################################################################################


################################################################################
def compute_scalars(fib, hdr):
    """ 
    Function
    ----------
    Get some scalar informations from the fibers and nifti files
        
    Inputs
    ----------
    fib: the fibers data
    hdr: the header of the fibers.trk
    
    Outputs
    ----------
    scalar1.npy: for each nifti file provided, save a matrix of size [#fibers, 5]
                      containing the data, mean, min, max and std for each fiber
    ...
    scalarN.npy: same
    
    Date
    ----------
    2010-09-05
    
    Author
    ----------
    Christophe Chenes
    """
    
    log.info("========================")
    log.info("Compute scalars")
        
    scalars      = {}
    scalarFields = np.array(gconf.get_cmt_scalarfields())
    pc           = -1
    for s in range(0, scalarFields.shape[0]):
        scalarFile = nibabel.load(scalarFields[s, 1])
        scalarData = scalarFile.get_data()
        scalarInfo = []
        for i,fi in enumerate(fib):
        
            # Percent counter
            pcN = int(round( float(100*i)/(len(fib)*scalarFields.shape[0]) ))
            if pcN > pc:	
                pc = pcN
                print '\t\t%4.0f%%' % (pc)
                
            crtFiber  = fi[0]
            crtScalar = np.zeros((crtFiber.shape[0]))
            for j in range(0, crtFiber.shape[0]):
                x = int( crtFiber[j,0] / float(hdr['voxel_size'][0]))
                y = int( crtFiber[j,1] / float(hdr['voxel_size'][0]))
                z = int( crtFiber[j,2] / float(hdr['voxel_size'][0]))
                crtScalar[j] = scalarData[x, y, z]
            scalarInfo.append(crtScalar)
        scalars.update({scalarFields[s, 0]: scalarInfo})
    return scalars               
    
    log.info("done")
    log.info("========================")
################################################################################


################################################################################
def cmat(fib, hdr): 
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
          	
    # Get the endpoints for each fibers
    log.info("========================")
    log.info("Get endpoints")
    en_fname  = op.join(gconf.get_cmt_fibers(), 'endpoints.npy')
    ep_fname  = op.join(gconf.get_cmt_fibers(), 'lengths.npy')
    if not os.path.isfile(en_fname) or not os.path.isfile(ep_fname):
        log.info('\tcomputing endpoints')
        endpoints, epLen = load_endpoints_from_trk(fib, hdr)
        log.info('\tsaving endpoints')
        np.save(en_fname, endpoints)
        np.save(ep_fname, epLen)
    else:
        log.info('\tloading endpoints')
        endpoints = np.load(en_fname)
        epLen     = np.load(ep_fname)
    log.info("done")
    log.info("========================")
	
	# Get the scalars informations
#    log.info("========================")
#    log.info("Get scalars info")
#    scalarInfo = np.array(gconf.get_cmt_scalarfields(sid))
#    sc_fname = op.join( gconf.get_cmt_matrices(), 'scalars.pickle' )
#    if not os.path.isfile(sc_fname):
#        log.info('\tcomputing scalars')
#        scalars = compute_scalars(fib, hdr)
#        log.info('\tsaving scalars')
#        nx.write_gpickle(scalars, sc_fname)         
#    else:
#        log.info('\tloading scalars')
#        scalars = nx.read_gpickle(sc_fname)
#    log.info("done")
#    log.info("========================")
	
    # Load the mat_mask 
    # TODO one mat_mask per resolution ?
    matMask = np.load(gconf.get_matMask4subject())
	
    # For each resolution
    log.info("========================")
    log.info("Resolution treatment")
    resolution = gconf.parcellation.keys()
    cmat = {} 
    for r in resolution:
        log.info("\tresolution = "+r)
      
        # Open the corresponding ROI
        log.info("\tOpen the corresponding ROI")
        roi_fname = op.join(gconf.get_cmt_fsout(), 'registered', 'HR__registered-TO-b0', r, 'ROI_HR_th.nii')
        roi       = nibabel.load(roi_fname)
        roiData   = roi.get_data()
      
        # Create the matrix
        log.info("\tCreate the connection matrix")
        nROIs = roiData.max()
        G     = nx.Graph()
        G.add_nodes_from( range(1, nROIs+1) )
        dis = 0
        
        # For each endpoints
        log.info("\tFill the connection matrix")
        for i in range(endpoints.shape[0]):
    
            # ROI start => ROI end
            startROI = roiData[endpoints[i, 0, 0], endpoints[i, 0, 1], endpoints[i, 0, 2]]
            endROI   = roiData[endpoints[i, 1, 0], endpoints[i, 1, 1], endpoints[i, 1, 2]]
            
            # Filter
            if startROI == 0 or endROI == 0:
                dis += 1
                continue
                
            # Add edge to graph
            # TODO Find an automatic way for the scalars informations
            if G.has_edge(startROI, endROI):
                G.edge[startROI][endROI]['fiblist'].append(i)
                G.edge[startROI][endROI]['fiblength'].append(epLen[i])   
#                G.edge[startROI][endROI]['gfa'].append(scalars['gfa'][i])          
            else:
                G.add_edge(startROI, endROI, fiblist   = [i])
                G.add_edge(startROI, endROI, fiblength = [epLen[i]])   
#                G.add_edge(startROI, endROI, gfa = [scalars['gfa'][i]])   
        
        # Add the number of fiber per edge
        for ed in G.edges_iter(data=True):
            G.edge[ed[0]][ed[1]]['weight'] = len(ed[2]['fiblist'])   
        
        # Filter with mat_mask
        for i in range (1,matMask.shape[0]+1):
            for j in range (i,matMask.shape[0]+1):
                if G.has_edge(i,j) and matMask[i-1,j-1] == 0:
                    print 'remove edge ['+str(i)+']['+str(j)+']'
                    G.remove_edge(i,j)
                        
        # Add all in the current resolution
        cmat.update({r: {'filename': roi_fname, 'graph': G}})  
        
    log.info("done")
    log.info("========================")
        
    # Save the connection matrix
    log.info("========================")
    log.info("Save the connection matrix")
    nx.write_gpickle(cmat, op.join(gconf.get_cmt_matrices(), 'cmat.pickle'))
    log.info("done")
    log.info("========================")						
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
    cmat: create the connection matrix
    cmat_shape: get some shape informations about each fibers (length)
    cmat_scalar: get some scalar informations about each fibers (gfa)
        
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
    log.info("========================")
    log.info("Read the fibers")
    fibFilename = op.join(gconf.get_cmt_fibers(), 'streamline.trk')
    fib, hdr    = nibabel.trackvis.read(fibFilename, False)
    log.info("done")
    log.info("========================")
    
    # Call
    cmat(fib, hdr)
        
    log.info("Connection matrix module took %s seconds to process" % (time()-start))
    log.info("########################")
################################################################################


