""" Convert a selection of files from the subject folder into
a connectome file format for visualization and analysis in the connectomeviewer """

import os, os.path as op
import sys
from time import time
from ...logme import *
import networkx as nx
import numpy as np
try:
    import cfflib as cf
except ImportError:
    print "Please install cfflib to use the connectome file format converter"

def add_fibersoriginal2connectome(connectome):

    log.info("Adding original fibers to connectome...")

    fibers_path = gconf.get_cmp_fibers()
    
    ctr = cf.CTrack(name='Original Tractography',
                     src=op.join(fibers_path, 'streamline.trk'),
                      fileformat='TrackVis', dtype='OriginalFibers')
    
    connectome.add_connectome_track(ctr)

    
def add_fibers2connectome(connectome):
    
    log.info("Adding filtered fibers to connectome...")
    
    fibers_path = gconf.get_cmp_fibers()
    
    ctr = cf.CTrack(name='Filtered Tractography',
                     src=op.join(fibers_path, 'streamline_filtered.trk'),
                      fileformat='TrackVis',dtype='FilteredFibers')
    # add filter settings as metadata
    ctr.update_metadata({'spline_filtered' : str(gconf.apply_splinefilter),
                        'fiber_cutoff_lower': gconf.fiber_cutoff_lower,
                        'fiber_cutoff_upper': gconf.fiber_cutoff_upper})

    connectome.add_connectome_track(ctr)
    
def add_fiberarr2connectome(connectome):
    
    log.info("Adding fiber arrays to connectome...")
    
    fibers_path = gconf.get_cmp_fibers()
    
    cda = cf.CData(name="Filtered fiber length",
                   src=op.join(fibers_path, 'lengths.npy'),
                   fileformat='NumPy',
                   dtype='FilteredFiberLengthArray')

    connectome.add_connectome_data(cda)

    log.info("Adding fiber endpoints array to connectome...")
        
    cda = cf.CData(name="Fiber endpoints",
                   src=op.join(fibers_path, 'endpoints.npy'),
                   fileformat='NumPy',
                   dtype='FiberEndpoints')
    
    log.info("Adding fiber endpoints (mm) array to connectome...")
        
    cda = cf.CData(name="Fiber endpoints (mm)",
                   src=op.join(fibers_path, 'endpointsmm.npy'),
                   fileformat='NumPy',
                   dtype='FiberEndpoints')
    connectome.add_connectome_data(cda)

    log.info("Adding fiber mean curvature array to connectome...")
        
    cda = cf.CData(name="Fiber mean curvature",
                   src=op.join(fibers_path, 'meancurvature.npy'),
                   fileformat='NumPy',
                   dtype='FiberCurvature')
    connectome.add_connectome_data(cda)

    resolution = gconf.parcellation.keys()
    for r in resolution:
        log.info("Adding fiber labels array (%s) to connectome..." % str(r))
        
        cda = cf.CData(name="Fiber labels (%s)" % str(r),
                       src=op.join(fibers_path, 'fiberlabels_%s.npy' % str(r)),
                       fileformat='NumPy',
                       dtype='FiberLabels')
        connectome.add_connectome_data(cda)


    
def add_raw2connectome(connectome, type):
    
    log.info("Adding raw data to connectome (%s)..." % type)
    
    nifti_dir = op.join(gconf.get_nifti())
    cvol = None
    
    if type == 'rawdiffusion':
        if gconf.diffusion_imaging_model == 'DSI':
            if op.exists(op.join(nifti_dir, 'DSI.nii.gz')):
                cvol = cf.CVolume(name="Raw Diffusion",
                               src=op.join(nifti_dir, 'DSI.nii.gz'),
                               fileformat='Nifti1',
                               dtype='DSI')    
                
        elif gconf.diffusion_imaging_model == 'DTI':
            if op.exists(op.join(nifti_dir, 'DTI.nii.gz')):
                cvol = cf.CVolume(name="Raw Diffusion",
                               src=op.join(nifti_dir, 'DTI.nii.gz'),
                               fileformat='Nifti1',
                               dtype='DTI')
    elif type == 'rawT1':
        if op.exists(op.join(nifti_dir, 'T1.nii.gz')):
            cvol = cf.CVolume(name="Raw T1 image",
                           src=op.join(nifti_dir, 'T1.nii.gz'),
                           fileformat='Nifti1',
                           dtype='T1-weighted')
    elif type == 'rawT2':
        if op.exists(op.join(nifti_dir, 'T2.nii.gz')):
            cvol = cf.CVolume(name="Raw T2 image",
                           src=op.join(nifti_dir, 'T2.nii.gz'),
                           fileformat='Nifti1',
                           dtype='T2-weighted')
    
    if not cvol is None:
        connectome.add_connectome_volume(cvol)    

