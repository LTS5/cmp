import os, os.path as op
import sys
from time import time
from ...logme import *
from glob import glob
import subprocess
from cmt.util import mymove

def resample_dsi():

    log.info("Resample the DSI dataset to 2x2x2 mm^3")
    log.info("======================================")

    input_dsi_file = op.join(gconf.get_nifti4subject(sid), 'DSI.nii')
    # XXX: this output file is never generated!
    ouput_dsi_file = op.join(gconf.get_cmt_rawdiff4subject(sid), 'DSI_resampled_2x2x2.nii.gz')
    res_dsi_dir = op.join(gconf.get_cmt_rawdiff4subject(sid), '2x2x2') 
    
    if not op.exists(input_dsi_file):
        log.error("File does not exists: %s" % input_dsi_file)
    else:
        log.debug("Found file: %s" % input_dsi_file)
            
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
    
    
def resample_dti():
    # XXX: necessary?

    log.info("Resample the DTI dataset to 2x2x2 mm^3")
    log.info("======================================")

    input_dsi_file = op.join(gconf.get_nifti4subject(sid), 'DTI.nii')
    # XXX: this output file is never generated!
    ouput_dsi_file = op.join(gconf.get_cmt_rawdiff4subject(sid), 'DTI_resampled_2x2x2.nii.gz')
    res_dsi_dir = op.join(gconf.get_cmt_rawdiff4subject(sid), '2x2x2') 
    
    if not op.exists(input_dsi_file):
        log.error("File does not exists: %s" % input_dsi_file)
    else:
        log.debug("Found file: %s" % input_dsi_file)
            
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
    log.info("==============================")
    
    # XXX: is first file correct like this?
    first_input_file = op.join(gconf.get_cmt_rawdiff4subject(sid), '2x2x2', 'MR0000.nii')
    dti_out_path = op.join(gconf.get_cmt_rawdiff4subject(sid), 'odf_0')
    
    if not op.exists(first_input_file):
        msg = "No input file available: %s" % first_input_file
        log.error(msg)
        raise Exception(msg)
    
    
    if gconf.mode_parameters.has_key('dti_recon_param'):
        param = gconf.mode_parameters['dti_recon_param']
    else:
        # store bvalues in 4th component of gradient_matrix
        # otherwise use --b_value 1000 for a global b value
        param = '--number_of_b0 1 --gradient_matrix %s 1'
        # others? -iop 1 0 0 0 1 0 -oc -p 3 -sn 0 -ot nii
         
    dti_cmd = 'dti_recon  %s %s %s' % (first_input_file,  
                             op.join(dti_out_path, "dti_"),
                             param % gconf.get_gradient_matrix(sid, False) )
    
    runCmd (dti_cmd, log )

    # XXX: what does it reconstruct (filename?)
    #if not op.exists(op.join(odf_out_path, "dsi_odf.nii")):
    #    log.error("Unable to reconstruct ODF!")
        
def compute_odfs():    

    log.info("Compute the ODFs field")
    log.info("=========================")
    
    first_input_file = op.join(gconf.get_cmt_rawdiff4subject(sid), '2x2x2', 'MR0000.nii')
    odf_out_path = op.join(gconf.get_cmt_rawdiff4subject(sid), 'odf_0')
    
    if not op.exists(first_input_file):
        msg = "No input file available: %s" % first_input_file
        log.error(msg)
        raise Exception(msg)
    
    # calculate ODF map
    
    # XXX: rm -f "odf_${sharpness}/dsi_"*
    if gconf.mode_parameters.has_key('odf_recon_param'):
        param = gconf.mode_parameters['odf_recon_param']
    else:
        param = '-b0 1 -dsi -p 4 -sn 0 -ot nii'

    odf_cmd = 'odf_recon %s %s %s %s -mat %s -s 0 %s' % (first_input_file, 
                             str(gconf.mode_parameters['nr_of_gradient_directions']),
                             str(gconf.mode_parameters['nr_of_sampling_directions']), 
                             op.join(odf_out_path, "dsi_"),
                             gconf.get_dtk_dsi_matrix(),
                             param )
    runCmd (odf_cmd, log )
    
    if not op.exists(op.join(odf_out_path, "dsi_odf.nii")):
        log.error("Unable to reconstruct ODF!")
        
    # calculate GFA map
    # XXX: rm -f "odf_${sharpness}/dsi_gfa.nii"

    # XXX: this will be replaced by Python code, to compute different scalar fields
    cmd = op.join(gconf.get_cmt_binary_path(), 'DTB_gfa')
    dta_cmd = '%s --dsi "%s"' % (cmd, op.join(odf_out_path, 'dsi_'))
    runCmd( dta_cmd, log )

    if not op.exists(op.join(odf_out_path, "dsi_gfa.nii")):
        log.error("Unable to calculate GFA map!")
    else:
        # copy dsi_gfa.nii to scalar folder for processing with connectionmatrix
        src = op.join(odf_out_path, "dsi_gfa.nii")
        dst = op.join(gconf.get_cmt_scalars4subject(sid), 'dsi_gfa.nii')
        mymove( src, dst, log )
    
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
        
    if gconf.processing_mode == ('DSI', 'Lausanne2011'):
        resample_dsi()
        compute_odfs()
    elif gconf.processing_mode == ('DTI', 'Lausanne2011'):
        resample_dti()
        compute_dts()
    
    log.info("Module took %s seconds to process." % (time()-start))

    if not len(gconf.emailnotify) == 0:
        msg = "Diffusion module finished!\nIt took %s seconds." % int(time()-start)
        send_email_notification(msg, gconf.emailnotify, log)
          