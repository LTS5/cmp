import os, os.path as op
from time import time
from ...logme import *

def convert_wm_mask():
    
    log.info("Convert WM MASK to 8 bit/pixel")
    log.info("==============================")
    
    infile = op.join(gconf.get_cmt_tracto_mask_tob0(), 'fsmask_1mm.nii')
    outfile = op.join(gconf.get_cmt_tracto_mask_tob0(), 'fsmask_1mm__8bit.nii')
    
    fsl_cmd = 'fslmaths %s %s -odt char' % (infile, outfile) 
    runCmd( fsl_cmd, log )
    
    log.info("[ DONE ]")
    

def fiber_tracking_dsi():
    
    log.info("Run STREAMLINE tractography")
    log.info("===========================")
    
    # XXX: rm "fibers/streamline.trk" &> /dev/null
    fibers_path = gconf.get_cmt_fibers()
                
    # streamline tractography

    if gconf.mode_parameters.has_key('streamline_param'):
        param = gconf.mode_parameters['streamline_param']
    else:
        param = '--angle 60 --rSeed 4'

    cmd = op.join(gconf.get_cmt_binary_path(), 'DTB_streamline')
    dtb_cmd = '%s --odf %s --wm %s --out %s %s' % (cmd, op.join(gconf.get_cmt_rawdiff(), 'odf_0', 'dsi_'),
                            # use the white matter mask after registration!
                            op.join(gconf.get_cmt_tracto_mask_tob0(), 'fsmask_1mm__8bit.nii'),
                            op.join(fibers_path, 'streamline'), param )
    
    runCmd( dtb_cmd, log )
        
    if not op.exists(op.join(fibers_path, 'streamline.trk')):
        log.error('No streamline.trk created')    
    
    # XXX: rm "${DATA_path}/${MY_SUBJECT}/${MY_TP}/4__CMT/fs_output/registred/HR__registered-TO-b0/fsmask_1mm__8bit.nii"
    log.info("[ DONE ]")


def fiber_tracking_dti():
    pass


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
    
    from os import environ
    env = environ
    # alessandro needs to update the Cpp file
    env['CMT_HOME'] = gconf.get_cmt_binary_path()

    convert_wm_mask()
    
    if gconf.processing_mode == ('DSI', 'Lausanne2011'):
        fiber_tracking_dsi()
    elif gconf.processing_mode == ('DTI', 'Lausanne2011'):
        fiber_tracking_dti()
    
    log.info("Module took %s seconds to process." % (time()-start))
    
    msg = "Tractography module finished!\nIt took %s seconds." % int(time()-start)
    send_email_notification(msg, gconf.emailnotify, log)  

