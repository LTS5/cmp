# Copyright (C) 2009-2011, Ecole Polytechnique Federale de Lausanne (EPFL) and
# Hospital Center and University of Lausanne (UNIL-CHUV), Switzerland
# All rights reserved.
#
#  This software is distributed under the open-source license Modified BSD.

import os, os.path as op
from glob import glob
import subprocess
import sys
from time import time
import shutil
from ...logme import *
from cmp.util import reorient


import nibabel as ni

def dsi2metadata():
    import nibabel.nicom.dicomreaders as dr
    raw_dir = op.join(gconf.get_rawdata())  
    dsi_dir = op.join(raw_dir, 'DSI')
    raw_glob = gconf.get_rawglob('diffusion')
    diffme = gconf.get_diffusion_metadata()
    try:
        # extract bvals, bvects, affine from dsi and store them as .txt in NIFTI
        data, affine, bval, bvect = dr.read_mosaic_dir(dsi_dir, raw_glob)
    except Exception, e:
        log.error("There was an exception: %s" % e)
        return
    
    del data
    import numpy as np
    np.savetxt(op.join(diffme, 'dsi_affine.txt'), affine, delimiter=',')
    np.savetxt(op.join(diffme, 'dsi_bvals.txt'), bval, delimiter=',')
    np.savetxt(op.join(diffme, 'dsi_bvects.txt'), bvect, delimiter=',')

    arr = np.zeros( (bvect.shape[0],bvect.shape[1]+1) )
    arr[:,:3] = bvect
    arr[:,3] = bval
    np.savetxt(op.join(diffme, 'gradient_table.txt'), arr, delimiter=',')
    
def diff2nifti_dsi_unpack():

    raw_dir = op.join(gconf.get_rawdata())    
    nifti_dir = op.join(gconf.get_nifti())
    dsi_dir = op.join(raw_dir, 'DSI')
    raw_glob = gconf.get_rawglob('diffusion')
    diffme = gconf.get_diffusion_metadata()

    log.info("Convert DSI ...")
    # check if .nii.gz / .nii.gz is already available
    if op.exists(op.join(dsi_dir, 'DSI.nii.gz')):
        shutil.copy(op.join(dsi_dir, 'DSI.nii.gz'), op.join(nifti_dir, 'DSI.nii.gz'))
    else:
        # read data
        files = glob(op.join(dsi_dir, raw_glob))
        if len(files) == 0:
            raise Exception('No files found for %s. Maybe change raw_glob variable for subject? (case-sensitive!)' % op.join(dsi_dir, raw_glob) )
		
        first = sorted(files)[0]
        diff_cmd = 'diff_unpack %s %s' % (first,
                                 op.join(nifti_dir, 'DSI.nii.gz'))            
        runCmd(diff_cmd, log)
        
def dsi_resamp():
    
    nifti_dir = op.join(gconf.get_nifti())
    
    log.info("Resampling 'DSI' to 1x1x1 mm^3...")
    
    # extract only first image with nibabel
    try:
        img = ni.load(op.join(nifti_dir, 'DSI.nii.gz'))
    except Exception, e:
        log.error("Exception occured: %s" % e)
        
    data = img.get_data()
    hdr = img.get_header()
    aff = img.get_affine()
    
    # update header
    hdr['dim'][4] = 1
    # first slice
    data = data[:,:,:,0]
    
    ni.save(ni.Nifti1Image(data, aff, hdr), op.join(nifti_dir, 'DSI_first.nii.gz'))
    
    mri_cmd = 'mri_convert -vs 1 1 1 %s %s' % (
                           op.join(nifti_dir, 'DSI_first.nii.gz'),
                           op.join(nifti_dir, 'Diffusion_b0_resampled.nii.gz'))
    
    runCmd(mri_cmd, log)

