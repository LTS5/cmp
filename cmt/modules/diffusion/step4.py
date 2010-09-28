import os, os.path as op
import sys
from time import time
from ...logme import *
from glob import glob
import subprocess

def resample_dsi():

    log.info("Resample the DSI dataset to 2x2x2 mm^3")
    log.info("======================================")

    input_dsi_file = op.join(gconf.get_nifti4subject(sid), 'DSI.nii')
    ouput_dsi_file = op.join(gconf.get_cmt_rawdiff4subject(sid), 'DSI_resampled_2x2x2.nii.gz')
    
    res_dsi_dir = op.join(gconf.get_cmt_rawdiff4subject(sid), '2x2x2') 
    
    if not op.exists(input_dsi_file):
        log.error("File does not exists: %s" % input_dsi_file)
    else:
        log.debug("Found file: %s" % input_dsi_file)

    if not op.exists(res_dsi_dir):
        try:
            os.makedirs(res_dsi_dir)
        finally:
            log.info("Created directory %s" % res_dsi_dir)
            
    split_cmd = 'fslsplit %s %s -t' % (input_dsi_file, op.join(res_dsi_dir, 'MR'))

    runCmd( split_cmd, log )
    
    files = glob( op.join(res_dsi_dir, 'MR*.nii'))
    for file in sorted(files):
        
        tmp_file = op.join(res_dsi_dir, 'tmp.nii')
        mri_cmd = 'mri_convert -vs 2 2 2 %s %s ' % (file, tmp_file)
        runCmd( mri_cmd, log )
        fsl_cmd = 'fslmaths %s %s -odt short' % (tmp_file, file)
        runCmd( fsl_cmd, log )        

    log.info(" [DONE] ")
    
def compute_dts():
    
    log.info("Compute diffusion tensor field")
    

def compute_odfs():    

    log.info("Compute the ODFs field(s)")
    log.info("=========================")
    
    first_input_file = op.join(gconf.get_cmt_rawdiff4subject(sid), '2x2x2', 'MR0000.nii')
    
    if not op.exists(first_input_file):
        msg = "No input file available: %s" % first_input_file
        log.error(msg)
        raise Exception(msg)
    
    # XXX: what about this parameter?
    for sharp in gconf.mode_parameters['sharpness_odf']:
        
        odf_out_path = op.join(gconf.get_cmt_rawdiff4subject(sid), 'odf_%s' % str(sharp))
        try:
            os.makedirs(odf_out_path)
        except os.error:
            log.info("%s was already existing" % str(odf_out_path))
    
        # calculate ODF map
        
        # XXX: rm -f "odf_${sharpness}/dsi_"*

        if not gconf.mode_parameters.has_key('odf_recon_para'):
            param = '-b0 1 -dsi -p 4 -sn 0 -ot nii'
        else:
            param = gconf.mode_parameters['odf_recon_para']

        odf_cmd = 'odf_recon %s %s %s %s -mat %s -s %s %s' % (first_input_file, 
                                 str(gconf.mode_parameters['nr_of_gradient_directions']),
                                 str(gconf.mode_parameters['nr_of_sampling_directions']), 
                                 op.join(odf_out_path, "dsi_"),
                                 gconf.get_dsi_matrix(),
                                 str(sharp),
                                 param )
        runCmd (odf_cmd, log )
        
        if not op.exists(op.join(odf_out_path, "dsi_odf.nii")):
            log.error("Unable to reconstruct ODF!")
            
        # calculate GFA map
        # XXX: rm -f "odf_${sharpness}/dsi_gfa.nii"

        dta_cmd = 'DTB_gfa --dsi "%s"' % op.join(odf_out_path, 'dsi_')
        runCmd( dta_cmd, log )

        if not op.exists(op.join(odf_out_path, "dsi_gfa.nii")):
            log.error("Unable to calculate GFA map!")
    
    log.info("[ DONE ]")

def run(conf, subject_tuple):
    """ Run the diffusion step
    
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
        
    if gconf.processing_mode == 'DSI':
        resample_dsi()
        compute_odfs()
    elif gconf.processing_mode == 'DTI':
        compute_dts()
    
    log.info("Module took %s seconds to process." % (time()-start))
