# Copyright (C) 2009-2011, Ecole Polytechnique Federale de Lausanne (EPFL) and
# Hospital Center and University of Lausanne (UNIL-CHUV), Switzerland
# All rights reserved.
#
#  This software is distributed under the open-source license Modified BSD.

""" This module performs basic resting-state fMRI """

import os, os.path as op
import sys
from time import time
from ...logme import *
import nibabel as nib
import numpy as np
import scipy.io as sio
import scipy
from os import environ
import statsmodels.api as sm


def slice_timing():
    """ perform time slicing with FSL slicetimer
    """
    log.info("Perform slice timing on fMRI volumes")
    log.info("====================================")

    if gconf.rsfmri_slice_timing == 'bottom-top interleaved':
        param = '--odd'
    elif gconf.rsfmri_slice_timing == 'top-bottom interleaved':
        param = '--down --odd'
    elif gconf.rsfmri_slice_timing == 'bottom-top':
        param = ' '
    elif gconf.rsfmri_slice_timing == 'top-bottom':
        param = '--down'

    fsl_cmd = 'slicetimer -i %s -o %s %s' % (
            op.join(gconf.get_nifti(), 'fMRI.nii.gz'),
            op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_slt.nii.gz'),
            param)
    runCmd(fsl_cmd, log)

    log.info("[ DONE ]")

    
def motion_correction():
    """ realign volume with FSL mcflirt
    """
    log.info("Realign fMRI volumes")
    log.info("=====================")

    # Output from previous preprocessing step
    if gconf.rsfmri_slice_timing != 'none':
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_slt.nii.gz')
    else:
        ref_path = op.join(gconf.get_nifti(), 'fMRI.nii.gz')

    param = '-stats -mats -plots'
    fsl_cmd = 'mcflirt -in %s -o %s %s' % (
            ref_path,
            op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_mcf'),
            param)
    runCmd(fsl_cmd, log)

    log.info("[ DONE ]")

    
def lin_regT12meanfmri():
    """ register T1 to mean fMRI
        FSL FLIRT
    """
    log.info("T1 -> meanfmri: FLIRT linear registration")
    log.info("=========================================")

    # apply skullstrip before linear registration
    fsl_cmd = 'bet %s %s' % (
        op.join(gconf.get_nifti(), 'T1.nii.gz'),
        op.join(gconf.get_nifti(), 'T1_skullstrip.nii.gz')
    )
    runCmd(fsl_cmd, log)
    fsl_cmd = 'bet %s %s' % (
        op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_mcf_meanvol.nii.gz'),
        op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_mcf_meanvol_skullstrip.nii.gz')
    )
    runCmd(fsl_cmd, log)

    if not gconf.rsfmri_lin_reg_param == '':
        param = gconf.rsfmri_lin_reg_param
    else:
        param = '-usesqform -nosearch -dof 6 -cost mutualinfo'

    flirt_cmd = 'flirt -in %s -ref %s -out %s -omat %s %s' % (
            op.join(gconf.get_nifti(), 'T1_skullstrip.nii.gz'),
            op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_mcf_meanvol_skullstrip.nii.gz'),
            op.join(gconf.get_nifti(), 'T1-TO-fMRI.nii.gz'),
            op.join(gconf.get_nifti_trafo(), 'T1-TO-fMRI.mat'),
            param)
    runCmd(flirt_cmd, log)

    if not op.exists(op.join(gconf.get_nifti_trafo(), 'T1-TO-fMRI.mat')):
        msg = "An error occurred. Linear transformation file %s not generated." % op.join(gconf.get_nifti_trafo(), 'T1-TO-fMRI.mat')
        log.error(msg)
        raise Exception(msg)
    
    log.info("[ DONE ]")