def diff2nifti_dti_unpack():

    raw_dir = op.join(gconf.get_rawdata())    
    nifti_dir = op.join(gconf.get_nifti())
    diffme = gconf.get_diffusion_metadata()
    dti_dir = op.join(raw_dir, 'DTI')
    raw_glob = gconf.get_rawglob('diffusion')

    log.info("Convert DTI ...") 
    # check if .nii.gz / .nii.gz is already available
    if op.exists(op.join(dti_dir, 'DTI.nii.gz')):
        shutil.copy(op.join(dti_dir, 'DTI.nii.gz'), op.join(nifti_dir, 'DTI.nii.gz'))
    else:
        # read data
        first = sorted(glob(op.join(dti_dir, raw_glob)))[0]
        diff_cmd = 'diff_unpack %s %s' % (first, op.join(nifti_dir, 'DTI.nii.gz'))            
        runCmd(diff_cmd, log)

def diff2nifti_qball_unpack():

    raw_dir = op.join(gconf.get_rawdata())
    nifti_dir = op.join(gconf.get_nifti())
    diffme = gconf.get_diffusion_metadata()
    dti_dir = op.join(raw_dir, 'QBALL')
    raw_glob = gconf.get_rawglob('diffusion')

    log.info("Convert QBALL ...")
    # check if .nii.gz / .nii.gz is already available
    if op.exists(op.join(dti_dir, 'QBALL.nii.gz')):
        shutil.copy(op.join(dti_dir, 'QBALL.nii.gz'), op.join(nifti_dir, 'QBALL.nii.gz'))
    else:
        # read data
        first = sorted(glob(op.join(dti_dir, raw_glob)))[0]
        diff_cmd = 'diff_unpack %s %s' % (first, op.join(nifti_dir, 'QBALL.nii.gz'))
        runCmd(diff_cmd, log)

def dti2metadata():
    import nibabel.nicom.dicomreaders as dr
    raw_dir = op.join(gconf.get_rawdata())  
    dti_dir = op.join(raw_dir, 'DTI')
    diffme = gconf.get_diffusion_metadata()
    raw_glob = gconf.get_rawglob('diffusion')
    try:
        # extract bvals, bvects, affine from dsi and store them as .txt in NIFTI
        data, affine, bval, bvect = dr.read_mosaic_dir(dti_dir, raw_glob)
    except Exception, e:
        log.error("There was an exception: %s" % e)
        return

    del data
    import numpy as np
    np.savetxt(op.join(diffme, 'dti_affine.txt'), affine, delimiter=',')
    np.savetxt(op.join(diffme, 'dti_bvals.txt'), bval, delimiter=',')
    np.savetxt(op.join(diffme, 'dti_bvects.txt'), bvect, delimiter=',')
    
    arr = np.zeros( (bvect.shape[0],bvect.shape[1]+1) )
    arr[:,:3] = bvect
    arr[:,3] = bval
    np.savetxt(op.join(diffme, 'gradient_table.txt'), arr, delimiter=',')

def qball2metadata():
    import nibabel.nicom.dicomreaders as dr
    raw_dir = op.join(gconf.get_rawdata())
    dti_dir = op.join(raw_dir, 'QBALL')
    diffme = gconf.get_diffusion_metadata()
    raw_glob = gconf.get_rawglob('diffusion')
    try:
        # extract bvals, bvects, affine from dsi and store them as .txt in NIFTI
        data, affine, bval, bvect = dr.read_mosaic_dir(dti_dir, raw_glob)
    except Exception, e:
        log.error("There was an exception: %s" % e)
        return

    del data
    import numpy as np
    np.savetxt(op.join(diffme, 'qball_affine.txt'), affine, delimiter=',')
    np.savetxt(op.join(diffme, 'qball_bvals.txt'), bval, delimiter=',')
    np.savetxt(op.join(diffme, 'qball_bvects.txt'), bvect, delimiter=',')

    arr = np.zeros( (bvect.shape[0],bvect.shape[1]+1) )
    arr[:,:3] = bvect
    arr[:,3] = bval
    np.savetxt(op.join(diffme, 'gradient_table.txt'), arr, delimiter=',')

