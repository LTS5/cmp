import gzip
import os, os.path as op
from time import time
from ...logme import *
from glob import glob

def convert_wm_mask():
    
    log.info("Convert WM MASK to 8 bit/pixel")
    log.info("==============================")
    
    infile = op.join(gconf.get_cmp_tracto_mask_tob0(), 'fsmask_1mm.nii.gz')
    outfile = op.join(gconf.get_cmp_tracto_mask_tob0(), 'fsmask_1mm__8bit.nii.gz')
    resampout = op.join(gconf.get_cmp_tracto_mask_tob0(), 'fsmask_1mm_resamp2x2x2.nii.gz')
    
    fsl_cmd = 'fslmaths %s %s -odt char' % (infile, outfile) 
    runCmd( fsl_cmd, log )
    
    # XXX: resample the white matter mask to b0 native space
    # make it usable dti_tracker
    mri_cmd = 'mri_convert -vs 2 2 2 %s %s ' % (infile, resampout)
    runCmd( mri_cmd, log )
        
    log.info("[ DONE ]")
    

def decompress(f):
    log.info("Decompress %s" % f)
    fin=gzip.open(f, 'rb')
    fc = fin.read()
    fout=open(f.rstrip('.gz'), 'wb')
    fout.write(fc)
    fout.close()
    fin.close()

def decompress_odf_nifti():
    log.info("Decompress Nifti files")
    log.info("======================")
    
    # need not decompress dtk output for now, store it
    # output as .nii
#    odf_out_path = gconf.get_cmp_rawdiff_reconout()
#    fi = glob(op.join(odf_out_path, '*.nii.gz'))
#    for f in fi:
#        decompress(f)
#        # remove .nii.gz
#        os.remove(f)

    # do not remove mask nii.gz
    mask = op.join(gconf.get_cmp_tracto_mask_tob0(), 'fsmask_1mm__8bit.nii.gz')
    decompress(mask)

    
def fiber_tracking_dsi():
    
    log.info("Run STREAMLINE tractography")
    log.info("===========================")
    
    fibers_path = gconf.get_cmp_fibers()
    odf_out_path = gconf.get_cmp_rawdiff_reconout()
    
    # streamline tractography
    if not gconf.streamline_param == '':
        param = gconf.streamline_param
    else:
        param = '--angle 40 --rSeed 4'

    cmd = op.join(gconf.get_cmp_binary_path(), 'DTB_streamline')
    dtb_cmd = '%s --odf %s --wm %s --odfdir %s --out %s %s' % (cmd, op.join(odf_out_path, 'dsi_'),
                            # use the white matter mask after registration!
                            op.join(gconf.get_cmp_tracto_mask_tob0(), 'fsmask_1mm__8bit.nii'),
                            gconf.get_dtb_streamline_vecs_file(),
                            op.join(fibers_path, 'streamline'), param )
    
    runCmd( dtb_cmd, log )
        
    if not op.exists(op.join(fibers_path, 'streamline.trk')):
        log.error('No streamline.trk created')    
    
    log.info("[ DONE ]")


def fiber_tracking_dti():

    log.info("Run STREAMLINE tractography")
    log.info("===========================")
    
    fibers_path = gconf.get_cmp_fibers()
    ten_out_path = gconf.get_cmp_rawdiff_reconout()
    
    # streamline tractography
    if not gconf.streamline_param_dti == '':
        param = gconf.streamline_param_dti
    else:
        param = ''

    dtk_cmd = 'dti_tracker %s %s -m %s %s' % (op.join(ten_out_path, 'dti_'),
                            # use the white matter mask after registration!
                            op.join(fibers_path, 'streamline.trk'), 
                            op.join(gconf.get_cmp_tracto_mask_tob0(), 'fsmask_1mm_resamp2x2x2.nii.gz'),
                            param )
    
    runCmd( dtk_cmd, log )
        
    if not op.exists(op.join(fibers_path, 'streamline.trk')):
        log.error('No streamline.trk created')    
    
    log.info("[ DONE ]")
    
def inspect(gconf, filtered = False):
    """ Inspect the results of this stage """
    if filtered:
        log = gconf.get_logger()
        trkcmd = 'trackvis %s' % op.join(gconf.get_cmp_fibers(), 'streamline_filtered.trk')
        runCmd( trkcmd, log )
    else:
        log = gconf.get_logger()
        trkcmd = 'trackvis %s' % op.join(gconf.get_cmp_fibers(), 'streamline.trk')
        runCmd( trkcmd, log )

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
    
    convert_wm_mask()
    
    if gconf.diffusion_imaging_model == 'DSI' and \
        gconf.diffusion_imaging_stream == 'Lausanne2011':
        decompress_odf_nifti()
        fiber_tracking_dsi()
    elif gconf.diffusion_imaging_model == 'DTI' and \
        gconf.diffusion_imaging_stream == 'Lausanne2011':
        fiber_tracking_dti()
    
    log.info("Module took %s seconds to process." % (time()-start))

    if not len(gconf.emailnotify) == 0:
        msg = "Tractography module finished!\nIt took %s seconds." % int(time()-start)
        send_email_notification(msg, gconf, log)  

def declare_inputs(conf):
    """Declare the inputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)
    diffusion_out_path = conf.get_cmp_rawdiff_reconout()
    
    conf.pipeline_status.AddStageInput(stage, conf.get_cmp_tracto_mask_tob0(), 'fsmask_1mm.nii.gz', 'fsmask_1mm-nii-gz')

    if conf.diffusion_imaging_model == 'DSI' and \
        conf.diffusion_imaging_stream == 'Lausanne2011':
        conf.pipeline_status.AddStageInput(stage, diffusion_out_path, 'dsi_odf.nii', 'dsi_odf-nii')
    elif conf.diffusion_imaging_model == 'DTI' and \
        conf.diffusion_imaging_stream == 'Lausanne2011':
        conf.pipeline_status.AddStageInput(stage, diffusion_out_path, 'dti_tensor.nii', 'dti_tensor-nii')      
        
    
def declare_outputs(conf):
    """Declare the outputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)
    fibers_path = conf.get_cmp_fibers()
        
    conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_tracto_mask_tob0(), 'fsmask_1mm__8bit.nii.gz', 'fsmask_1mm__8bit-nii-gz')
    
    if conf.diffusion_imaging_model == 'DSI' and \
       conf.diffusion_imaging_stream == 'Lausanne2011':
        conf.pipeline_status.AddStageOutput(stage, fibers_path, 'streamline.trk', 'streamline-trk')
    elif conf.diffusion_imaging_model == 'DTI' and \
        conf.diffusion_imaging_stream == 'Lausanne2011':
        conf.pipeline_status.AddStageOutput(stage, fibers_path, 'streamline.trk', 'streamline-trk')
              
          