def bb_regT12meanfmri():
    """ register T1 to mean fMRI
        FREESURFER BBREGISTER
    """
    log.info("T1 -> meanfmri: BBREGISTER linear registration")
    log.info("==============================================")

    if not gconf.rsfmri_bb_reg_param == '':
        param = gconf.rsfmri_bb_reg_param
    else:
        param = '--init-header --dti'

    environ['SUBJECTS_DIR'] = gconf.get_subj_dir()

    bbregister_cmd = 'bbregister --s %s --mov %s --reg %s --fslmat %s %s' % (
        'FREESURFER',                                               # --s subject  : FreeSurfer subject name
        op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_mcf_meanvol.nii.gz'),              # --mov volid  : input/movable volume
        op.join(gconf.get_nifti_bbregister(), 'fMRI-TO-orig.dat'),  # --reg register.dat : output registration file
        op.join(gconf.get_nifti_bbregister(), 'fMRI-TO-orig.mat'),
        param)
    runCmd(bbregister_cmd, log)

    convert_xfm_command = 'convert_xfm -inverse %s -omat %s' % (    # tool for manipulating FSL transformation matrices
        op.join(gconf.get_nifti_bbregister(), 'fMRI-TO-orig.mat'),
        op.join(gconf.get_nifti_bbregister(), 'orig-TO-fMRI.mat'),
    )
    runCmd(convert_xfm_command, log)

    tkregister2_command = 'tkregister2 --regheader --mov %s --targ %s --regheader --reg %s --fslregout %s --noedit' % ( # --regheader : compute regstration from headers
        op.join(gconf.get_fs(), 'mri', 'rawavg.mgz'),               # --mov  movable volume  <fmt>
        op.join(gconf.get_fs(), 'mri', 'orig.mgz'),                 # --targ target volume <fmt>
        op.join(gconf.get_nifti_bbregister(), 'T1-TO-orig.dat'),    # --reg  register.dat : input/output registration file
        op.join(gconf.get_nifti_bbregister(), 'T1-TO-orig.mat'),    # --fslregout file : FSL-Style registration output matrix
    )
    runCmd(tkregister2_command, log)

    convert_xfm_command = 'convert_xfm -omat %s -concat %s %s' % (
        op.join(gconf.get_nifti_trafo(), 'T1-TO-fMRI.mat'),
        op.join(gconf.get_nifti_bbregister(), 'orig-TO-fMRI.mat'),
        op.join(gconf.get_nifti_bbregister(), 'T1-TO-orig.mat'),
    )
    runCmd(convert_xfm_command, log)

    flirt_cmd = 'flirt -applyxfm -init %s -in %s -ref %s -out %s' % (
        op.join(gconf.get_nifti_trafo(), 'T1-TO-fMRI.mat'),
        op.join(gconf.get_nifti(), 'T1.nii.gz'),
        op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_mcf_meanvol.nii.gz'),
        op.join(gconf.get_nifti(), 'T1-TO-fMRI.nii.gz'),
    )
    runCmd(flirt_cmd, log)

    if not op.exists(op.join(gconf.get_nifti_trafo(), 'T1-TO-fMRI.mat')):
        msg = "An error occurred. Linear transformation file %s not generated." % op.join(gconf.get_nifti_trafo(), 'T1-TO-fMRI.mat')
        log.error(msg)
        raise Exception(ms)

    log.info("[ DONE ]")

    
def apply_registration_roi_to_fmean():
    """ apply registration ROI_HR to fmean
    """
    log.info("Apply registration T1-TO-fMRI to cortical ROIs")
    log.info("==============================================")

    outmat = op.join( gconf.get_nifti_trafo(), 'T1-TO-fMRI.mat' )

    if gconf.rsfmri_registration_mode == 'BBregister':
        reffile = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_mcf_meanvol.nii.gz')
    else:
        reffile = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_mcf_meanvol_skullstrip.nii.gz')

    param = '-interp nearestneighbour'
    for s in gconf.parcellation.keys():
        log.info("Resolution = " + s)
        outfile = op.join(gconf.get_cmp_fmri(), 'ROIv_HR_th-TO-fMRI-%s.nii.gz' % s)
        infile = op.join(gconf.get_cmp_tracto_mask(), s, 'ROIv_HR_th.nii.gz')

        flirt_cmd = 'flirt -applyxfm -init %s -in %s -ref %s -out %s %s' % (
                    outmat,
                    infile,
                    reffile,
                    outfile,
                    param)

        runCmd( flirt_cmd, log )

        if not op.exists(outfile):
            msg = "An error occurred. File %s not generated." % outfile
            log.error(msg)
            raise Exception(msg)

    log.info("WM mask")
    outfile = op.join(gconf.get_cmp_fmri(), 'fsmask_1mm-TO-fMRI.nii.gz')
    infile = op.join(gconf.get_cmp_tracto_mask(), 'fsmask_1mm.nii.gz')
    flirt_cmd = 'flirt -applyxfm -init %s -in %s -ref %s -out %s %s' % (
                    outmat,
                    infile,
                    reffile,
                    outfile,
                    param)
    runCmd( flirt_cmd, log )

    log.info("aseg")
    outfile = op.join(gconf.get_cmp_fmri(), 'aseg-TO-fMRI.nii.gz')
    infile = op.join(gconf.get_cmp_tracto_mask(), 'aseg.nii.gz')
    flirt_cmd = 'flirt -applyxfm -init %s -in %s -ref %s -out %s %s' % (
                    outmat,
                    infile,
                    reffile,
                    outfile,
                    param)
    runCmd( flirt_cmd, log )

    log.info("[ DONE ]")


