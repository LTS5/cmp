import os, os.path as op
from time import time
from ...logme import *
import cmt.util as util

def spline_filtering():
    log.info("Spline filtering the fibers")
    log.info("===========================")

    src = op.join(gconf.get_cmt_fibers(), 'streamline.trk') 
    ren = op.join(gconf.get_cmt_fibers(), 'streamline_beforespline.trk')
    
    # rename original fiber
    util.myrename(src, ren, log)

    sp_cmd = 'spline_filter %s 1 %s' % (ren, src)
    
    runCmd( sp_cmd, log )
    
#    os.rename(op.join(gconf.get_cmt_fibers(), "tmp.trk"), op.join(gconf.get_cmt_fibers(), "streamline.trk"))
    
    log.info("[ DONE ]")
    
    
def filter_fibers():
    
    log.info("Fiber Filtering")
    log.info("===============")

    try:
        import dipy
    except ImportError:
        log.info("Can not run filter fibers because DiPy is missing")
        return

    intrk = op.join(gconf.get_cmt_fibers(), 'streamline.trk')
    outtrk = op.join(gconf.get_cmt_fibers(), 'streamline_beforefilter.trk')
    
    util.myrename(intrk, outtrk)
    
    # find a balance between discarding spurious fibers and still
    # keep cortico-cortico ones, amidst of not having ground-truth
    
    # compute a downsampled version of the fibers using 4 points
    
    # discard smaller than x mm fibers
    # and which have a minimum angle smaller than y degrees
    
    
def run(conf):
    """ Run the fiber filtering
    
    Parameters
    ----------
    conf : PipelineConfiguration object
        
    """
    # setting the global configuration variable
    globals()['gconf'] = conf
    globals()['log'] = gconf.get_logger() 
    start = time()
    
    spline_filtering()
    
    log.info("Module took %s seconds to process." % (time()-start))
    
    if not len(gconf.emailnotify) == 0:
        msg = "Fiber filtering module finished!\nIt took %s seconds." % int(time()-start)
        send_email_notification(msg, gconf.emailnotify, log)  
        
def declare_inputs(conf):
    """Declare the inputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)
    fibers_path = conf.get_cmt_fibers()
    
    conf.pipeline_status.AddStageInput(stage, fibers_path, 'streamline.trk', 'streamline-trk')
        
def declare_outputs(conf):
    """Declare the outputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)
    fibers_path = conf.get_cmt_fibers()
    
    conf.pipeline_status.AddStageOutput(stage, fibers_path, 'streamline.trk', 'streamline-trk')
            
                      

