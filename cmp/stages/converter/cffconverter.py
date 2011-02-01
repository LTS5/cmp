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

def add_fibers2connectome(connectome):
    log.info("Adding filtered fibers to connectome...")
    trkfile = op.join(gconf.get_cmp_fibers(), 'streamline_filtered.trk')
    # XXX: add tractography, wait for cfflib adder method
    

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
        cnet = cf.CNetwork(name = 'cmat.pickle')
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
    c.connectome_meta.set_reference(gconf.reference)
    c.connectome_meta.set_species(gconf.species)
    c.connectome_meta.set_description(gconf.description)

    mydict = {}
    for ele in gconf.subject_metadata:
        mydict[str(ele.key), str(ele.value)]        
    mydict['subject_name'] = gconf.subject_name
    mydict['subject_timepoint'] = gconf.subject_timepoint
    mydict['subject_workingdir'] = gconf.subject_workingdir
    c.connectome_meta.update_metadata(mydict)

    # XXX: depending on what was checked
    if gconf.cff_fullnetworkpickle:
        # adding networks
        add_cmat2connectome(c, addcmatpickle = gconf.cff_cmatpickle)
        
    if gconf.cff_filteredfibers:
        add_fibers2connectome(c)
        
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
