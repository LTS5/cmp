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

    if not gconf.streamline_param == '':
        param = gconf.streamline_param
    else:
        param = '--angle 40 --rSeed 4'

    cmd = op.join(gconf.get_cmt_binary_path(), 'DTB_streamline')
    dtb_cmd = '%s --odf %s --wm %s --odfdir %s --out %s %s' % (cmd, op.join(gconf.get_cmt_rawdiff(), 'odf_0', 'dsi_'),
                            # use the white matter mask after registration!
                            op.join(gconf.get_cmt_tracto_mask_tob0(), 'fsmask_1mm__8bit.nii'),
                            gconf.get_dtb_streamline_vecs_file(),
                            op.join(fibers_path, 'streamline'), param )
    
    runCmd( dtb_cmd, log )
        
    if not op.exists(op.join(fibers_path, 'streamline.trk')):
        log.error('No streamline.trk created')    
    
    # XXX: rm "${DATA_path}/${MY_SUBJECT}/${MY_TP}/4__CMT/fs_output/registered/HR__registered-TO-b0/fsmask_1mm__8bit.nii"
    log.info("[ DONE ]")


def fiber_tracking_dti():
    pass


def run(conf):
    """ Run the tractography step
    
    Parameters
    ----------
    conf : PipelineConfiguration object
        
    """
    # setting the global configuration variable
    globals()['gconf'] = conf
    globals()['log'] = gconf.get_logger() 
    start = time()
    
    from os import environ
    env = environ
    # alessandro needs to update the Cpp file
    env['CMT_HOME'] = gconf.get_cmt_binary_path()

    convert_wm_mask()
    
    if gconf.diffusion_imaging_model == 'DSI' and \
        gconf.diffusion_imaging_stream == 'Lausanne2011':
        fiber_tracking_dsi()
    elif gconf.diffusion_imaging_model == 'DTI' and \
        gconf.diffusion_imaging_stream == 'Lausanne2011':
        fiber_tracking_dti()
    
    log.info("Module took %s seconds to process." % (time()-start))
    
    msg = "Tractography module finished!\nIt took %s seconds." % int(time()-start)
    send_email_notification(msg, gconf.emailnotify, log)  

