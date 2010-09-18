import os, os.path as op
import logging
log = logging.getLogger()
from glob import glob
import subprocess
import sys
import shutil

import nibabel.nicom.dicomreaders as dr
import nibabel as ni

def dicom2nifti():
    log.info("STEP 1a: DICOM -> NIFTI conversion")

    raw_dir = op.join(gconf.get_raw4subject(sid))
    
    nifti_dir = op.join(gconf.get_nifti4subject(sid))
    if not op.exists(nifti_dir):
        try:
            os.makedirs(nifti_dir)
        except os.error:
            log.info("%s was already existing" % str(nifti_dir))
       
    log.info("Convert DSI ...") 
    # check if .nii / .nii.gz is already available
    if op.exists(op.join(dsi_dir, 'DSI.nii')):
        shutil.copy(op.join(dsi_dir, 'DSI.nii'), op.join(nifti_dir, 'DSI.nii'))
    else:
        
        # read data
        dd = dr.read_mosaic_dir(dsi_dir, gconf.raw_glob)

        # save data and affine as nifti
        ni.save(ni.Nifti1Image(dd[0], dd[1]), op.join(nifti_dir, 'DSI.nii'))
    
        log.info("Dataset 'DSI.nii' succesfully created!")

    log.info("Resampling 'DSI' to 1x1x1 mm^3...")

    mri_cmd = ['mri_convert -vs 1 1 1 %s %s' % (
                           op.join(nifti_dir, 'DSI.nii'),
                           op.join(nifti_dir, 'DSI_b0_resampled.nii.gz'))]

    
    # XXX: does not create resampled. nii
    log.info("Starting mri_convert ...")
    proc = subprocess.Popen(' '.join(mri_cmd),
                           shell = True,
                           stdout = subprocess.PIPE,
                           stderr = subprocess.PIPE,
                           cwd = gconf.get_cmt_rawdiff4subject(sid))
    
    out, err = proc.communicate()
    log.info(out)

    log.info("Converting 'T1'...")

    # check if .nii / .nii.gz is already available
    if op.exists(op.join(t1_dir, 'T1.nii')):
        shutil.copy(op.join(t1_dir, 'T1.nii'), op.join(nifti_dir, 'T1.nii'))
    else:
        
        # read data
        dd = dr.read_mosaic_dir(t1_dir, gconf.raw_glob)

    ## change orientation of "T1" to fit "b0"
    #"${CMT_HOME}/registration"/nifti_reorient_like.sh "T1.nii" "DSI.nii"

        # save data and affine as nifti
        ni.save(ni.Nifti1Image(dd[0], dd[1]), op.join(nifti_dir, 'T1.nii'))
    
        log.info("Dataset 'T1.nii' succesfully created!")
        

    if gconf.reg_mode == 'N':
        log.info("Converting 'T2'...")
    
        # check if .nii / .nii.gz is already available
        if op.exists(op.join(t2_dir, 'T2.nii')):
            shutil.copy(op.join(t2_dir, 'T2.nii'), op.join(nifti_dir, 'T2.nii'))
        else:
            
            # read data
            dd = dr.read_mosaic_dir(t2_dir, gconf.raw_glob)
    
            #    # change orientation of "T2" to fit "b0"
            #    "${CMT_HOME}/registration"/nifti_reorient_like.sh "T2.nii" "DSI.nii"
    
            # save data and affine as nifti
            ni.save(ni.Nifti1Image(dd[0], dd[1]), op.join(nifti_dir, 'T2.nii'))
        
            log.info("Dataset 'T2.nii' succesfully created!")

    log.info("[ DONE ]")
    
    pass


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
    
    dicom2nifti()
    