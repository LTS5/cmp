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
        param = '--angle 60 --rSeed 4'

    cmd = op.join(gconf.get_cmt_binary_path(), 'DTB_streamline')
    dtb_cmd = '%s --odf %s --wm %s --out %s %s' % (cmd, op.join(gconf.get_cmt_rawdiff(), 'odf_0', 'dsi_'),
                            # use the white matter mask after registration!
                            op.join(gconf.get_cmt_tracto_mask_tob0(), 'fsmask_1mm__8bit.nii'),
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

def declare_inputs(conf):
    """Declare the inputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)
    odf_out_path = op.join(conf.get_cmt_rawdiff(), 'odf_0')
    
    conf.pipeline_status.AddStageInput(stage, conf.get_cmt_tracto_mask_tob0(), 'fsmask_1mm.nii', 'fsmask_1mm-nii')


    if conf.diffusion_imaging_model == 'DSI' and \
        conf.diffusion_imaging_stream == 'Lausanne2011':
        conf.pipeline_status.AddStageInput(stage, odf_out_path, 'dsi_odf.nii', 'dsi_odf-nii')
    elif conf.diffusion_imaging_model == 'DTI' and \
        conf.diffusion_imaging_stream == 'Lausanne2011':
        pass        
        
    
def declare_outputs(conf):
    """Declare the outputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)
    fibers_path = conf.get_cmt_fibers()
        
    conf.pipeline_status.AddStageOutput(stage, conf.get_cmt_tracto_mask_tob0(), 'fsmask_1mm__8bit.nii', 'fsmask_1mm__8bit-nii')
    
    if conf.diffusion_imaging_model == 'DSI' and \
       conf.diffusion_imaging_stream == 'Lausanne2011':
        conf.pipeline_status.AddStageOutput(stage, fibers_path, 'streamline.trk', 'streamline-trk')
    elif conf.diffusion_imaging_model == 'DTI' and \
        conf.diffusion_imaging_stream == 'Lausanne2011':
        pass
              
          