def run(conf):
    """ Run the first rsfmri analysis stage

    Parameters
    ----------
    conf : PipelineConfiguration object

    """
    # setting the global configuration variable
    globals()['gconf'] = conf
    globals()['log'] = gconf.get_logger()
    start = time()

    log.info("Resting state fMRI - Registration stage")
    log.info("=======================================")

    # PREPROCESSING
    if conf.rsfmri_slice_timing != 'none':
        slice_timing()
    motion_correction()

    # REGISTRATION
    if conf.rsfmri_registration_mode == 'BBregister':
        bb_regT12meanfmri()
    else:
        lin_regT12meanfmri()

    # APPLY REGISTRATION
    apply_registration_roi_to_fmean()

    log.info("Module took %s seconds to process." % (time()-start))

    if not len(gconf.emailnotify) == 0:
        msg = ["rsfMRI registration", int(time()-start)]
        send_email_notification(msg, gconf, log)


def declare_inputs(conf):
    """Declare the inputs to the stage to the PipelineStatus object"""

    stage = conf.pipeline_status.GetStage(__name__)
    nifti_dir = conf.get_nifti()
    fs_dir_mri = op.join(conf.get_fs(), 'mri')
    
    conf.pipeline_status.AddStageInput(stage, nifti_dir, 'fMRI.nii.gz', 'rs-fMRI-nii.-gz')
    conf.pipeline_status.AddStageInput(stage, nifti_dir, 'T1.nii.gz', 't1-nii-gz')

    # requirements: NativeFreesurfer, and output of parcellation stage
    tracto_masks_path = conf.get_cmp_tracto_mask()
    for p in conf.parcellation.keys():
        conf.pipeline_status.AddStageInput(stage, op.join(tracto_masks_path, p), 'ROIv_HR_th.nii.gz', 'ROIv_HR_th_%s-nii-gz' % (p))

    if conf.rsfmri_registration_mode == 'BBregister':
        conf.pipeline_status.AddStageInput(stage, fs_dir_mri, 'rawavg.mgz', 'rawavg-mgz')
        conf.pipeline_status.AddStageInput(stage, fs_dir_mri, 'orig.mgz', 'orig-mgz')


def declare_outputs(conf):
    """Declare the outputs to the stage to the PipelineStatus object"""

    stage = conf.pipeline_status.GetStage(__name__)
    nifti_bbregister_dir = conf.get_nifti_bbregister()

    if conf.rsfmri_slice_timing != 'none':
        conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_preproc(), 'fMRI_slt.nii.gz', 'fmri_slt-nii-gz')

    conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_preproc(), 'fMRI_mcf.nii.gz', 'fmri_mcf-nii-gz')
    conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_preproc(), 'fMRI_mcf_meanvol.nii.gz', 'fmri_mcf_meanvol-nii-gz')
    conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_preproc(), 'fMRI_mcf.par', 'fmri_mcf-par')

    conf.pipeline_status.AddStageOutput(stage, conf.get_nifti(), 'T1-TO-fMRI.nii.gz', 'T1-TO-fMRI-nii-gz')
    conf.pipeline_status.AddStageOutput(stage, conf.get_nifti_trafo(), 'T1-TO-fMRI.mat', 'T1-TO-fMRI-mat')

    conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri(), 'aseg-TO-fMRI.nii.gz', 'aseg-TO-fMRI-nii-gz')
    conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri(), 'fsmask_1mm-TO-fMRI.nii.gz', 'fsmask_1mm-TO-fMRI-nii-gz')

    for p in conf.parcellation.keys():
        ROI1 = 'ROIv_HR_th-TO-fMRI-' + p + '.nii.gz'
        ROI2 = 'ROIv_HR_th-TO-fMRI-' + p +'-nii-gz'
        conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri(), ROI1, ROI2)

    if conf.rsfmri_registration_mode == 'BBregister':
        conf.pipeline_status.AddStageOutput(stage, nifti_bbregister_dir, 'fMRI-TO-orig.dat', 'fMRI-TO-orig-dat')
        conf.pipeline_status.AddStageOutput(stage, nifti_bbregister_dir, 'fMRI-TO-orig.mat', 'fMRI-TO-orig-mat')
        conf.pipeline_status.AddStageOutput(stage, nifti_bbregister_dir, 'orig-TO-fMRI.mat', 'fMRI-TO-b0-mat')
        conf.pipeline_status.AddStageOutput(stage, nifti_bbregister_dir, 'T1-TO-orig.dat', 'T1-TO-orig-dat')
        conf.pipeline_status.AddStageOutput(stage, nifti_bbregister_dir, 'T1-TO-orig.mat', 'T1-TO-orig-mat')
    else:
        conf.pipeline_status.AddStageOutput(stage, conf.get_nifti(), 'T1_skullstrip.nii.gz', 'T1_skullstrip-nii-gz')
        conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_preproc(), 'fMRI_mcf_meanvol_skullstrip.nii.gz', 'fMRI_mcf_meanvol_skullstrip-nii-gz')




