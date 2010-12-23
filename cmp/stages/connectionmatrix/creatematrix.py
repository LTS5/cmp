import os, os.path as op
from time import time
from glob import glob
import numpy as np
import nibabel
import networkx as nx
from ...logme import *

def load_endpoints_from_trk(fib, voxelSize):
    """ Get the endpoints from each fibers
        
    Parameters
    ----------
    fib: the fibers data
    voxelSize: 3-tuple containing the voxel size of the ROI image
    
    Returns
    -------
    endpoints: matrix of size [#fibers, 2, 3] containing for each fiber the
               index of its first and last point
    """

    log.info("========================")
    log.info("load_endpoints_from_trk")
    
    # Init
    n         = len(fib)
    endpoints = np.zeros( (n, 2, 3) )
    pc        = -1

    # Computation for each fiber
    for i, fi in enumerate(fib):
    
        # Percent counter
        pcN = int(round( float(100*i)/n ))
        if pcN > pc and pcN%1 == 0:	
            pc = pcN
            log.info('%4.0f%%' % (pc))

        f = fi[0]
    
        # store startpoint
        endpoints[i,0,:] = f[0,:]
        # store endpoint
        endpoints[i,1,:] = f[-1,:]
        
        # Translate from mm to index
        endpoints[i,0,0] = int( endpoints[i,0,0] / float(voxelSize[0]))
        endpoints[i,0,1] = int( endpoints[i,0,1] / float(voxelSize[1]))
        endpoints[i,0,2] = int( endpoints[i,0,2] / float(voxelSize[2]))
        endpoints[i,1,0] = int( endpoints[i,1,0] / float(voxelSize[0]))
        endpoints[i,1,1] = int( endpoints[i,1,1] / float(voxelSize[1]))
        endpoints[i,1,2] = int( endpoints[i,1,2] / float(voxelSize[2]))
		
    # Return the matrices  
    return endpoints  
	
    log.info("done")
    log.info("========================")

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
    scalarFields = np.array(gconf.get_cmp_scalarfields())
    pc           = -1
    for s in range(0, scalarFields.shape[0]):
        scalarFile = nibabel.load(scalarFields[s, 1])
        scalarData = scalarFile.get_data()
        scalarVoxelSize = scalarFile.get_header().get_zooms()
        
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
                x = int( crtFiber[j,0] / float(scalarVoxelSize[0]))
                y = int( crtFiber[j,1] / float(scalarVoxelSize[1]))
                z = int( crtFiber[j,2] / float(scalarVoxelSize[2]))
                crtScalar[j] = scalarData[x, y, z]
            scalarInfo.append(crtScalar)
        scalars.update({scalarFields[s, 0]: scalarInfo})
    return scalars               
    
    log.info("done")
    log.info("========================")

def cmat(): 
    """ Create the connection matrix for each resolution using fibers and ROIs.
        
    Parameters
    ----------
    fib: the fibers data
    hdr: the header of the fibers.trk
    
    Returns
    -------
    cmat.dat: the connection matrix

    """
          	
    # create the endpoints for each fibers
    en_fname  = op.join(gconf.get_cmp_fibers(), 'endpoints.npy')
    ep_fname  = op.join(gconf.get_cmp_fibers(), 'lengths.npy')
    intrk = op.join(gconf.get_cmp_fibers(), 'streamline_filtered.trk')

    fib, hdr    = nibabel.trackvis.read(intrk, False)
    
    # Previously, load_endpoints_from_trk() used the voxel size stored
    # in the track hdr to transform the endpoints to ROI voxel space.
    # This only works if the ROI voxel size is the same as the DSI/DTI
    # voxel size.  In the case of DTI, it is not.  
    # We do, however, assume that all of the ROI images have the same
    # voxel size, so this code just loads the first one to determine
    # what it should be
    firstROIFile = op.join(gconf.get_cmp_tracto_mask_tob0(), 
                           gconf.parcellation.keys()[0],
                           'ROI_HR_th.nii.gz')
    firstROI = nibabel.load(firstROIFile)
    roiVoxelSize = firstROI.get_header().get_zooms()
    log.info('Computing endpoints')
    endpoints = load_endpoints_from_trk(fib, roiVoxelSize)
    log.info('Saving endpoints')
    np.save(en_fname, endpoints)

    # load fiber lengths array
    epLen     = np.load(ep_fname)
	
	# Get the scalars informations
