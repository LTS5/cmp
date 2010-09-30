import os, os.path as op
from glob import glob
import subprocess
import sys
from time import time
import shutil
from ...logme import *
from cmt.modules.util import reorient

import nibabel.nicom.dicomreaders as dr
import nibabel as ni

def diff2nifti_dsi_unpack():

    raw_dir = op.join(gconf.get_raw4subject(sid))    
    nifti_dir = op.join(gconf.get_nifti4subject(sid))

    dsi_dir = op.join(raw_dir, 'DSI')
    log.info("Convert DSI ...") 
    # check if .nii / .nii.gz is already available
    if op.exists(op.join(dsi_dir, 'DSI.nii')):
        shutil.copy(op.join(dsi_dir, 'DSI.nii'), op.join(nifti_dir, 'DSI.nii'))
    else:
        # read data
        files = glob(op.join(dsi_dir, gconf.raw_glob))
        if len(files) == 0:
            raise Exception('No files found for %s. Maybe change raw_glob variable?' % op.join(dsi_dir, gconf.raw_glob) )
		
        first = sorted(files)[0]
        diff_cmd = 'diff_unpack %s %s' % (first, op.join(nifti_dir, 'DSI.nii'))            
        runCmd(diff_cmd, log)
        
        # extract bvals, bvects, affine from dsi and store them as .txt in 2__NIFTI
        data, affine, bval, bvect = dr.read_mosaic_dir(dsi_dir, gconf.raw_glob)
        del data
        import numpy as np
        np.savetxt(op.join(nifti_dir, 'dsi_affine.txt'), affine)
        np.savetxt(op.join(nifti_dir, 'dsi_bvals.txt'), bval)
        np.savetxt(op.join(nifti_dir, 'dsi_bvects.txt'), bvect)

    log.info("Resampling 'DSI' to 1x1x1 mm^3...")
    mri_cmd = 'mri_convert -vs 1 1 1 %s %s' % (
                           op.join(nifti_dir, 'DSI.nii'),
                           op.join(nifti_dir, 'DSI_b0_resampled.nii'))
    
    runCmd(mri_cmd, log)

def diff2nifti_dti_unpack():

    raw_dir = op.join(gconf.get_raw4subject(sid))    
    nifti_dir = op.join(gconf.get_nifti4subject(sid))

    dti_dir = op.join(raw_dir, 'DTI')
    log.info("Convert DTI ...") 
    # check if .nii / .nii.gz is already available
    if op.exists(op.join(dti_dir, 'DTI.nii')):
        shutil.copy(op.join(dti_dir, 'DTI.nii'), op.join(nifti_dir, 'DTI.nii'))
    else:
        # read data
        first = sorted(glob(op.join(dti_dir, gconf.raw_glob)))[0]
        diff_cmd = 'diff_unpack %s %s' % (first, op.join(nifti_dir, 'DTI.nii'))            
        runCmd(diff_cmd, log)
        
        # extract bvals, bvects, affine from dsi and store them as .txt in 2__NIFTI
        data, affine, bval, bvect = dr.read_mosaic_dir(dti_dir, gconf.raw_glob)
        del data
        import numpy as np
        np.savetxt(op.join(nifti_dir, 'dti_affine.txt'), affine)
        np.savetxt(op.join(nifti_dir, 'dti_bvals.txt'), bval)
        np.savetxt(op.join(nifti_dir, 'dti_bvects.txt'), bvect)

    log.info("Resampling 'DTI' to 1x1x1 mm^3...")
    mri_cmd = 'mri_convert -vs 1 1 1 %s %s' % (
                           op.join(nifti_dir, 'DTI.nii'),
                           op.join(nifti_dir, 'DTI_b0_resampled.nii'))
    
    runCmd(mri_cmd, log)

def t12nifti_diff_unpack():

    raw_dir = op.join(gconf.get_raw4subject(sid))
    nifti_dir = op.join(gconf.get_nifti4subject(sid))
    
    log.info("Converting 'T1'...")
    t1_dir = op.join(raw_dir, 'T1')
    if op.exists(op.join(t1_dir, 'T1.nii')):
        log.info("T1.nii already exists. No unpacking.")
        shutil.copy(op.join(t1_dir, 'T1.nii'), op.join(nifti_dir, 'T1.nii'))
    else:
        first = sorted(glob(op.join(t1_dir, gconf.raw_glob)))[0]
        diff_cmd = 'diff_unpack %s %s' % (first, op.join(nifti_dir, 'T1.nii'))
        runCmd(diff_cmd, log)
        log.info("Dataset 'T1.nii' succesfully created!")
        
    reorient(op.join(nifti_dir, 'T1.nii'), op.join(nifti_dir, 'DSI.nii'), log)
        
def t22nifti_diff_unpack():
    
    raw_dir = op.join(gconf.get_raw4subject(sid))
    nifti_dir = op.join(gconf.get_nifti4subject(sid))
    
    log.info("Converting 'T2'...")
    t2_dir = op.join(raw_dir, 'T1')
    # check if .nii / .nii.gz is already available
    if op.exists(op.join(t2_dir, 'T2.nii')):
        log.info("T2.nii already exists. No unpacking.")
        shutil.copy(op.join(t2_dir, 'T2.nii'), op.join(nifti_dir, 'T2.nii'))
    else:
        first = sorted(glob(op.join(t1_dir, gconf.raw_glob)))[0]
        diff_cmd = 'diff_unpack %s %s' % (first, op.join(nifti_dir, 'T2.nii'))
        runCmd (diff_cmd, log)        
        log.info("Dataset 'T2.nii' successfully created!")

    reorient(op.join(nifti_dir, 'T2.nii'), op.join(nifti_dir, 'DSI.nii'), log)

    log.info("[ DONE ]")
    
def run(conf, subject_tuple):
    """ Run the first dicom converter step
    
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
    
    log.info("DICOM -> NIFTI conversion")
    log.info("=========================")
    
    if gconf.processing_mode == 'DSI':
        diff2nifti_dsi_unpack()
    elif gconf.processing_mode == 'DTI':
        diff2nifti_dti_unpack()
    t12nifti_diff_unpack()
    if gconf.registration_mode == 'N':
        t22nifti_diff_unpack()

    log.info("Module took %s seconds to process." % (time()-start))
                
