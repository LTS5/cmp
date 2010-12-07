import os, os.path as op
from time import time
from ...logme import *
import cmt.util as util
import numpy as np
import nibabel.trackvis as tv
    
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
    

def compute_length_array(trkfile):

    try:
        from cviewer.libs.dipy.core.track_metrics import length
    except ImportError:
        return
    
    streams, hdr = tv.read(trkfile, as_generator = True)
    n_fibers = hdr['n_count']
    if n_fibers == 0:
        return
    leng = np.zeros(n_fibers, dtype = np.float)
    for i,fib in enumerate(streams):
        leng[i] = length(fib[0])
    return leng
    

def filter_fibers():
    
    log.info("Fiber Filtering")
    log.info("===============")

    intrk = op.join(gconf.get_cmt_fibers(), 'streamline.trk')
    outtrk = op.join(gconf.get_cmt_fibers(), 'streamline_beforelengthfilter.trk')
    
    # compute length array
    le = compute_length_array(intrk)
    
    # cut the fibers smaller than value
    cut = 30.0
    reducedidx = np.where(le>30.0)[0]
    
    # load trackfile (downside, needs everything in memory)
    fibold, hdrold = tv.read(intrk)
    
    # rewrite the track vis file with the reduced number of fibers
    outstreams = []
    for i in reducedidx:
        outstreams.append( (fibold[i],None,None) )
    
    n_fib_out = len(outstreams)
    hdrnew = tv.empty_header(hdrold)
    hdrnew['n_count'] = n_fib_out
    
    util.myrename(intrk, outtrk)
    tv.write(outtrk, outstreams, hdrnew)
    
    # ----
    
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
    
    if gconf.apply_splinefilter:
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
            
                      

