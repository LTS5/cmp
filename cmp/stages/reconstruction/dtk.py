# Copyright (C) 2009-2011, Ecole Polytechnique Federale de Lausanne (EPFL) and
# Hospital Center and University of Lausanne (UNIL-CHUV), Switzerland
# All rights reserved.
#
#  This software is distributed under the open-source license Modified BSD.

import os, os.path as op
import sys
from time import time
from ...logme import *
from glob import glob
import subprocess
from cmp.util import mymove
import gzip

def resample_dsi():

    log.info("Resample the DSI dataset to 2x2x2 mm^3")
    log.info("======================================")

    input_dsi_file = op.join(gconf.get_nifti(), 'DSI.nii.gz')
    # XXX: this output file is never generated!
    output_dsi_file = op.join(gconf.get_cmp_rawdiff(), 'DSI_resampled_2x2x2.nii.gz')
    res_dsi_dir = gconf.get_cmp_rawdiff_resampled()
    
    if not op.exists(input_dsi_file):
        log.error("File does not exists: %s" % input_dsi_file)
    else:
        log.debug("Found file: %s" % input_dsi_file)
            
    split_cmd = 'fslsplit %s %s -t' % (input_dsi_file, op.join(res_dsi_dir, 'MR'))
    runCmd( split_cmd, log )
    
    files = glob( op.join(res_dsi_dir, 'MR*.nii.gz'))
    for file in sorted(files):        
        tmp_file = op.join(res_dsi_dir, 'tmp.nii.gz')
        mri_cmd = 'mri_convert -vs 2 2 2 %s %s ' % (file, tmp_file)
        runCmd( mri_cmd, log )
        fsl_cmd = 'fslmaths %s %s -odt short' % (tmp_file, file)
        runCmd( fsl_cmd, log )        

    fslmerge_cmd = 'fslmerge -a %s %s' % (output_dsi_file,  op.join(res_dsi_dir, 'MR0000.nii.gz'))
    runCmd( fslmerge_cmd, log )

    log.info(" [DONE] ")

def resample_qball():

    log.info("Resample the QBALL dataset to 2x2x2 mm^3")
    log.info("======================================")

    input_dsi_file = op.join(gconf.get_nifti(), 'QBALL.nii.gz')
    # XXX: this output file is never generated!
    output_dsi_file = op.join(gconf.get_cmp_rawdiff(), 'QBALL_resampled_2x2x2.nii.gz')
    res_dsi_dir = gconf.get_cmp_rawdiff_resampled()

    if not op.exists(input_dsi_file):
        log.error("File does not exists: %s" % input_dsi_file)
    else:
        log.debug("Found file: %s" % input_dsi_file)

    split_cmd = 'fslsplit %s %s -t' % (input_dsi_file, op.join(res_dsi_dir, 'MR'))
    runCmd( split_cmd, log )

    files = glob( op.join(res_dsi_dir, 'MR*.nii.gz'))
    for file in sorted(files):
        tmp_file = op.join(res_dsi_dir, 'tmp.nii.gz')
        mri_cmd = 'mri_convert -vs 2 2 2 %s %s ' % (file, tmp_file)
        runCmd( mri_cmd, log )
        fsl_cmd = 'fslmaths %s %s -odt short' % (tmp_file, file)
        runCmd( fsl_cmd, log )

    fslmerge_cmd = 'fslmerge -a %s %s' % (output_dsi_file,  op.join(res_dsi_dir, 'MR0000.nii.gz'))
    runCmd( fslmerge_cmd, log )

    log.info(" [DONE] ")
    