def dti_resamp():
    
    nifti_dir = op.join(gconf.get_nifti())
    
    log.info("Resampling 'DTI' to 1x1x1 mm^3...")
    
    try:
        # extract only first image with nibabel
        img = ni.load(op.join(nifti_dir, 'DTI.nii.gz'))
    except Exception, e:
        log.error("Exception occured: %s" % e)
        
    data = img.get_data()
    hdr = img.get_header()
    aff = img.get_affine()
    
    # update header
    hdr['dim'][4] = 1
    # first slice
    data = data[:,:,:,0]
    
    ni.save(ni.Nifti1Image(data, aff, hdr), op.join(nifti_dir, 'DTI_first.nii.gz'))
    
    mri_cmd = 'mri_convert -vs 1 1 1 %s %s' % (
                           op.join(nifti_dir, 'DTI_first.nii.gz'),
                           op.join(nifti_dir, 'Diffusion_b0_resampled.nii.gz'))
    
    runCmd(mri_cmd, log)

def qball_resamp():

    nifti_dir = op.join(gconf.get_nifti())

    log.info("Resampling 'QBALL' to 1x1x1 mm^3...")

    try:
        # extract only first image with nibabel
        img = ni.load(op.join(nifti_dir, 'QBALL.nii.gz'))
    except Exception, e:
        log.error("Exception occured: %s" % e)

    data = img.get_data()
    hdr = img.get_header()
    aff = img.get_affine()

    # update header
    hdr['dim'][4] = 1
    # first slice
    data = data[:,:,:,0]

    ni.save(ni.Nifti1Image(data, aff, hdr), op.join(nifti_dir, 'QBALL_first.nii.gz'))

    mri_cmd = 'mri_convert -vs 1 1 1 %s %s' % (
                           op.join(nifti_dir, 'QBALL_first.nii.gz'),
                           op.join(nifti_dir, 'Diffusion_b0_resampled.nii.gz'))

    runCmd(mri_cmd, log)
    
def t12nifti_diff_unpack():

    raw_dir = op.join(gconf.get_rawdata())
    nifti_dir = op.join(gconf.get_nifti())
    
    log.info("Converting 'T1'...")
    t1_dir = op.join(raw_dir, 'T1')
    if op.exists(op.join(t1_dir, 'T1.nii.gz')):
        log.info("T1.nii.gz already exists. No unpacking.")
        shutil.copy(op.join(t1_dir, 'T1.nii.gz'), op.join(nifti_dir, 'T1.nii.gz'))
    else:
        raw_glob = gconf.get_rawglob('T1')
        first = sorted(glob(op.join(t1_dir, raw_glob)))[0]
        diff_cmd = 'diff_unpack %s %s' % (first, op.join(nifti_dir, 'T1.nii.gz'))
        runCmd(diff_cmd, log)
        log.info("Dataset 'T1.nii.gz' succesfully created!")
        
def t22nifti_diff_unpack():
    
    raw_dir = op.join(gconf.get_rawdata())
    nifti_dir = op.join(gconf.get_nifti())
    
    log.info("Converting 'T2'...")
    t2_dir = op.join(raw_dir, 'T2')
    # check if .nii.gz / .nii.gz is already available
    if op.exists(op.join(t2_dir, 'T2.nii.gz')):
        log.info("T2.nii.gz already exists. No unpacking.")
        shutil.copy(op.join(t2_dir, 'T2.nii.gz'), op.join(nifti_dir, 'T2.nii.gz'))
    else:
        raw_glob = gconf.get_rawglob('T2')
        first = sorted(glob(op.join(t2_dir, raw_glob)))[0]
        diff_cmd = 'diff_unpack %s %s' % (first, op.join(nifti_dir, 'T2.nii.gz'))
        runCmd (diff_cmd, log)        
        log.info("Dataset 'T2.nii.gz' successfully created!")

    log.info("[ DONE ]")
    
    
