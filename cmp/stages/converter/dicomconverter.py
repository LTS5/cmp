import os, os.path as op
from glob import glob
import subprocess
import sys
from time import time
import shutil
from ...logme import *
from cmp.util import reorient

import nibabel.nicom.dicomreaders as dr
import nibabel as ni

def diff2nifti_dsi_unpack():

    raw_dir = op.join(gconf.get_rawdata())    
    nifti_dir = op.join(gconf.get_nifti())
    dsi_dir = op.join(raw_dir, 'DSI')
    raw_glob = gconf.get_rawglob('diffusion')
    diffme = gconf.get_diffusion_metadata()

    log.info("Convert DSI ...")
    # check if .nii / .nii.gz is already available
    if op.exists(op.join(dsi_dir, 'DSI.nii')):
        shutil.copy(op.join(dsi_dir, 'DSI.nii'), op.join(nifti_dir, 'DSI.nii'))
    else:
        # read data
        files = glob(op.join(dsi_dir, raw_glob))
        if len(files) == 0:
            raise Exception('No files found for %s. Maybe change raw_glob variable for subject? (case-sensitive!)' % op.join(dsi_dir, raw_glob) )
		
        first = sorted(files)[0]
        diff_cmd = 'diff_unpack %s %s' % (first,
                                 op.join(nifti_dir, 'DSI.nii'))            
        runCmd(diff_cmd, log)
        
        # extract bvals, bvects, affine from dsi and store them as .txt in NIFTI
        data, affine, bval, bvect = dr.read_mosaic_dir(dsi_dir, raw_glob)
        del data
        import numpy as np
        np.savetxt(op.join(diffme, 'dsi_affine.txt'), affine, delimiter=',')
        np.savetxt(op.join(diffme, 'dsi_bvals.txt'), bval, delimiter=',')
        np.savetxt(op.join(diffme, 'dsi_bvects.txt'), bvect, delimiter=',')

        arr = np.zeros( (bvect.shape[0],bvect.shape[1]+1) )
        arr[:,:3] = bvect
        arr[:,3] = bval
        np.savetxt(op.join(diffme, 'gradient_table.txt'), arr, delimiter=',')
        

def dsi_resamp():
    
    nifti_dir = op.join(gconf.get_nifti())
    
    log.info("Resampling 'DSI' to 1x1x1 mm^3...")
    
    # extract only first image with nibabel
    img = ni.load(op.join(nifti_dir, 'DSI.nii'))
    data = img.get_data()
    hdr = img.get_header()
    aff = img.get_affine()
    
    # update header
    hdr['dim'][4] = 1
    # first slice
    data = data[:,:,:,0]
    
    ni.save(ni.Nifti1Image(data, aff, hdr), op.join(nifti_dir, 'DSI_first.nii'))
    
    mri_cmd = 'mri_convert -vs 1 1 1 %s %s' % (
                           op.join(nifti_dir, 'DSI_first.nii'),
                           op.join(nifti_dir, 'Diffusion_b0_resampled.nii'))
    
    runCmd(mri_cmd, log)

def diff2nifti_dti_unpack():

    raw_dir = op.join(gconf.get_rawdata())    
    nifti_dir = op.join(gconf.get_nifti())
    diffme = gconf.get_diffusion_metadata()
    dti_dir = op.join(raw_dir, 'DTI')
    raw_glob = gconf.get_rawglob('diffusion')

    log.info("Convert DTI ...") 
    # check if .nii / .nii.gz is already available
    if op.exists(op.join(dti_dir, 'DTI.nii')):
        shutil.copy(op.join(dti_dir, 'DTI.nii'), op.join(nifti_dir, 'DTI.nii'))
    else:
        # read data
        first = sorted(glob(op.join(dti_dir, raw_glob)))[0]
        diff_cmd = 'diff_unpack %s %s' % (first, op.join(nifti_dir, 'DTI.nii'))            
        runCmd(diff_cmd, log)
        
        # extract bvals, bvects, affine from dsi and store them as .txt in NIFTI
        data, affine, bval, bvect = dr.read_mosaic_dir(dti_dir, raw_glob)
        del data
        import numpy as np
        np.savetxt(op.join(diffme, 'dti_affine.txt'), affine, delimiter=',')
        np.savetxt(op.join(diffme, 'dti_bvals.txt'), bval, delimiter=',')
        np.savetxt(op.join(diffme, 'dti_bvects.txt'), bvect, delimiter=',')
        
        arr = np.zeros( (bvect.shape[0],bvect.shape[1]+1) )
        arr[:,:3] = bvect
        arr[:,3] = bval
        np.savetxt(op.join(diffme, 'gradient_table.txt'), arr, delimiter=',')