def resample_dti():

    log.info("Resample the DTI dataset to 2x2x2 mm^3")
    log.info("======================================")

    input_dsi_file = op.join(gconf.get_nifti(), 'DTI.nii.gz')
    # XXX: this output file is never generated!
    output_dsi_file = op.join(gconf.get_cmp_rawdiff(), 'DTI_resampled_2x2x2.nii.gz')
    res_dsi_dir = gconf.get_cmp_rawdiff_resampled()
    
    if not op.exists(input_dsi_file):
        log.error("File does not exists: %s" % input_dsi_file)
    else:
        log.debug("Found file: %s" % input_dsi_file)
            
    split_cmd = 'fslsplit %s %s -t' % (input_dsi_file, op.join(res_dsi_dir, 'MR'))
    runCmd( split_cmd, log )
    
    files = glob( op.join(res_dsi_dir, 'MR*.nii.gz'))
    for file in sorted(files):        
        tmp_file = op.join(res_dsi_dir, 'tmp.nii.gz')
        mri_cmd = 'mri_convert -vs 2 2 2 %s %s ' % (file, tmp_file)
        runCmd( mri_cmd, log )
        fsl_cmd = 'fslmaths %s %s -odt short' % (tmp_file, file)
        runCmd( fsl_cmd, log )        
    
    fslmerge_cmd = 'fslmerge -a %s %s' % (output_dsi_file,  op.join(res_dsi_dir, 'MR*.nii.gz'))
    runCmd( fslmerge_cmd, log )

    log.info(" [DONE] ")
    
    