def reorient_t1(model):
    nifti_dir = op.join(gconf.get_nifti())
    if model == 'DSI':
        reorient(op.join(nifti_dir, 'T1.nii.gz'), op.join(nifti_dir, 'DSI.nii.gz'), log)
    elif model == 'DTI':
        reorient(op.join(nifti_dir, 'T1.nii.gz'), op.join(nifti_dir, 'DTI.nii.gz'), log)

def reorient_t2(model):
    nifti_dir = op.join(gconf.get_nifti())
    if model == 'DSI':
        reorient(op.join(nifti_dir, 'T2.nii.gz'), op.join(nifti_dir, 'DSI.nii.gz'), log)
        
    elif model == 'DTI':
        reorient(op.join(nifti_dir, 'T2.nii.gz'), op.join(nifti_dir, 'DTI.nii.gz'), log)
    

def inspect(gconf):
    """ Inspect the results of this stage """
    log = gconf.get_logger()


    if gconf.do_convert_T1:
        log.info("Check T1 raw data")
        fsl_view_cmd = 'fslview %s' % (op.join(gconf.get_nifti(), 'T1.nii.gz') )
        runCmd( fsl_view_cmd, log )
        
    if gconf.do_convert_T2:
        log.info("Check T2 raw data")
        fsl_view_cmd = 'fslview %s' % (op.join(gconf.get_nifti(), 'T2.nii.gz') )
        runCmd( fsl_view_cmd, log )

    if gconf.do_convert_diffusion:
        log.info("Check raw diffusion data")
        if gconf.diffusion_imaging_model == 'DSI':
            fsl_view_cmd = 'fslview %s' % (op.join(gconf.get_nifti(), 'DSI.nii.gz') )
            runCmd( fsl_view_cmd, log )
        elif gconf.diffusion_imaging_model == 'DTI':
            fsl_view_cmd = 'fslview %s' % (op.join(gconf.get_nifti(), 'DTI.nii.gz') )
            runCmd( fsl_view_cmd, log )
        elif gconf.diffusion_imaging_model == 'QBALL':
            fsl_view_cmd = 'fslview %s' % (op.join(gconf.get_nifti(), 'QBALL.nii.gz') )
            runCmd( fsl_view_cmd, log )

            
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
    
    if gconf.diffusion_imaging_model == 'DSI' and gconf.do_convert_diffusion:
        diff2nifti_dsi_unpack()
        dsi_resamp()
        if gconf.extract_diffusion_metadata:
            dsi2metadata()
        
    elif gconf.diffusion_imaging_model == 'DTI' and gconf.do_convert_diffusion:
        diff2nifti_dti_unpack()
        dti_resamp()
        if gconf.extract_diffusion_metadata:
            dti2metadata()

    elif gconf.diffusion_imaging_model == 'QBALL' and gconf.do_convert_diffusion:
        diff2nifti_qball_unpack()
        qball_resamp()
        if gconf.extract_diffusion_metadata:
            qball2metadata()
    
    if gconf.do_convert_T1:
        t12nifti_diff_unpack()
        reorient_t1(gconf.diffusion_imaging_model)
    
    if gconf.do_convert_T2:
        t22nifti_diff_unpack()
        reorient_t2(gconf.diffusion_imaging_model)

    log.info("Module took %s seconds to process." % (time()-start))

    if not len(gconf.emailnotify) == 0: 
        msg = ["DICOM Converter", int(time()-start)]
        send_email_notification(msg, gconf, log)    
        