def add_scalars2connectome(connectome, type):
    
    log.info("Adding scalar fields to connectome...")
    
    scalarpath = gconf.get_cmp_scalars()
    
    if type == 'gfa':
        if gconf.diffusion_imaging_model == 'DSI':
            if op.exists(op.join(scalarpath, 'dsi_gfa.nii')):
                cvol = cf.CVolume(name="GFA Scalar Map",
                               src=op.join(scalarpath, 'dsi_gfa.nii'),
                               fileformat='Nifti1',
                               dtype='GFA')
                connectome.add_connectome_volume(cvol)    


def add_roiseg2connectome(connectome):
    
    log.info("Adding ROI segmentation to connectome...")

    # add about everything
    reg_path = gconf.get_cmp_tracto_mask()
        
    asegf = op.join(reg_path, 'aseg.nii.gz')
    ribbonf = op.join(reg_path, 'ribbon.nii.gz')    
    fsmaskf = op.join(reg_path, 'fsmask_1mm.nii.gz')
    unkf = op.join(reg_path, 'cc_unknown.nii.gz')
    
    if op.exists(asegf):
        cvol = cf.CVolume(name="Aseg segmentation volume",
                       src=asegf,
                       fileformat='Nifti1',
                       dtype='Segmentation')
        connectome.add_connectome_volume(cvol)
                
    if op.exists(ribbonf):
        cvol = cf.CVolume(name="Ribbon segmentation volume",
                       src=ribbonf,
                       fileformat='Nifti1',
                       dtype='Segmentation')
        connectome.add_connectome_volume(cvol)
                
    if op.exists(fsmaskf):
        cvol = cf.CVolume(name="White matter mask",
                       src=fsmaskf,
                       fileformat='Nifti1',
                       dtype='Segmentation')
        connectome.add_connectome_volume(cvol)
        
    if op.exists(unkf):
        cvol = cf.CVolume(name="CC and Unknown",
                       src=unkf,
                       fileformat='Nifti1',
                       dtype='Segmentation')
        connectome.add_connectome_volume(cvol)
                
    # is original T1 space
    for p in gconf.parcellation.keys():
        log.info("Adding volume ROI for resolution (original space): %s" % p)
        file = op.join(op.join(reg_path, p), 'ROI_HR_th.nii.gz')
        
        if op.exists(file):
            cvol = cf.CVolume(name="ROI Volume %s" % p,
                           src=file,
                           fileformat='Nifti1',
                           dtype='Segmentation')
            connectome.add_connectome_volume(cvol)
    
    # in space registred to b0
    reg_path = gconf.get_cmp_tracto_mask_tob0()
    for p in gconf.parcellation.keys():
        log.info("Adding volume ROI for resolution (in b0 space): %s" % p)
        file = op.join(op.join(reg_path, p), 'ROI_HR_th.nii.gz')
        
        if op.exists(file):
            cvol = cf.CVolume(name="ROI Scale %s (b0 space)" % p,
                           src=file,
                           fileformat='Nifti1',
                           dtype='Segmentation')
            connectome.add_connectome_volume(cvol)
        
def add_surfaces2connectome(connectome):
    
    log.info("Adding surfaces to connectome...")
    
    li = ['rh.pial', 'lh.pial',
          'rh.inflated', 'lh.inflated',
          'rh.sphere', 'lh.sphere',
          'rh.white', 'lh.white']
    
    fs_dir = gconf.get_fs()
    
    for i in li:
        outfile = op.join(fs_dir, 'surf', i+'.gii')
        cmd = 'mris_convert %s %s' % (op.join(fs_dir, 'surf', i), outfile)
        runCmd( cmd, log )
    
        if op.exists(outfile):
            csur = cf.CSurface(name="Surface %s" % i,
                           src=outfile,
                           fileformat='Gifti',
                           dtype='Surfaceset')
            
            connectome.add_connectome_surface(csur)
        
        
