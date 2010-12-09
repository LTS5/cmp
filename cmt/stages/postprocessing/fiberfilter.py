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
    ren = op.join(gconf.get_cmt_fibers(), 'streamline_splinefiltered.trk')
    
    sp_cmd = 'spline_filter %s 1 %s' % (src, ren)    
    runCmd( sp_cmd, log )
    
    le = compute_length_array(ren)
    
#    os.rename(op.join(gconf.get_cmt_fibers(), "tmp.trk"), op.join(gconf.get_cmt_fibers(), "streamline.trk"))
    
    log.info("[ DONE ]")
    

def compute_length_array(trkfile=None, streams=None, savefname = 'lengths.npy'):
    if streams is None and not trkfile is None:
        log.info("Compute length array for fibers in %s" % trkfile)
        streams, hdr = tv.read(trkfile, as_generator = True)
        n_fibers = hdr['n_count']
        if n_fibers == 0:
            msg = "Header field n_count of trackfile %s is set to 0. No track seem to exist in this file." % trkfile
            log.error(msg)
            raise Exception(msg)
    else:
        n_fibers = len(streams)
        
    leng = np.zeros(n_fibers, dtype = np.float)
    for i,fib in enumerate(streams):
        leng[i] = util.length(fib[0])
    
    # store length array
    lefname = op.join(gconf.get_cmt_fibers(), savefname)
    np.save(lefname, leng)
    log.info("Store lengths array to: %s" % lefname)
    
    return leng
    

def filter_fibers(applied_spline=False):
    
    log.info("Cut Fiber Filtering")
    log.info("===================")
    log.info("Was spline filtering applied? %s" % applied_spline)
    
    if applied_spline:
        intrk = op.join(gconf.get_cmt_fibers(), 'streamline_splinefiltered.trk')
    else:
        intrk = op.join(gconf.get_cmt_fibers(), 'streamline.trk')
        
    log.info("Input file for fiber cutting is: %s" % intrk)
    
    outtrk = op.join(gconf.get_cmt_fibers(), 'streamline_cutfiltered.trk')
    
    # compute length array
    le = compute_length_array(intrk, savefname = 'lengths_beforecutfiltered.npy')
    
    # cut the fibers smaller than value
    reducedidx = np.where(le>gconf.fiber_cutoff)[0]
    
    # load trackfile (downside, needs everything in memory)
    fibold, hdrold = tv.read(intrk)
    
    # rewrite the track vis file with the reduced number of fibers
    outstreams = []
    for i in reducedidx:
        outstreams.append( fibold[i] )
    
    n_fib_out = len(outstreams)
    hdrnew = hdrold.copy()
    hdrnew['n_count'] = n_fib_out
    
    log.info("Compute length array for cutted fibers")
    le = compute_length_array(streams=outstreams)
    log.info("Write out file: %s" % outtrk)
    tv.write(outtrk, outstreams, hdrnew)
    
    # ----
    # extension idea
    
    # find a balance between discarding spurious fibers and still
    # keep cortico-cortico ones, amidst of not having ground-truth
    
    # compute a downsampled version of the fibers using 4 points
    
    # discard smaller than x mm fibers
    # and which have a minimum angle smaller than y degrees
    
def inspect(gconf):
    """ Inspect the results of this stage """
    log = gconf.get_logger()
    trkcmd = 'trackvis %s' % op.join(gconf.get_cmt_fibers(), 'streamline_filtered.trk')
    runCmd( trkcmd, log )
    
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
        if gconf.apply_fiberlength:
            filter_fibers(applied_spline=True)
            util.myrename(op.join(gconf.get_cmt_fibers(), 'streamline_cutfiltered.trk'),
                          op.join(gconf.get_cmt_fibers(), 'streamline_filtered.trk'), log)            
        else:
            util.myrename(op.join(gconf.get_cmt_fibers(), 'streamline_splinefiltered.trk'),
                          op.join(gconf.get_cmt_fibers(), 'streamline_filtered.trk'), log)
    else:
        if gconf.apply_fiberlength:
            filter_fibers(applied_spline=False)
            util.myrename(op.join(gconf.get_cmt_fibers(), 'streamline_cutfiltered.trk'),
                          op.join(gconf.get_cmt_fibers(), 'streamline_filtered.trk'), log)    
            
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
    
    conf.pipeline_status.AddStageOutput(stage, fibers_path, 'streamline_filtered.trk', 'streamline-trk')
    conf.pipeline_status.AddStageOutput(stage, conf.get_cmt_fibers(), 'lengths.npy', 'lengths-npy') 
                      