#    log.info("========================")
#    log.info("Get scalars info")
#    scalarInfo = np.array(gconf.get_cmp_scalarfields(sid))
#    sc_fname = op.join( gconf.get_cmp_matrices(), 'scalars.pickle' )
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
	
    # For each resolution
    log.info("========================")
    log.info("Resolution treatment")
    resolution = gconf.parcellation.keys()
    cmat = {}
    for r in resolution:
        log.info("Resolution = "+r)
      
        # Open the corresponding ROI
        log.info("Open the corresponding ROI")
        roi_fname = op.join(gconf.get_cmp_tracto_mask_tob0(), r, 'ROI_HR_th.nii.gz')
        roi       = nibabel.load(roi_fname)
        roiData   = roi.get_data()
      
        # Create the matrix
        nROIs = gconf.parcellation[r]['number_of_regions']
        log.info("Create the connection matrix (%s rois)" % nROIs)
        G     = nx.Graph()
        # add node information from parcellation
        gp = nx.read_graphml(gconf.parcellation[r]['node_information_graphml'])
        for u,d in gp.nodes_iter(data=True):
            G.add_node(int(u), d)

        #G.add_nodes_from( range(1, int(nROIs)+1) )
        dis = 0
        
        # For each endpoints
        log.info("Fill the connection matrix")
        for i in range(endpoints.shape[0]):
    
            # ROI start => ROI end

            try:
                startROI = int(roiData[endpoints[i, 0, 0], endpoints[i, 0, 1], endpoints[i, 0, 2]])
                endROI   = int(roiData[endpoints[i, 1, 0], endpoints[i, 1, 1], endpoints[i, 1, 2]])
            except IndexError:
                log.error("AN INDEXERROR EXCEPTION OCCURED FOR FIBER %s. PLEASE CHECK ENDPOINT GENERATION" % i)
                continue
            
            # Filter
            if startROI == 0 or endROI == 0:
                dis += 1
                continue
            
            if startROI > nROIs or endROI > nROIs:
                log.debug("Start or endpoint of fiber terminate in a voxel which is labeled higher")
                log.debug("than is expected by the parcellation node information.")
                log.debug("Start ROI: %i, End ROI: %i" % (startROI, endROI))
                log.debug("This needs investigation!")
                continue
            
            # Add edge to graph
            if G.has_edge(startROI, endROI):
                G.edge[startROI][endROI]['fiblist'].append(i)
                G.edge[startROI][endROI]['fiblength'].append(epLen[i])          
            else:
                G.add_edge(startROI, endROI, fiblist   = [i])
                G.add_edge(startROI, endROI, fiblength = [epLen[i]])
                
        log.error("Found %i fibers that start or terminate in a voxel which is not labeled. (zero value)" % dis)
  
                                
        # Add all in the current resolution
        cmat.update({r: {'filename': roi_fname, 'graph': G}})  
        
    log.info("done")
    log.info("========================")
        
    # Save the connection matrix
    log.info("========================")
    log.info("Save the connection matrix")
    nx.write_gpickle(cmat, op.join(gconf.get_cmp_matrices(), 'cmat.pickle'))
    log.info("done")
    log.info("========================")						

def run(conf):
    """ Run the connection matrix module
    
    Parameters
    ----------
    conf : PipelineConfiguration object
    
    """
    # setting the global configuration variable
    globals()['gconf'] = conf
    globals()['log'] = gconf.get_logger() 
    start = time()
    
    cmat()
            
    log.info("Module took %s seconds to process." % (time()-start))
    
    if not len(gconf.emailnotify) == 0:
        msg = "Fiber filtering module finished!\nIt took %s seconds." % int(time()-start)
        send_email_notification(msg, gconf, log)  
        

def declare_inputs(conf):
    """Declare the inputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)
    
    conf.pipeline_status.AddStageInput(stage, conf.get_cmp_fibers(), 'streamline_filtered.trk', 'streamline-trk')
    
    for r in conf.parcellation.keys():
        conf.pipeline_status.AddStageInput(stage, op.join(conf.get_cmp_tracto_mask_tob0(), r), 'ROI_HR_th.nii.gz', 'ROI_HR_th_%s-nii-gz' % r)
        
def declare_outputs(conf):
    """Declare the outputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)
            
    conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_matrices(), 'cmat.pickle', 'cmat-pickle')
    conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fibers(), 'endpoints.npy', 'endpoints-npy')       
    
