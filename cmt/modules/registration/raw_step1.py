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
    
    if not op.exists(raw_dir):
        log.error("Raw data path does not exist: %s" % rawdir)
        log.error("Please create folder structure according to documentation")
        raise Exception("Raw data not available")
    else:
        dsi_dir = op.join(raw_dir, 'DSI')
        if not op.exists(dsi_dir):
            raise Exception("No DSI path in raw data folder")
        t1_dir = op.join(raw_dir, 'T1')
        if not op.exists(t1_dir):
            raise Exception("No T1 path in raw data folder")
        if gconf.reg_mode == 'N':
            t2_dir = op.join(t2_dir)
            if not op.exists(t2_dir):
                raise Exception("No T2 path in raw data folder")
            
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

def regT12b0():
    log.info("T1 -> b0 (LINEAR/NONLINEAR) registration in one time-point")
    
    if gconf.reg_mode == 'N':
        log.info("STEP 1c: T1 -> T2 -> b0 NONLINEAR registration")
    
        # take result display
        
#            # LINEAR register T1 --> b0
#            "${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 3a "${MY_SUBJECT}" "${MY_TP}" 1.1
#            "${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 3a "${MY_SUBJECT}" "${MY_TP}" 1.2
#            "${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 3a "${MY_SUBJECT}" "${MY_TP}" 1.3
#    
#            # Create BINARY MASKS needed for nonlinear registration
#            "${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 3a "${MY_SUBJECT}" "${MY_TP}" 2.1 0.2 0.3        # T2 mask
#            "${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 3a "${MY_SUBJECT}" "${MY_TP}" 2.2 0.2 0.2        # b0 mask
#    
#            # NONLINEAR register T1 --> b0
#            "${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 3a "${MY_SUBJECT}" "${MY_TP}" 3
    
        log.info("[ DONE ]")
    else:
        log.info("STEP 1c: T1 -> b0 LINEAR registration")
    
        # "${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 3b "${MY_SUBJECT}" "${MY_TP}"
    
        log.info("[ DONE ]")


def run(conf, subject_tuple):
    """ Run the first registration step
    
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
#    regT12b0()
    