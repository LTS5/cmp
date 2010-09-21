import os, os.path as op
from time import time
from ...logme import *
from glob import glob
import subprocess

def convert_wm_mask():
    
    log.info("Convert WM MASK to 8 bit/pixel")
    log.info("==============================")
    
    infile = op.join(gconf.get_cmt_fsmask4subject(sid), 'fsmask_1mm.nii')
    outfile = op.join(gconf.get_cmt_fsmask4subject(sid), 'fsmask_1mm__8bit.nii')
    
    fsl_cmd = 'fslmaths %s %s -odt char' % (infile, outfile) 
    runCmd( fsl_cmd, log )
    
    log.info("[ DONE ]")
    

def fiber_tracking_dsi():
    
    log.info("Run STREAMLINE tractography")
    log.info("===========================")
    
    # XXX: rm "fibers/streamline.trk" &> /dev/null
    
    if not op.exists(gconf.get_cmt_fibers4subject(sid)):
        fibers_path = os.makedirs(gconf.get_cmt_fibers4subject(sid))
    
    # XXX: be clear about it
    if len(gconf.mode_parameters['sharpness_odf']) == 1:
        # normal streamline
        
        dtb_cmd = ['DTB_streamline', \
                                 "--odf %s" % op.join(gconf.get_cmt_rawdiff4subject(sid), 'odf_0', 'dsi_'),
                                 "--angle 60",
                                 "--wm %s" % op.join(gconf.get_cmt_fsmask4subject(sid), 'fsmask_1mm__8bit.nii'),
                                 "--rSeed 4",
                                 "--out %s" % op.join(gconf.get_cmt_fibers4subject(sid), 'streamline')]
        dtb_cmd = ' '.join(dtb_cmd)
        
        runCmd( dtb_cmd, log )
        
    else:
        # streamline with 2 ODFs
        for ele in gconf.mode_parameters['sharpness_odf']:
            log.info("Compute streamline for element %s" % ele)
            
            dtb_cmd = ['DTB_streamline', \
                                     "--odf %s" % op.join(gconf.get_cmt_rawdiff4subject(sid), 'odf_%s' % str(ele), 'dsi_'),
                                     "--angle 45",
                                     "--odf2 %s" % op.join(gconf.get_cmt_rawdiff4subject(sid), 'odf_0', 'dsi_'),
                                     "--angle2 60",
                                     "--wm %s" % op.join(gconf.get_cmt_fsmask4subject(sid), 'fsmask_1mm__8bit.nii'),
                                     "--rSeed 4",
                                     "--out %s" % op.join(gconf.get_cmt_fibers4subject(sid), 'streamline')]
            dtb_cmd = ' '.join(dtb_cmd)
            runCmd( dtb_cmd, log )
                    
    if not op.exists(op.join(gconf.get_cmt_fibers4subject(sid), 'streamline.trk')):
        log.error('No streamline.trk created')    
    
    # XXX: rm "${DATA_path}/${MY_SUBJECT}/${MY_TP}/4__CMT/fs_output/registred/HR__registered-TO-b0/fsmask_1mm__8bit.nii"
    log.info("[ DONE ]")


def fiber_tracking_dti():
    pass

def spline_filtering():
    log.info("Spline filtering the fibers")
    log.info("===========================")

    sp_cmd = 'spline_filter %s 1 %s' % (op.join(gconf.get_cmt_fibers4subject(sid), 'streamline.trk'),
               op.join(gconf.get_cmt_fibers4subject(sid), 'streamline_spline.trk') )
    
    runCmd( sp_cmd, log )
    
#    os.rename(op.join(gconf.get_cmt_fibers4subject(sid), "tmp.trk"), op.join(gconf.get_cmt_fibers4subject(sid), "streamline.trk"))

    # XXX: add trackvis for inspection
    
    log.info("[ DONE ]")


def run(conf, subject_tuple):
    """ Run the tractography step
    
    Parameters
    ----------
    conf : PipelineConfiguration object
    subject_tuple : tuple, (subject_id, timepoint)
        Process the given subject
        
    """
    # setting the global configuration variable
    globals()['gconf'] = conf
    globals()['sid'] = subject_tuple
    globals()['log'] = gconf.get_logger4subject(sid) 
    start = time()
    
    convert_wm_mask()
    
    if gconf.processing_mode == 'DSI':
        fiber_tracking_dsi()
    elif gconf.processing_mode == 'DTI':
        fiber_tracking_dti()

    spline_filtering()
    
    log.info("Module took %s seconds to process." % (time()-start))