def dti_resamp():
    
    nifti_dir = op.join(gconf.get_nifti())
    
    log.info("Resampling 'DTI' to 1x1x1 mm^3...")
    
    # extract only first image with nibabel
    img = ni.load(op.join(nifti_dir, 'DTI.nii'))
    data = img.get_data()
    hdr = img.get_header()
    aff = img.get_affine()
    
    # update header
    hdr['dim'][4] = 1
    # first slice
    data = data[:,:,:,0]
    
    ni.save(ni.Nifti1Image(data, aff, hdr), op.join(nifti_dir, 'DTI_first.nii'))
    
    mri_cmd = 'mri_convert -vs 1 1 1 %s %s' % (
                           op.join(nifti_dir, 'DTI_first.nii'),
                           op.join(nifti_dir, 'Diffusion_b0_resampled.nii'))
    
    runCmd(mri_cmd, log)
    
def t12nifti_diff_unpack():

    raw_dir = op.join(gconf.get_rawdata())
    nifti_dir = op.join(gconf.get_nifti())
    
    log.info("Converting 'T1'...")
    t1_dir = op.join(raw_dir, 'T1')
    if op.exists(op.join(t1_dir, 'T1.nii')):
        log.info("T1.nii already exists. No unpacking.")
        shutil.copy(op.join(t1_dir, 'T1.nii'), op.join(nifti_dir, 'T1.nii'))
    else:
        raw_glob = gconf.get_rawglob('T1')
        first = sorted(glob(op.join(t1_dir, raw_glob)))[0]
        diff_cmd = 'diff_unpack %s %s' % (first, op.join(nifti_dir, 'T1.nii'))
        runCmd(diff_cmd, log)
        log.info("Dataset 'T1.nii' succesfully created!")
        
def t22nifti_diff_unpack():
    
    raw_dir = op.join(gconf.get_rawdata())
    nifti_dir = op.join(gconf.get_nifti())
    
    log.info("Converting 'T2'...")
    t2_dir = op.join(raw_dir, 'T2')
    # check if .nii / .nii.gz is already available
    if op.exists(op.join(t2_dir, 'T2.nii')):
        log.info("T2.nii already exists. No unpacking.")
        shutil.copy(op.join(t2_dir, 'T2.nii'), op.join(nifti_dir, 'T2.nii'))
    else:
        raw_glob = gconf.get_rawglob('T2')
        first = sorted(glob(op.join(t2_dir, raw_glob)))[0]
        diff_cmd = 'diff_unpack %s %s' % (first, op.join(nifti_dir, 'T2.nii'))
        runCmd (diff_cmd, log)        
        log.info("Dataset 'T2.nii' successfully created!")

    log.info("[ DONE ]")
    
    
def reorient_t1(model):
    nifti_dir = op.join(gconf.get_nifti())
    if model == 'DSI':
        reorient(op.join(nifti_dir, 'T1.nii'), op.join(nifti_dir, 'DSI.nii'), log)
    elif model == 'DTI':
        reorient(op.join(nifti_dir, 'T1.nii'), op.join(nifti_dir, 'DTI.nii'), log)

def reorient_t2(model):
    nifti_dir = op.join(gconf.get_nifti())
    if model == 'DSI':
        reorient(op.join(nifti_dir, 'T2.nii'), op.join(nifti_dir, 'DSI.nii'), log)
        
    elif model == 'DTI':
        reorient(op.join(nifti_dir, 'T2.nii'), op.join(nifti_dir, 'DTI.nii'), log)
    
    
