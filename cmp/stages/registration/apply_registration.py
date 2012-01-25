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
import shutil

def apply_nlin_registration():
    
    log.info("Apply the nonlinear REGISTRATION TRANSFORM to the output of FreeSurfer (WM+GM)")
    log.info("==============================================================================")
    log.info("(i.e. fsmask_1mm.*, scale33/ROI_HR_th.* etc)")

    tracto_masks_path = gconf.get_cmp_tracto_mask()
    tracto_masks_path_out = gconf.get_cmp_tracto_mask_tob0()
    
    if not op.exists(tracto_masks_path):
        msg = "Path does not exists but it should after the mask creation module: %s" % tracto_masks_path
        log.error(msg)
        raise Exception(msg)  

    # XXX: is this correct?
    orig_mat = op.join(gconf.get_nifti_trafo(), 'T1-TO-T2.mat')
    out_mat = op.join(tracto_masks_path_out, 'tmp_premat.mat')
    try:
        shutil.copy(orig_mat, out_mat)
    finally:
        log.info("Copied file %s to %s." % (orig_mat, out_mat))


    log.info("Apply non-linear registration...")
    # warp fsmask_1mm and parcellations    
    warp_files = ['fsmask_1mm.nii.gz']
    for park in gconf.parcellation.keys():
        warp_files.append(op.join(park, 'ROI_HR_th.nii.gz'))
        if gconf.parcellation_scheme == "Lausanne2008":
            warp_files.append(op.join(park, 'ROIv_HR_th.nii.gz'))
    
    for infile in warp_files:
        log.info("Warp file: %s" % infile)
        applywarp_cmp = 'applywarp --in="%s" --premat="%s" --ref="%s" --warp="%s" --out="%s" --interp=nn' % \
                        (op.join(tracto_masks_path, infile),
                         out_mat,
                         op.join(gconf.get_nifti(), 'Diffusion_b0_resampled.nii.gz'),
                         op.join(gconf.get_nifti(), 'T2-TO-b0_warp.nii.gz'),
                         op.join(tracto_masks_path_out, infile)
                         )
        runCmd (applywarp_cmp, log )
        
        if not op.exists(op.join(tracto_masks_path_out, infile)):
            msg = "An error occurred. File %s not generated." % op.join(tracto_masks_path_out, infile)
            log.error(msg)
            raise Exception(msg)
        
        log.info("[ DONE ]")
        
    log.info("Chain of registrations applied. [ DONE ]")
    log.info("[ Saved in %s ]" % tracto_masks_path_out)


def apply_lin_registration():

    log.info("Apply the linear REGISTRATION TRANSFORM to the output of FreeSurfer (WM+GM)")
    log.info("===========================================================================")
    log.info("(i.e. fsmask_1mm.*, scale33/ROI_HR_th.* etc)")

    tracto_masks_path = gconf.get_cmp_tracto_mask()
    tracto_masks_path_out = gconf.get_cmp_tracto_mask_tob0()
    
    if not op.exists(tracto_masks_path):
        msg = "Path does not exists but it should after the mask creation module: %s" % tracto_masks_path
        log.error(msg)
        raise Exception(msg)  

    orig_mat = op.join(gconf.get_nifti_trafo(), 'T1-TO-b0.mat')
    out_mat = op.join(tracto_masks_path_out, 'tmp_premat.mat')
    try:
        shutil.copy(orig_mat, out_mat)
    finally:
        log.info("Copied file %s to %s." % (orig_mat, out_mat))

    log.info("Apply linear registration...")

    # warp fsmask_1mm and parcellations
    
    warp_files = ['fsmask_1mm.nii.gz']
    for park in gconf.parcellation.keys():
        warp_files.append(op.join(park, 'ROI_HR_th.nii.gz'))
        if gconf.parcellation_scheme == "Lausanne2008":
            warp_files.append(op.join(park, 'ROIv_HR_th.nii.gz'))
    
    for infile in warp_files:
        log.info("Warp file: %s" % infile)
        flirt_cmd = 'flirt -applyxfm -init %s -in %s -ref %s -out %s -interp nearestneighbour' % (
                    out_mat,
                    op.join(tracto_masks_path, infile),
                    op.join(gconf.get_nifti(), 'Diffusion_b0_resampled.nii.gz'),
                    op.join(tracto_masks_path_out, infile)
                    )
        
        runCmd( flirt_cmd, log )
        
        if not op.exists(op.join(tracto_masks_path_out, infile)):
            msg = "An error occurred. File %s not generated." % op.join(tracto_masks_path_out, infile)
            log.error(msg)
            raise Exception(msg)
        
        log.info("[ DONE ]")              
        
    log.info("Chain of registrations applied. [ DONE ]")
    log.info("[ Saved in %s ]" % tracto_masks_path_out)
    

