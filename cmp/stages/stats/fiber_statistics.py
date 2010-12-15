import os, os.path as op
import sys
from time import time
from ...logme import *

def fiberlength_histogram():

    try:
        import numpy as np    
        import matplotlib.mlab as mlab
        import matplotlib.pyplot as plt
    except ImportError:
        return
    
    # get fiber length array
    fiblen = np.load(op.join(gconf.get_cmp_fibers(), 'lengths.npy'))
    
    # the histogram of the data
    n, bins, patches = plt.hist(fiblen, facecolor='green', alpha=0.75)
    
    plt.xlabel('Fiber length')
    plt.ylabel('Number of Fibers')
    plt.title(r'The fiberlength histogram')
    plt.grid(True)

    plt.savefig(op.join(gconf.get_stats(), 'fiberlength_histogram.png'))


def run(conf):
    """ Run the fiber statistics module
    
    Parameters
    ----------
    conf : PipelineConfiguration object
        
    """
    # setting the global configuration variable
    globals()['gconf'] = conf
    globals()['log'] = gconf.get_logger() 
    start = time()
    
    log.info("Statistics Module")
    log.info("=================")

    fiberlength_histogram()
    
    log.info("Module took %s seconds to process." % (time()-start))
    
    if not len(gconf.emailnotify) == 0:
        msg = "Statistics module finished!\nIt took %s seconds." % int(time()-start)
        send_email_notification(msg, gconf, log)
        
def declare_inputs(conf):
    """Declare the inputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)
    
    conf.pipeline_status.AddStageInput(stage, conf.get_cmp_fibers(), 'lengths.npy', 'lengths-npy')
        
        
def declare_outputs(conf):
    """Declare the outputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)
            
    conf.pipeline_status.AddStageOutput(stage, conf.get_stats(), 'fiberlength_histogram.png', 'fiberlength_histogram-png')
    