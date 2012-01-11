# Button: to check

""" This module performs basic resting-state fMRI """

import os, os.path as op
import sys
from time import time
from ...logme import *
import nibabel as nib
import numpy as np
import scipy.io as sio
from os import environ

def realign():
    """ realign volume with mc flirt
    """
    log.info("Realign fMRI volumes")
    log.info("=====================")

    param = ''
    flirt_cmd = 'mcflirt -in %s %s' % (
            op.join(gconf.get_nifti(), 'fMRI.nii.gz'),
            param)
    runCmd(flirt_cmd, log)

    log.info("[ DONE ]")

    
def mean_fmri():
    """ compute mean fMRI
    """
    nifti_dir = op.join(gconf.get_nifti())
    param = ''
    flirt_cmd = 'fslmaths %s -Tmean %s' % (
            op.join(gconf.get_nifti(), 'fMRI_mcf.nii.gz'),
            op.join(gconf.get_nifti(), 'meanfMRI.nii.gz'))
    runCmd(flirt_cmd, log)

    
def lin_regT12meanfmri():
    """ register T1 to mean fMRI
        FSL FLIRT
    """
    log.info("T1 -> meanfmri: FLIRT linear registration")
    log.info("=========================================")

    if not gconf.rsfmri_lin_reg_param == '':
        param = gconf.rsfmri_lin_reg_param
    else:
        param = '-usesqform -nosearch -dof 6 -cost mutualinfo'

    flirt_cmd = 'flirt -in %s -ref %s -out %s -omat %s %s' % (
            op.join(gconf.get_nifti(), 'T1.nii.gz'),
            op.join(gconf.get_nifti(), 'meanfMRI.nii.gz'),
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
        op.join(gconf.get_nifti(), 'meanfMRI.nii.gz'),              # --mov volid  : input/movable volume
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
        op.join(gconf.get_nifti(), 'meanfMRI.nii.gz'),
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

    param = '-interp nearestneighbour'
    for s in gconf.parcellation.keys():
        log.info("Resolution = " + s)
        outfile = op.join(gconf.get_cmp_fmri(), 'ROIv_HR_th-TO-fMRI-%s.nii.gz' % s)
        infile = op.join(gconf.get_cmp_tracto_mask(), s, 'ROIv_HR_th.nii.gz')
        flirt_cmd = 'flirt -applyxfm -init %s -in %s -ref %s -out %s %s' % (
                    outmat,
                    infile,
                    op.join(gconf.get_nifti(), 'meanfMRI.nii.gz'),
                    outfile,
                    param)

        runCmd( flirt_cmd, log )

        if not op.exists(outfile):
            msg = "An error occurred. File %s not generated." % outfile
            log.error(msg)
            raise Exception(msg)

    log.info("[ DONE ]")
    

def average_rsfmri():
    """ compute the average signal for each GM ROI.
    """
    log.info("Compute rs-fMRI signal for each cortical ROI")
    log.info("============================================")

    fdata = nib.load( op.join(gconf.get_nifti(), 'fMRI_mcf.nii.gz') ).get_data()

    tp = fdata.shape[3]

    # loop throughout all the resolutions ('scale33', ..., 'scale500')
    for s in gconf.parcellation.keys():
        infile = op.join(gconf.get_cmp_fmri(), 'ROIv_HR_th-TO-fMRI-%s.nii.gz' % s)
        mask = nib.load( infile ).get_data().astype( np.uint32 )

        # N: number of ROIs for current resolution
        N = mask.max()
        # matrix number of rois vs timepoints
        odata = np.zeros( (N,tp), dtype = np.float32 )

        # loop throughout all the ROIs (current resolution)
        for i in range(1,N+1):
            odata[i-1,:] = fdata[mask==i].mean( axis = 0 )

        np.save( op.join(gconf.get_cmp_fmri(), 'averageTimeseries_%s.npy' % s), odata )

        if gconf.do_save_mat:
            sio.save( op.join(gconf.get_cmp_fmri(), 'averageTimeseries_%s.mat' % s), {'TCS':odata} )

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

    log.info("resting state fMRI stage")
    log.info("========================")

    realign()
    mean_fmri()
    if gconf.rsfmri_registration_mode == 'BBregister':
        bb_regT12meanfmri()
    else:
        lin_regT12meanfmri()
    apply_registration_roi_to_fmean()
    average_rsfmri()

    log.info("Module took %s seconds to process." % (time()-start))

    if not len(gconf.emailnotify) == 0:
        msg = ["rsfMRI analysis", int(time()-start)]
        send_email_notification(msg, gconf, log)


def declare_inputs(conf):
    """Declare the inputs to the stage to the PipelineStatus object"""

    stage = conf.pipeline_status.GetStage(__name__)
    nifti_dir = conf.get_nifti()
    fs_dir_mri = op.join(conf.get_fs(), 'mri')
    
    conf.pipeline_status.AddStageInput(stage, nifti_dir, 'fMRI.nii.gz', 'rs-fMRI-nii.-gz')
    conf.pipeline_status.AddStageInput(stage, nifti_dir, 'T1.nii.gz', 't1-nii-gz')

    # requirements: NativeFreesurfer, and output of parcellation stage
    tracto_masks_path_out = conf.get_cmp_tracto_mask_tob0()
    for p in conf.parcellation.keys():
        conf.pipeline_status.AddStageInput(stage, op.join(tracto_masks_path_out, p), 'ROIv_HR_th.nii.gz', 'ROIv_HR_th_%s-nii-gz' % (p))

    if conf.rsfmri_registration_mode == 'BBregister':
        conf.pipeline_status.AddStageInput(stage, fs_dir_mri, 'rawavg.mgz', 'rawavg-mgz')
        conf.pipeline_status.AddStageInput(stage, fs_dir_mri, 'orig.mgz', 'orig-mgz')


def declare_outputs(conf):
    """Declare the outputs to the stage to the PipelineStatus object"""

    stage = conf.pipeline_status.GetStage(__name__)
    nifti_bbregister_dir = conf.get_nifti_bbregister()

    conf.pipeline_status.AddStageOutput(stage, conf.get_nifti(), 'fMRI_mcf.nii.gz', 'fmri_mcf-nii-gz')
    conf.pipeline_status.AddStageOutput(stage, conf.get_nifti(), 'meanfMRI.nii.gz', 'meanfmri-nii-gz')
    conf.pipeline_status.AddStageOutput(stage, conf.get_nifti(), 'T1-TO-fMRI.nii.gz', 'T1-TO-fMRI-nii-gz')
    conf.pipeline_status.AddStageOutput(stage, conf.get_nifti_trafo(), 'T1-TO-fMRI.mat', 'T1-TO-fMRI-mat')

    for p in conf.parcellation.keys():
        ROI1 = 'ROIv_HR_th-TO-fMRI-' + p + '.nii.gz'
        ROI2 = 'ROIv_HR_th-TO-fMRI-' + p +'-nii-gz'
        series1 = 'averageTimeseries_' + p + '.npy'
        series2 = 'averageTimeseries_' + p + '-npy'
        conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri(), ROI1, ROI2)
        conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri(), series1, series2)
        if conf.do_svae_mat:
            seriesmat1 = 'averageTimeseries_' + p + '.mat'
            seriesmet2 = 'averageTimeseries_' + p + '-mat'
            conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri(), seriesmat1, seriesmat2)


    if conf.rsfmri_registration_mode == 'BBregister':
        conf.pipeline_status.AddStageOutput(stage, nifti_bbregister_dir, 'fMRI-TO-orig.dat', 'fMRI-TO-orig-dat')
        conf.pipeline_status.AddStageOutput(stage, nifti_bbregister_dir, 'fMRI-TO-orig.mat', 'fMRI-TO-orig-mat')
        conf.pipeline_status.AddStageOutput(stage, nifti_bbregister_dir, 'orig-TO-fMRI.mat', 'fMRI-TO-b0-mat')
        conf.pipeline_status.AddStageOutput(stage, nifti_bbregister_dir, 'T1-TO-orig.dat', 'T1-TO-orig-dat')
        conf.pipeline_status.AddStageOutput(stage, nifti_bbregister_dir, 'T1-TO-orig.mat', 'T1-TO-orig-mat')