def add_cmat2connectome(connectome, addcmatpickle = False):
    log.info("Loading cmat.pickle....")
    cmat = nx.read_gpickle(op.join(gconf.get_cmp_matrices(), 'cmat.pickle'))
    resolution = gconf.parcellation.keys()
    for r in resolution:
        log.info("Adding connectome for resolution: %s" % r)
        # retrieve the graph
        g = cmat[r]['graph']
        # the graph to use for storage
        gs = nx.Graph()
        # read the parcellation graph for node information
        gp = nx.read_graphml(gconf.parcellation[r]['node_information_graphml'])
        for u,d in gp.nodes_iter(data=True):
            gs.add_node(int(u), d)
        # add edges
        for u,v,d in g.edges_iter(data=True):
            # measures to add, XXX
            di = { 'number_of_fibers' : len(d['fiblist']),
                   'average_fiber_length' : np.mean(d['fiblength'])
                  }
            gs.add_edge(u,v, di)
        cnet = cf.CNetwork(name = 'connectome_%s' % r)
        cnet.set_with_nxgraph(gs)
        cnet.update_metadata( { 'resolution' : r,
                                'segmentation_volume_filename' : cmat[r]['filename']})
        connectome.add_connectome_network(cnet)
        log.info("Done.")
        
    if addcmatpickle:
        log.info("Adding cmat.pickle to connectome...")
        cnet = cf.CNetwork(name = 'cmat')
        cnet.set_with_nxgraph('connectome_cmat', cmat)
        connectome.add_connectome_network(cnet)       
        log.info("Done.")

def convert2cff():
    
    # filename from metadata name
    # define path in folder structure, maybe root
    
    outputcff = op.join(gconf.get_cffdir(), '%s_%s.cff' % (gconf.subject_name, gconf.subject_timepoint))
    
    c = cf.connectome()
    
    # creating metadata
    c.connectome_meta.set_title('%s - %s' % (gconf.subject_name, gconf.subject_timepoint) )
    c.connectome_meta.set_creator(gconf.creator)
    c.connectome_meta.set_email(gconf.email)
    c.connectome_meta.set_publisher(gconf.publisher)
    c.connectome_meta.set_created(gconf.created)
    c.connectome_meta.set_modified(gconf.modified)
    c.connectome_meta.set_license(gconf.license)
    c.connectome_meta.set_rights(gconf.rights)
    c.connectome_meta.set_references(gconf.reference)
    c.connectome_meta.set_relation(gconf.relation)
    c.connectome_meta.set_species(gconf.species)
    c.connectome_meta.set_description(gconf.description)

    mydict = {}
    for ele in gconf.subject_metadata:
        if str(ele.key) == "":
            continue
        mydict[str(ele.key)] = str(ele.value)
        
    mydict['subject_name'] = gconf.subject_name
    mydict['subject_timepoint'] = gconf.subject_timepoint
    mydict['subject_workingdir'] = gconf.subject_workingdir
    c.connectome_meta.update_metadata(mydict)

    # XXX: depending on what was checked
    if gconf.cff_fullnetworkpickle:
        # adding networks
        add_cmat2connectome(c, addcmatpickle = gconf.cff_cmatpickle)
        
    if gconf.cff_originalfibers:
        add_fibersoriginal2connectome(c)
        
    if gconf.cff_filteredfibers:
        add_fibers2connectome(c)
        
    if gconf.cff_fiberarr:
        add_fiberarr2connectome(c)
        
    if gconf.cff_rawdiffusion:
        add_raw2connectome(c, 'rawdiffusion')
        
    if gconf.cff_rawT1:
        add_raw2connectome(c, 'rawT1')
        
    if gconf.cff_rawT2:
        add_raw2connectome(c, 'rawT2')
    
    if gconf.cff_scalars:
        add_scalars2connectome(c, 'gfa')
    
    if gconf.cff_roisegmentation:
        add_roiseg2connectome(c)    
    
    if gconf.cff_surfaces:
        add_surfaces2connectome(c)
    
    cf.save_to_cff(c,outputcff)
    
def run(conf):
    """ Run the CFF Converter module
    
    Parameters
    ----------
    conf : PipelineConfiguration object
        
    """
    # setting the global configuration variable
    globals()['gconf'] = conf
    globals()['log'] = gconf.get_logger() 
    start = time()
    
    log.info("Connectome File Converter")
    log.info("=========================")

    convert2cff()
    
    log.info("Module took %s seconds to process." % (time()-start))
    
    if not len(gconf.emailnotify) == 0:
        msg = ["CFF Converter", int(time()-start)]
        send_email_notification(msg, gconf, log)
        
def declare_inputs(conf):
    """Declare the inputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)
    
    conf.pipeline_status.AddStageInput(stage, conf.get_cmp_matrices(), 'cmat.pickle', 'cmat-pickle')
        
    
def declare_outputs(conf):
    """Declare the outputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)
       
    conf.pipeline_status.AddStageOutput(stage, conf.get_cffdir(), '%s_%s.cff' % (conf.subject_name, conf.subject_timepoint), 'connectome-cff')