def compute_dts():
    
    log.info("Compute diffusion tensor field")
    log.info("==============================")
    
    input_file = op.join(gconf.get_cmp_rawdiff(), 'DTI_resampled_2x2x2.nii.gz')
    dti_out_path = gconf.get_cmp_rawdiff_reconout()
    
    if not op.exists(input_file):
        msg = "No input file available: %s" % input_file
        log.error(msg)
        raise Exception(msg)
    
    if not gconf.dti_recon_param == '':
        param = gconf.dti_recon_param + ' -gm %s' % gconf.gradient_table_file
    else:
        param = ' -gm %s' % gconf.gradient_table_file
        # store bvalues in 4th component of gradient_matrix
        # otherwise use --b_value 1000 for a global b value
        # param = '--number_of_b0 1 --gradient_matrix %s 1'
        # others? -iop 1 0 0 0 1 0 -oc -p 3 -sn 0 -ot nii.gz
         
    dti_cmd = 'dti_recon %s %s -b0 %s -b %s %s -ot nii' % (input_file,  
                             op.join(dti_out_path, "dti_"),
			     gconf.nr_of_b0,
			     gconf.max_b0_val,
                             param)
    
    runCmd (dti_cmd, log )

    # convert scalar maps

    if not op.exists(op.join(dti_out_path, "dti_fa.nii")):
        log.error("Unable to calculate FA map!")
    else:
        src = op.join(dti_out_path, "dti_fa.nii")
        dst = op.join(gconf.get_cmp_scalars(), 'dti_fa.nii.gz')

        log.info("Gzip compress...")
        f_in = open(src, 'rb')
        f_out = gzip.open(dst, 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()

    if not op.exists(op.join(dti_out_path, "dti_adc.nii")):
        log.error("Unable to calculate ADC map!")
    else:
        src = op.join(dti_out_path, "dti_adc.nii")
        dst = op.join(gconf.get_cmp_scalars(), 'dti_adc.nii.gz')

        log.info("Gzip compress...")
        f_in = open(src, 'rb')
        f_out = gzip.open(dst, 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()

    # XXX: what does it reconstruct (filename?)
    #if not op.exists(op.join(odf_out_path, "dsi_odf.nii.gz")):
    #    log.error("Unable to reconstruct ODF!")


def compute_hardi_odf():    

    log.info("Compute the ODFs field (HARDI/QBALL)")
    log.info("====================================")

    first_input_file = op.join(gconf.get_cmp_rawdiff(), '2x2x2', 'MR0000.nii.gz')
    odf_out_path = gconf.get_cmp_rawdiff_reconout()

    output_dsi_file = op.join(gconf.get_cmp_rawdiff(), 'QBALL_resampled_2x2x2.nii.gz')

    # hardi matrix creation
    if not gconf.odf_recon_param == '':
        param = gconf.dti_recon_param + ' -gm %s' % gconf.gradient_table_file
    else:
        param = ' -gm %s' % gconf.gradient_table_file
        
    hardi_cmd = 'hardi_mat "%s" "%s" -ref "%s" -oc' % (gconf.gradient_table_file, op.join(gconf.get_nifti(), 'temp_mat.dat'), output_dsi_file )

    runCmd( hardi_cmd, log )

    if not op.exists(first_input_file):
        msg = "No input file available: %s" % first_input_file
        log.error(msg)
        raise Exception(msg)

    # calculate ODF map
    if not gconf.hardi_recon_param == '':
        param = gconf.hardi_recon_param
    else:
        param = '-b0 1 -p 3 -sn 1'

    odf_cmd = 'odf_recon "%s" %s %s "%s" -mat "%s" -s 0 %s -ot nii' % (first_input_file,
                             str(gconf.nr_of_gradient_directions),
                             str(gconf.nr_of_sampling_directions),
                             op.join(odf_out_path, "hardi_"),
                             op.join(gconf.get_nifti(), 'temp_mat.dat'),
                             param )
    runCmd (odf_cmd, log )

    #compute_scalars(gconf.get_cmp_rawdiff_reconout(), 'hardi')

def compute_odfs():    

    log.info("Compute the ODFs field")
    log.info("=========================")
    
    first_input_file = op.join(gconf.get_cmp_rawdiff(), '2x2x2', 'MR0000.nii.gz')
    odf_out_path = gconf.get_cmp_rawdiff_reconout()
    
    if not op.exists(first_input_file):
        msg = "No input file available: %s" % first_input_file
        log.error(msg)
        raise Exception(msg)
    
    # calculate ODF map
    
    # XXX: rm -f "odf_${sharpness}/dsi_"*
    if not gconf.odf_recon_param == '':
        param = gconf.odf_recon_param
    else:
        param = '-b0 1 -dsi -p 4 -sn 0'

    odf_cmd = 'odf_recon %s %s %s %s -mat %s -s 0 %s -ot nii' % (first_input_file, 
                             str(gconf.nr_of_gradient_directions),
                             str(gconf.nr_of_sampling_directions), 
                             op.join(odf_out_path, "dsi_"),
                             gconf.get_dtk_dsi_matrix(),
                             param )
    runCmd (odf_cmd, log )

    compute_scalars(odf_out_path, 'dsi')

    # calculate P0 map only for DSI
    prefix = 'dsi'
    cmd = op.join(gconf.get_cmp_binary_path(), 'DTB_P0')
    dta_cmd = '%s --dsi "%s" --dwi "%s"' % (cmd, op.join(odf_out_path, prefix+'_'), op.join(gconf.get_nifti(), 'DSI.nii.gz'))
    runCmd( dta_cmd, log )

    if not op.exists(op.join(odf_out_path, prefix+"_P0.nii")):
        log.error("Unable to calculate P0 map!")
    else:
        # copy dsi_kurtosis.nii.gz to scalar folder for processing with connectionmatrix
        src = op.join(odf_out_path, prefix+"_P0.nii")
        dst = op.join(gconf.get_cmp_scalars(), prefix+'_P0.nii.gz')

        log.info("Gzip compress...")
        f_in = open(src, 'rb')
        f_out = gzip.open(dst, 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()

def compute_scalars(odf_out_path, prefix):

    if not op.exists(op.join(odf_out_path, prefix+"_odf.nii")):
        log.error("Unable to reconstruct ODF!")

    # calculate GFA map
    cmd = op.join(gconf.get_cmp_binary_path(), 'DTB_gfa')
    dta_cmd = '%s --dsi "%s" --m 2' % (cmd, op.join(odf_out_path, prefix+'_'))
    runCmd( dta_cmd, log )

    if not op.exists(op.join(odf_out_path, prefix+"_gfa.nii")):
        log.error("Unable to calculate GFA map!")
    else:
        # copy dsi_gfa.nii.gz to scalar folder for processing with connectionmatrix
        src = op.join(odf_out_path, prefix+'_gfa.nii')
        dst = op.join(gconf.get_cmp_scalars(), prefix+'_gfa.nii.gz')

        log.info("Gzip compress...")
        f_in = open(src, 'rb')
        f_out = gzip.open(dst, 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()

        # mymove( src, dst, log )

    # calculate skewness map
    cmd = op.join(gconf.get_cmp_binary_path(), 'DTB_gfa')
    dta_cmd = '%s --dsi "%s" --m 3' % (cmd, op.join(odf_out_path, prefix+'_'))
    runCmd( dta_cmd, log )

    if not op.exists(op.join(odf_out_path, prefix+"_skewness.nii")):
        log.error("Unable to calculate skewness map!")
    else:
        # copy dsi_gfa.nii.gz to scalar folder for processing with connectionmatrix
        src = op.join(odf_out_path, prefix+"_skewness.nii")
        dst = op.join(gconf.get_cmp_scalars(), prefix+'_skewness.nii.gz')

        log.info("Gzip compress...")
        f_in = open(src, 'rb')
        f_out = gzip.open(dst, 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()


    # calculate dsi_kurtosis map
    cmd = op.join(gconf.get_cmp_binary_path(), 'DTB_gfa')
    dta_cmd = '%s --dsi "%s" --m 4' % (cmd, op.join(odf_out_path, prefix+'_'))
    runCmd( dta_cmd, log )

    if not op.exists(op.join(odf_out_path, prefix+"_kurtosis.nii")):
        log.error("Unable to calculate kurtosis map!")
    else:
        # copy dsi_kurtosis.nii.gz to scalar folder for processing with connectionmatrix
        src = op.join(odf_out_path, prefix+"_kurtosis.nii")
        dst = op.join(gconf.get_cmp_scalars(), prefix+'_kurtosis.nii.gz')

        log.info("Gzip compress...")
        f_in = open(src, 'rb')
        f_out = gzip.open(dst, 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()

        # mymove( src, dst, log )


    log.info("[ DONE ]")

def convert_to_dir_dsi():

    log.info("Convert to new file format")
    log.info("==========================")

    odf_out_path = gconf.get_cmp_rawdiff_reconout()

    cmd = op.join(gconf.get_cmp_binary_path(), 'DTB_dtk2dir --dirlist "%s" --prefix "%s" --type "dsi" --vf 0 %s' %
                  (gconf.get_dtb_streamline_vecs_file(), op.join(odf_out_path, 'dsi_'), gconf.dtb_dtk2dir_param) )
    
    runCmd (cmd, log )

    if not op.exists(op.join(odf_out_path, "dsi_dir.nii")):
        log.error("Unable to create dsi_dir.nii")
    
    log.info("[ DONE ]")
    
def convert_to_dir_dti():

    log.info("Convert to new file format")
    log.info("==========================")

    dti_out_path = gconf.get_cmp_rawdiff_reconout()

    cmd = op.join(gconf.get_cmp_binary_path(), 'DTB_dtk2dir --prefix "%s" --type "dti" %s' %
                   ( op.join(dti_out_path, 'dti_'), gconf.dtb_dtk2dir_param ) )
    
    runCmd (cmd, log )

    if not op.exists(op.join(dti_out_path, "dti_dir.nii")):
        log.error("Unable to create dti_dir.nii")
    
    log.info("[ DONE ]")

def convert_to_dir_qball():

    log.info("Convert to new file format")
    log.info("==========================")

    dti_out_path = gconf.get_cmp_rawdiff_reconout()

    cmd = op.join(gconf.get_cmp_binary_path(), 'DTB_dtk2dir --prefix "%s" --type "dsi" --dirlist "%s" %s' %
                  ( op.join(dti_out_path, 'hardi_'), gconf.get_dtb_streamline_vecs_file(), gconf.dtb_dtk2dir_param ) )

    runCmd (cmd, log )

    if not op.exists(op.join(dti_out_path, "hardi_dir.nii")):
        log.error("Unable to create hardi_dir.nii")

    log.info("[ DONE ]")
    
    
def run(conf):
    """ Run the diffusion step
    
    Parameters
    ----------
    conf : PipelineConfiguration object
        
    """
    
    # setting the global configuration variable
    globals()['gconf'] = conf
    globals()['log'] = gconf.get_logger() 
    start = time()
        
    if gconf.diffusion_imaging_model == 'DSI':
        resample_dsi()
        compute_odfs()
        convert_to_dir_dsi()
    elif gconf.diffusion_imaging_model == 'DTI':
        resample_dti()
        compute_dts()
        convert_to_dir_dti()
    elif gconf.diffusion_imaging_model == 'QBALL':
        resample_qball()
        compute_hardi_odf()
        convert_to_dir_qball()

    log.info("Module took %s seconds to process." % (time()-start))

    if not len(gconf.emailnotify) == 0:
        msg = ["Diffusion module", int(time()-start)]
        send_email_notification(msg, gconf, log)
          
def declare_inputs(conf):
    """Declare the inputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)
    nifti_dir = conf.get_nifti()
    
    if conf.diffusion_imaging_model == 'DSI':
        conf.pipeline_status.AddStageInput(stage, nifti_dir, 'DSI.nii.gz', 'dsi-nii-gz')
        
    elif conf.diffusion_imaging_model == 'DTI':
        conf.pipeline_status.AddStageInput(stage, nifti_dir, 'DTI.nii.gz', 'dti-nii-gz')

    elif conf.diffusion_imaging_model == 'QBALL':
        conf.pipeline_status.AddStageInput(stage, nifti_dir, 'QBALL.nii.gz', 'qball-nii-gz')

    
def declare_outputs(conf):
    """Declare the outputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)
    rawdiff_dir = conf.get_cmp_rawdiff()
    diffusion_out_path = conf.get_cmp_rawdiff_reconout()
    
    cmp_scalars_path = conf.get_cmp_scalars()
    
    if conf.diffusion_imaging_model == 'DSI':
        conf.pipeline_status.AddStageOutput(stage, rawdiff_dir, 'DSI_resampled_2x2x2.nii.gz', 'DSI_resampled_2x2x2-nii-gz')
        conf.pipeline_status.AddStageOutput(stage, diffusion_out_path, 'dsi_odf.nii', 'dsi_odf-nii')
        conf.pipeline_status.AddStageOutput(stage, diffusion_out_path, 'dsi_dir.nii', 'dsi_dir-nii')
          
    elif conf.diffusion_imaging_model == 'DTI':
        conf.pipeline_status.AddStageOutput(stage, rawdiff_dir, 'DTI_resampled_2x2x2.nii.gz', 'DTI_resampled_2x2x2-nii-gz')
        conf.pipeline_status.AddStageOutput(stage, diffusion_out_path, 'dti_tensor.nii', 'dti_tensor-nii')
        conf.pipeline_status.AddStageOutput(stage, diffusion_out_path, 'dti_dir.nii', 'dti_dir-nii')
          
    elif conf.diffusion_imaging_model == 'QBALL':
        conf.pipeline_status.AddStageOutput(stage, rawdiff_dir, 'QBALL_resampled_2x2x2.nii.gz', 'QBALL_resampled_2x2x2-nii-gz')
        conf.pipeline_status.AddStageOutput(stage, diffusion_out_path, 'hardi_odf.nii', 'hardi_odf-nii')
        conf.pipeline_status.AddStageOutput(stage, diffusion_out_path, 'hardi_dir.nii', 'hardi_dir-nii')
