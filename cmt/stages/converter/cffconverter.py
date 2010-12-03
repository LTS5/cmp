""" Convert a selection of files from the subject folder into
a connectome file format for visualization and analysis in the connectomeviewer """

import os, os.path as op
import sys
from time import time
from ...logme import *

def convert_cmat2cff(cmat_fname, cff_fname):
    """ Converts a given cmat file produced by the pipeline into
    a connectome file
    
    Parameters
    ----------
    cmat_fname : string
        The input filename of the graph pickle. Ending .pickle
    cff_fname : string
        Absolute path to the output filename of the cff
    """
    
    cmat = nx.read_gpickle(cmat_fname)
        
    # first, simply create connectome file for networks
    # use the default. graphml, see for correct node labels (integers) to match
    # import cfflib
    # tutorial steps from cfflib for creation, using cmat
    # number of fibers
    # average length
    print "Convert to a connectome file"

    # loop over resolutions and store number of fibers in graphml


def convert2cff():
    
    # filename from metadata name
    # define path in folder structure, maybe root
    
    outputcff = ''
    
    convert_cmat2cff(op.join(gconf.get_cmt_matrices(), 'cmat.pickle'), outputcff)
    
    
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
        msg = "CFF Converter module finished!\nIt took %s seconds." % int(time()-start)
        send_email_notification(msg, gconf.emailnotify, log)