def run(conf):
    """ Run the first dicom converter step
    
    Parameters
    ----------
    conf : PipelineConfiguration object
        
    """
    # setting the global configuration variable
    globals()['gconf'] = conf
    globals()['log'] = gconf.get_logger() 
    start = time()
    
    log.info("DICOM -> NIFTI conversion")
    log.info("=========================")
    
    if gconf.diffusion_imaging_model == 'DSI':
        diff2nifti_dsi_unpack()
        dsi_resamp()
        
        
    elif gconf.diffusion_imaging_model == 'DTI':
        diff2nifti_dti_unpack()
        dti_resamp()
        t12nifti_diff_unpack()
        
    t12nifti_diff_unpack()
    reorient_t1(gconf.diffusion_imaging_model)
    
    if gconf.registration_mode == 'Nonlinear':
        t22nifti_diff_unpack()
        reorient_t2(gconf.diffusion_imaging_model)

    log.info("Module took %s seconds to process." % (time()-start))

    if not len(gconf.emailnotify) == 0:
        msg = "DICOM Converter module finished!\nIt took %s seconds." % int(time()-start)
        send_email_notification(msg, gconf, log)    
        
def declare_inputs(conf):
    """Declare the inputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)

    raw_dir = op.join(conf.get_rawdata())        
    nifti_dir = op.join(conf.get_nifti())
    dsi_dir = op.join(raw_dir, 'DSI')
    raw_glob = conf.get_rawglob('diffusion')
    diffme = conf.get_diffusion_metadata()
    dti_dir = op.join(raw_dir, 'DTI')
    t1_dir = op.join(raw_dir, 'T1')
    t2_dir = op.join(raw_dir, 'T2')
        
    if conf.diffusion_imaging_model == 'DSI':
        conf.pipeline_status.AddStageInput(stage, dsi_dir, raw_glob, 'dsi-dcm')        
                
    elif conf.diffusion_imaging_model == 'DTI':
        conf.pipeline_status.AddStageInput(stage, dti_dir, raw_glob, 'dti-dcm')
        
    conf.pipeline_status.AddStageInput(stage, t1_dir, raw_glob, 't1-dcm')
    
    if conf.registration_mode == 'Nonlinear':
        conf.pipeline_status.AddStageInput(stage, t2_dir, raw_glob, 't2-dcm')        
                
    
def declare_outputs(conf):
    """Declare the outputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)

    raw_dir = op.join(conf.get_rawdata())        
    nifti_dir = op.join(conf.get_nifti())
    dsi_dir = op.join(raw_dir, 'DSI')
    raw_glob = conf.get_rawglob('diffusion')
    diffme = conf.get_diffusion_metadata()
    dti_dir = op.join(raw_dir, 'DTI')
    
    if conf.diffusion_imaging_model == 'DSI':
        conf.pipeline_status.AddStageOutput(stage, diffme, 'dsi_affine.txt', 'affine')
        conf.pipeline_status.AddStageOutput(stage, diffme, 'dsi_bvals.txt', 'bvals')
        conf.pipeline_status.AddStageOutput(stage, diffme, 'dsi_bvects.txt', 'bvects')
        conf.pipeline_status.AddStageOutput(stage, diffme, 'gradient_table.txt', 'gradient_table')
        conf.pipeline_status.AddStageOutput(stage, nifti_dir, 'DSI.nii', 'dsi-nii')
        
        
    elif conf.diffusion_imaging_model == 'DTI':
        conf.pipeline_status.AddStageOutput(stage, diffme, 'dti_affine.txt', 'affine')
        conf.pipeline_status.AddStageOutput(stage, diffme, 'dti_bvals.txt', 'bvals')
        conf.pipeline_status.AddStageOutput(stage, diffme, 'dti_bvects.txt', 'bvects')
        conf.pipeline_status.AddStageOutput(stage, diffme, 'gradient_table.txt', 'gradient_table')
        conf.pipeline_status.AddStageOutput(stage, nifti_dir, 'DTI.nii', 'dti-nii')

    conf.pipeline_status.AddStageOutput(stage, nifti_dir, 'Diffusion_b0_resampled.nii', 'diffusion-resampled-nii')        
    conf.pipeline_status.AddStageOutput(stage, nifti_dir, 'T1.nii', 't1-nii')
    
    if conf.registration_mode == 'Nonlinear':
        conf.pipeline_status.AddStageOutput(stage, nifti_dir, 'T2.nii', 't2-nii')
        
       