def declare_inputs(conf):
    """Declare the inputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)

    raw_dir = op.join(conf.get_rawdata())        
    nifti_dir = op.join(conf.get_nifti())
    dsi_dir = op.join(raw_dir, 'DSI')
    raw_glob_diffusion = conf.get_rawglob('diffusion')
    raw_glob_T1 = conf.get_rawglob('T1')
    raw_glob_T2 = conf.get_rawglob('T2')
    diffme = conf.get_diffusion_metadata()
    dti_dir = op.join(raw_dir, 'DTI')
    t1_dir = op.join(raw_dir, 'T1')
    t2_dir = op.join(raw_dir, 'T2')

    print ("globs: (%s, %s, %s" % (raw_glob_diffusion, raw_glob_T1, raw_glob_T2))        
    if conf.diffusion_imaging_model == 'DSI'  and conf.do_convert_diffusion:
        conf.pipeline_status.AddStageInput(stage, dsi_dir, raw_glob_diffusion, 'dsi-dcm')        
                
    elif conf.diffusion_imaging_model == 'DTI' and conf.do_convert_diffusion:
        conf.pipeline_status.AddStageInput(stage, dti_dir, raw_glob_diffusion, 'dti-dcm')
        
    if conf.do_convert_T1:        
        conf.pipeline_status.AddStageInput(stage, t1_dir, raw_glob_T1, 't1-dcm')
    
    if conf.do_convert_T2:
        conf.pipeline_status.AddStageInput(stage, t2_dir, raw_glob_T2, 't2-dcm')        
                
    
def declare_outputs(conf):
    """Declare the outputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)

    raw_dir = op.join(conf.get_rawdata())        
    nifti_dir = op.join(conf.get_nifti())
    dsi_dir = op.join(raw_dir, 'DSI')
    diffme = conf.get_diffusion_metadata()
    dti_dir = op.join(raw_dir, 'DTI')
    
    if conf.diffusion_imaging_model == 'DSI' and conf.do_convert_diffusion:
        # not required output in case nibabel dicom reader can not handle DICOMs
#        conf.pipeline_status.AddStageOutput(stage, diffme, 'dsi_affine.txt', 'affine')
#        conf.pipeline_status.AddStageOutput(stage, diffme, 'dsi_bvals.txt', 'bvals')
#        conf.pipeline_status.AddStageOutput(stage, diffme, 'dsi_bvects.txt', 'bvects')
#        conf.pipeline_status.AddStageOutput(stage, diffme, 'gradient_table.txt', 'gradient_table')
        conf.pipeline_status.AddStageOutput(stage, nifti_dir, 'DSI.nii.gz', 'dsi-nii-gz')
        
        
    elif conf.diffusion_imaging_model == 'DTI' and conf.do_convert_diffusion:
        # not required output in case nibabel dicom reader can not handle DICOMs
#        conf.pipeline_status.AddStageOutput(stage, diffme, 'dti_affine.txt', 'affine')
#        conf.pipeline_status.AddStageOutput(stage, diffme, 'dti_bvals.txt', 'bvals')
#        conf.pipeline_status.AddStageOutput(stage, diffme, 'dti_bvects.txt', 'bvects')
#        conf.pipeline_status.AddStageOutput(stage, diffme, 'gradient_table.txt', 'gradient_table')
        conf.pipeline_status.AddStageOutput(stage, nifti_dir, 'DTI.nii.gz', 'dti-nii-gz')

    elif conf.diffusion_imaging_model == 'QBALL' and conf.do_convert_diffusion:
        conf.pipeline_status.AddStageOutput(stage, nifti_dir, 'QBALL.nii.gz', 'qball-nii-gz')

    if conf.do_convert_diffusion:
        conf.pipeline_status.AddStageOutput(stage, nifti_dir, 'Diffusion_b0_resampled.nii.gz', 'diffusion-resampled-nii-gz')
        
    if conf.do_convert_T1:                    
        conf.pipeline_status.AddStageOutput(stage, nifti_dir, 'T1.nii.gz', 't1-nii-gz')
    
    if conf.do_convert_T2: 
        conf.pipeline_status.AddStageOutput(stage, nifti_dir, 'T2.nii.gz', 't2-nii-gz')
        
       
