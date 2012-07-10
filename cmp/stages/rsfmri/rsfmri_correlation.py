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

    

def average_rsfmri():
    """ compute the average signal for each GM ROI.
    """
    log.info("Compute average rs-fMRI signal for each cortical ROI")
    log.info("====================================================")

    fdata = nib.load( op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_preprocessed.nii.gz') ).get_data()

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

        np.save( op.join(gconf.get_cmp_fmri_timeseries(), 'averageTimeseries_%s.npy' % s), odata )

        if gconf.do_save_mat:
            sio.savemat( op.join(gconf.get_cmp_fmri_timeseries(), 'averageTimeseries_%s.mat' % s), {'TCS':odata} )

    log.info("[ DONE ]")


def compute_correlation():
    """ compute correlation between average fMRI signals
    """
    log.info("Compute functional connectivity matrices")
    log.info("========================================")

    if gconf.rsfmri_scrubbing_apply:
        # load scrubbing FD and DVARS series
        FD = np.load( op.join(gconf.get_cmp_fmri_preproc(), 'FD.npy') )
        DVARS = np.load( op.join(gconf.get_cmp_fmri_preproc(), 'DVARS.npy') )
        # evaluate scrubbing mask
        FD_th = float(gconf.rsfmri_scrubbing_FD)
        DVARS_th = float(gconf.rsfmri_scrubbing_DVARS)
        FD_mask = np.array(np.nonzero(FD < FD_th))[0,:]
        DVARS_mask = np.array(np.nonzero(DVARS < DVARS_th))[0,:]
        index = np.sort(np.unique(np.concatenate((FD_mask,DVARS_mask)))) + 1
        index = np.concatenate(([0],index))
        log_scrubbing = "DISCARDED time points after scrubbing: " + str(FD.shape[0]-index.shape[0]+1) + " over " + str(FD.shape[0]+1)
        log.info(log_scrubbing)
        np.save( op.join(gconf.get_cmp_fmri_preproc(), 'tp_after_scrubbing.npy'), index )
        sio.savemat( op.join(gconf.get_cmp_fmri_preproc(), 'tp_after_scrubbing.mat'), {'index':index} )
    else:
        s = gconf.parcellation.keys()[0]
        ts = np.load( op.join(gconf.get_cmp_fmri_timeseries(), 'averageTimeseries_%s.npy' % s) )
        tp = ts.shape[1]
        index = np.linspace(0,tp-1,tp).astype('int')

    # loop throughout all the resolutions ('scale33', ..., 'scale500')
    for s in gconf.parcellation.keys():
        ts = np.load( op.join(gconf.get_cmp_fmri_timeseries(), 'averageTimeseries_%s.npy' % s) )

        # initialize connectivity matrix
        nnodes = ts.shape[0]
        fmat = np.zeros((nnodes,nnodes))
        i = -1
        for i_signal in ts:
            i += 1
            for j in xrange(i,nnodes):
                j_signal = ts[j,:]
                # apply scrubbing
                value = np.corrcoef(i_signal[index],j_signal[index])[0,1]
                fmat[i,j] = value
                fmat[j,i] = value

        np.save( op.join(gconf.get_cmp_fmri_matrices(), 'fconnectome_%s.npy' % s), fmat )
        if gconf.do_save_mat:
            sio.savemat( op.join(gconf.get_cmp_fmri_matrices(), 'fconnectome_%s.mat' % s), {'fmat':fmat} )

    log.info("[ DONE ]")


def run(conf):
    """ Run the third rsfmri analysis stage

    Parameters
    ----------
    conf : PipelineConfiguration object

    """
    # setting the global configuration variable
    globals()['gconf'] = conf
    globals()['log'] = gconf.get_logger()
    start = time()

    log.info("Resting state fMRI - Correlation stage")
    log.info("======================================")

    # GENERATE AVERAGE TIME SERIES
    average_rsfmri()

    # CORRELATION
    compute_correlation()

    log.info("Module took %s seconds to process." % (time()-start))

    if not len(gconf.emailnotify) == 0:
        msg = ["rsfMRI correlation", int(time()-start)]
        send_email_notification(msg, gconf, log)


def declare_inputs(conf):
    """Declare the inputs to the stage to the PipelineStatus object"""

    stage = conf.pipeline_status.GetStage(__name__)

    conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_preproc(), 'fMRI_preprocessed.nii.gz', 'fmri_preprocessed-nii-gz')

    if conf.rsfmri_scrubbing_apply:
        conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_preproc(), 'FD.npy', 'FD-npy')
        conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_preproc(), 'DVARS.npy', 'DVARS-npy')


def declare_outputs(conf):
    """Declare the outputs to the stage to the PipelineStatus object"""

    stage = conf.pipeline_status.GetStage(__name__)

    for p in conf.parcellation.keys():
        series1 = 'averageTimeseries_' + p + '.npy'
        series2 = 'averageTimeseries_' + p + '-npy'
        fmat1 = 'fconnectome_' + p + '.npy'
        fmat2 = 'fconnectome_' + p + '-npy'
        conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_timeseries(), series1, series2)
        conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_matrices(), fmat1, fmat2)
        if conf.do_save_mat:
            seriesmat1 = 'averageTimeseries_' + p + '.mat'
            seriesmat2 = 'averageTimeseries_' + p + '-mat'
            fmatmat1 = 'fconnectome_' + p + '.mat'
            fmatmat2 = 'fconnectome_' + p + '-mat'
            conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_timeseries(), seriesmat1, seriesmat2)
            conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_matrices(), fmatmat1, fmatmat2)

    if conf.rsfmri_scrubbing_apply:
        conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_preproc(), 'tp_after_scrubbing.npy', 'tp_after_scrubbing-npy')
        conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_preproc(), 'tp_after_scrubbing.mat', 'tp_after_scrubbing-mat')