def run(conf):
    """ Run the apply registration step
    
    Parameters
    ----------
    conf : PipelineConfiguration object
        
    """
    # setting the global configuration variable
    globals()['gconf'] = conf
    globals()['log'] = gconf.get_logger() 
    
    start = time()
    
    if gconf.registration_mode == 'Nonlinear':
        apply_nlin_registration()
    elif gconf.registration_mode == 'Linear' or gconf.registration_mode == 'BBregister':
        apply_lin_registration()
    
    log.info("Module took %s seconds to process." % (time()-start))

    if not len(gconf.emailnotify) == 0:
        msg = ["Apply registration", int(time()-start)]
        send_email_notification(msg, gconf, log)  
        
        
def declare_inputs(conf):
    """Declare the inputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)
    nifti_trafo_dir = conf.get_nifti_trafo()
    nifti_dir = conf.get_nifti()
    tracto_masks_path = conf.get_cmp_tracto_mask()
    
    if conf.registration_mode == 'Nonlinear':
        conf.pipeline_status.AddStageInput(stage, nifti_trafo_dir, 'T1-TO-T2.mat', 'T1-TO-T2-mat')
        conf.pipeline_status.AddStageInput(stage, nifti_dir, 'T2-TO-b0_warp.nii.gz', 'T2-TO-b0_warp-nii-gz')
    
    elif conf.registration_mode == 'Linear':
        conf.pipeline_status.AddStageInput(stage, nifti_trafo_dir, 'T1-TO-b0.mat', 'T1-TO-b0-mat')
        
    conf.pipeline_status.AddStageInput(stage, tracto_masks_path, 'fsmask_1mm.nii.gz', 'fsmask_1mm-nii-gz')
    conf.pipeline_status.AddStageInput(stage, nifti_dir, 'Diffusion_b0_resampled.nii.gz', 'Diffusion_b0_resampled-nii-gz')
    for p in conf.parcellation.keys():
        conf.pipeline_status.AddStageInput(stage, op.join(tracto_masks_path, p), 'ROI_HR_th.nii.gz', 'ROI_HR_th_%s-nii-gz' % (p))

    if conf.parcellation_scheme == "Lausanne2008":
        for p in conf.parcellation.keys():
            conf.pipeline_status.AddStageInput(stage, op.join(tracto_masks_path, p), 'ROIv_HR_th.nii.gz', 'ROIv_HR_th_%s-nii-gz' % (p))

    
def declare_outputs(conf):
    """Declare the outputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)
    tracto_masks_path_out = conf.get_cmp_tracto_mask_tob0()
            
    conf.pipeline_status.AddStageOutput(stage, tracto_masks_path_out, 'fsmask_1mm.nii.gz', 'fsmask_1mm-nii-gz')            
    for p in conf.parcellation.keys():
        conf.pipeline_status.AddStageOutput(stage, op.join(tracto_masks_path_out, p), 'ROI_HR_th.nii.gz', 'ROI_HR_th_%s-nii-gz' % (p))

    if conf.parcellation_scheme == "Lausanne2008":
        for p in conf.parcellation.keys():
            conf.pipeline_status.AddStageOutput(stage, op.join(tracto_masks_path_out, p), 'ROIv_HR_th.nii.gz', 'ROIv_HR_th_%s-nii-gz' % (p))
                    
