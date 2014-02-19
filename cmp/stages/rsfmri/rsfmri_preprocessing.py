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
from scipy import signal
import nibabel as nib
import numpy as np
import scipy.io as sio
import scipy
from os import environ
import statsmodels.api as sm



def spatial_smoothing():
    """ smooth fMRI volumes
    """
    log.info("Apply Gaussian smoothing on fMRI volumes")
    log.info("========================================")

    param = '-s '+ gconf.rsfmri_smoothing
    fsl_cmd = 'fslmaths %s %s %s' % (
            op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_mcf.nii.gz'),
            param,
            op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_smoothing.nii.gz'))
    runCmd(fsl_cmd, log)

    log.info("[ DONE ]")


def discard_timepoints():
    """ discard first n timpoints
    """
    log.info("Discard first n timepoints")
    log.info("==========================")

    # Output from previous preprocessing step
    if float(gconf.rsfmri_smoothing) > 0:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_smoothing.nii.gz')
    else:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_mcf.nii.gz')

    # Extract CSF average signal
    dataimg = nib.load( ref_path )
    data = dataimg.get_data()

    n_discard = float(gconf.rsfmri_discard) - 1

    new_data = data.copy()
    new_data = new_data[:,:,:,n_discard:-1]

    hd = dataimg.get_header()
    hd.set_data_shape([hd.get_data_shape()[0],hd.get_data_shape()[1],hd.get_data_shape()[2],hd.get_data_shape()[3]-n_discard-1])
    img = nib.Nifti1Image(new_data, dataimg.get_affine(), hd)
    nib.save(img, op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_discard.nii.gz'))

    log.info("[ DONE ]")


def nuisance_regression():
    #regress out nuisance signals (WM, CSF, movements) through GLM
    
    log.info("Regression of nuisance signals")
    log.info("==============================")

    # Output from previous preprocessing step
    if float(gconf.rsfmri_discard) > 0:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_discard.nii.gz')
    elif float(gconf.rsfmri_smoothing) > 0:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_smoothing.nii.gz')
    else:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_mcf.nii.gz')
        
    # Extract whole brain average signal
    dataimg = nib.load( ref_path )
    data = dataimg.get_data()
    tp = data.shape[3]
    if gconf.rsfmri_nuisance_global:
        brainfile = op.join(gconf.get_cmp_fmri(), 'brain_eroded-TO-fMRI.nii.gz') # load eroded whole brain mask
        brain = nib.load( brainfile ).get_data().astype( np.uint32 )
        global_values = data[brain==1].mean( axis = 0 )
        global_values = global_values - np.mean(global_values)
        np.save( op.join(gconf.get_cmp_fmri_preproc(), 'averageGlobal.npy'), global_values )
        sio.savemat( op.join(gconf.get_cmp_fmri_preproc(), 'averageGlobal.mat' ), {'avgGlobal':global_values} )    		

    # Extract CSF average signal
    if gconf.rsfmri_nuisance_CSF:
        csffile = op.join(gconf.get_cmp_fmri(), 'csf_eroded-TO-fMRI.nii.gz') # load eroded CSF mask
        csf = nib.load( csffile ).get_data().astype( np.uint32 )
        csf_values = data[csf==1].mean( axis = 0 )
        csf_values = csf_values - np.mean(csf_values)
        np.save( op.join(gconf.get_cmp_fmri_preproc(), 'averageCSF.npy'), csf_values )
        sio.savemat( op.join(gconf.get_cmp_fmri_preproc(), 'averageCSF.mat' ), {'avgCSF':csf_values} )

    # Extract WM average signal
    if gconf.rsfmri_nuisance_WM:
        WMfile = op.join(gconf.get_cmp_fmri(), 'fsmask_1mm_eroded-TO-fMRI.nii.gz') # load eroded WM mask
        WM = nib.load( WMfile ).get_data().astype( np.uint32 )
        wm_values = data[WM==1].mean( axis = 0 )
        wm_values = wm_values - np.mean(wm_values)
        np.save( op.join(gconf.get_cmp_fmri_preproc(), 'averageWM.npy'), wm_values )
        sio.savemat( op.join(gconf.get_cmp_fmri_preproc(), 'averageWM.mat' ), {'avgWM':wm_values} )

    # Import parameters from head motion estimation
    if gconf.rsfmri_nuisance_motion:
        move = np.genfromtxt( op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_mcf.par') )
        move = move - np.mean(move,0)

    # GLM: regress out nuisance covariates
    new_data = data.copy()
    s = gconf.parcellation.keys()[0]
    gm = nib.load(op.join(gconf.get_cmp_fmri(), 'ROIv_HR_th-TO-fMRI-%s.nii.gz' % s)).get_data().astype( np.uint32 )
    if float(gconf.rsfmri_discard) > 0:
        n_discard = float(gconf.rsfmri_discard) - 1
        if gconf.rsfmri_nuisance_motion:
            move = move[n_discard:-1,:]

    # build regressors matrix
    if gconf.rsfmri_nuisance_global:
		X = np.hstack(global_values.reshape(tp,1))
		log.info('Detrend global average signal')
		if gconf.rsfmri_nuisance_CSF:		
			X = np.hstack((X.reshape(tp,1),csf_values.reshape(tp,1)))
			log.info('Detrend CSF average signal')
			if gconf.rsfmri_nuisance_WM:
				X = np.hstack((X,wm_values.reshape(tp,1)))
				log.info('Detrend WM average signal')
				if gconf.rsfmri_nuisance_motion:
					X = np.hstack((X,move))
					log.info('Detrend motion average signals')
			elif gconf.rsfmri_nuisance_motion:
				X = np.hstack((X,move))
				log.info('Detrend motion average signals')
		elif gconf.rsfmri_nuisance_WM:
			X = np.hstack((X.reshape(tp,1),wm_values.reshape(tp,1)))
			log.info('Detrend WM average signal')
			if gconf.rsfmri_nuisance_motion:
				X = np.hstack((X,move))
				log.info('Detrend motion average signals')
		elif gconf.rsfmri_nuisance_motion:
			X = np.hstack((X.reshape(tp,1),move))
			log.info('Detrend motion average signals')
    elif gconf.rsfmri_nuisance_CSF:			
		X = np.hstack((csf_values.reshape(tp,1)))
		log.info('Detrend CSF average signal')
		if gconf.rsfmri_nuisance_WM:
			X = np.hstack((X.reshape(tp,1),wm_values.reshape(tp,1)))
			log.info('Detrend WM average signal')
			if gconf.rsfmri_nuisance_motion:
				X = np.hstack((X,move))
				log.info('Detrend motion average signals')
		elif gconf.rsfmri_nuisance_motion:
			X = np.hstack((X.reshape(tp,1),move))
			log.info('Detrend motion average signals')
    elif gconf.rsfmri_nuisance_WM:				
		X = np.hstack((wm_values.reshape(tp,1)))
		log.info('Detrend WM average signal')
		if gconf.rsfmri_nuisance_motion:
			X = np.hstack((X.reshape(tp,1),move))
			log.info('Detrend motion average signals')
    elif gconf.rsfmri_nuisance_motion:
		X = move
		log.info('Detrend motion average signals')
		
    X = sm.add_constant(X)
    log.info('Shape X GLM')
    log.info(X.shape)

    # loop throughout all GM voxels
    for index,value in np.ndenumerate( gm ):
        Y = data[index[0],index[1],index[2],:].reshape(tp,1)
        gls_model = sm.GLS(Y,X)
        gls_results = gls_model.fit()
        #new_data[index[0],index[1],index[2],:] = gls_results.resid
        new_data[index[0],index[1],index[2],:] = gls_results.resid #+ gls_results.params[8]

    img = nib.Nifti1Image(new_data, dataimg.get_affine(), dataimg.get_header())
    nib.save(img, op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_nuisance.nii.gz'))

    log.info("[ DONE ]")


def linear_detrending(rsfmri_nuisance):
    """ linear detrending
    """
    log.info("Linear detrending")
    log.info("=================")

    # Output from previous preprocessing step
    if rsfmri_nuisance:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_nuisance.nii.gz')
    elif float(gconf.rsfmri_discard) > 0:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_discard.nii.gz')
    elif float(gconf.rsfmri_smoothing) > 0:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_smoothing.nii.gz')
    else:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_mcf.nii.gz')

    # Load data
    dataimg = nib.load( ref_path )
    data = dataimg.get_data()
    tp = data.shape[3]

    # GLM: regress out nuisance covariates
    new_data_det = data.copy()
    s = gconf.parcellation.keys()[0]
    gm = nib.load(op.join(gconf.get_cmp_fmri(), 'ROIv_HR_th-TO-fMRI-%s.nii.gz' % s)).get_data().astype( np.uint32 )

    for index,value in np.ndenumerate( gm ):
        if value == 0:
            continue

        Ydet = signal.detrend(data[index[0],index[1],index[2],:].reshape(tp,1), axis=0)
        new_data_det[index[0],index[1],index[2],:] = Ydet[:,0]

    img = nib.Nifti1Image(new_data_det, dataimg.get_affine(), dataimg.get_header())
    nib.save(img, op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_detrending.nii.gz'))

    log.info("[ DONE ]")    


def lowpass_filtering(rsfmri_nuisance):
    """ apply lowpass filtering in time domain
    """
    log.info("Apply lowpass filtering")
    log.info("=======================")

    # Output from previous preprocessing step
    if gconf.rsfmri_detrending:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_detrending.nii.gz')
    elif rsfmri_nuisance:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_nuisance.nii.gz')
    elif float(gconf.rsfmri_discard) > 0:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_discard.nii.gz')
    elif float(gconf.rsfmri_smoothing) > 0:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_smoothing.nii.gz')
    else:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_mcf.nii.gz')

    param = '-bptf -1 ' + gconf.rsfmri_lowpass
    fsl_cmd = 'fslmaths %s %s %s' % (
            ref_path,
            param,
            op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_lowpass'))
    runCmd(fsl_cmd, log)

    log.info("[ DONE ]")


def scrubbing(rsfmri_nuisance):
    """ compute scrubbing parameters: FD and DVARS
    """
    log.info("Precompute FD and DVARS for scrubbing")
    log.info("=====================================")

    # Output from previous preprocessing step
    if float(gconf.rsfmri_lowpass) > 0:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_lowpass.nii.gz')
    elif gconf.rsfmri_detrending:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_detrending.nii.gz')
    elif rsfmri_nuisance:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_nuisance.nii.gz')
    elif float(gconf.rsfmri_discard) > 0:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_discard.nii.gz')
    elif float(gconf.rsfmri_smoothing) > 0:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_smoothing.nii.gz')
    else:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_mcf.nii.gz')

    dataimg = nib.load( ref_path )
    data = dataimg.get_data()
    tp = data.shape[3]
    WMfile = op.join(gconf.get_cmp_fmri(), 'fsmask_1mm-TO-fMRI.nii.gz')
    WM = nib.load( WMfile ).get_data().astype( np.uint32 )
    s = gconf.parcellation.keys()[0]
    GM = nib.load(op.join(gconf.get_cmp_fmri(), 'ROIv_HR_th-TO-fMRI-%s.nii.gz' % s)).get_data().astype( np.uint32 )
    mask = WM + GM
    move = np.genfromtxt( op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_mcf.par') )

    # initialize motion measures
    FD = np.zeros((tp-1,1))
    DVARS = np.zeros((tp-1,1))

    # loop throughout all the time points
    for i in xrange(0,tp-1):
        # FD
        move0 = move[i,:]
        move1 = move[i+1,:]
        this_move = move1 - move0
        this_move = np.absolute(this_move)
        FD[i] = this_move.sum()

        # DVARS
        # extract current and following time points
        temp0 = data[:,:,:,i]
        temp1 = data[:,:,:,i+1]
        temp = temp1 - temp0
        temp = np.power(temp,2)
        temp = temp[mask>0]
        DVARS[i] = np.power(temp.mean(),0.5)

    np.save( op.join(gconf.get_cmp_fmri_preproc(), 'FD.npy'), FD )
    np.save( op.join(gconf.get_cmp_fmri_preproc(), 'DVARS.npy'), DVARS )
    sio.savemat( op.join(gconf.get_cmp_fmri_preproc(), 'FD.mat'), {'FD':FD} )
    sio.savemat( op.join(gconf.get_cmp_fmri_preproc(), 'DVARS.mat'), {'DVARS':DVARS} )

    log.info("[ DONE ]")


def run(conf):
    """ Run the second rsfmri analysis stage

    Parameters
    ----------
    conf : PipelineConfiguration object

    """
    # setting the global configuration variable
    globals()['gconf'] = conf
    globals()['log'] = gconf.get_logger()
    start = time()

    log.info("Resting state fMRI - Preprocessing stage")
    log.info("========================================")

    # PREPROCESSING STEPS
    if float(conf.rsfmri_smoothing) > 0:
        spatial_smoothing()

    if float(conf.rsfmri_discard) > 0:
        discard_timepoints()


    if conf.rsfmri_nuisance_WM or conf.rsfmri_nuisance_CSF or conf.rsfmri_nuisance_motion:
        rsfmri_nuisance = True
        nuisance_regression()
    else:
        rsfmri_nuisance = False

    if conf.rsfmri_detrending:
        linear_detrending(rsfmri_nuisance)

    if float(conf.rsfmri_lowpass) > 0:
        lowpass_filtering(rsfmri_nuisance)

    if conf.rsfmri_scrubbing_parameters:
        scrubbing(rsfmri_nuisance)

    # Final output preprocessing
    if float(conf.rsfmri_lowpass) > 0:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_lowpass.nii.gz')
    elif conf.rsfmri_detrending:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_detrending.nii.gz')
    elif rsfmri_nuisance:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_nuisance.nii.gz')
    elif float(conf.rsfmri_discard) > 0:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_discard.nii.gz')
    elif float(conf.rsfmri_smoothing) > 0:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_smoothing.nii.gz')
    else:
        ref_path = op.join(gconf.get_cmp_fmri_preproc(), 'fMRI_mcf.nii.gz')
    dataimg = nib.load( ref_path )
    nib.save(dataimg, op.join(conf.get_cmp_fmri_preproc(), 'fMRI_preprocessed.nii.gz'))

    log.info("Module took %s seconds to process." % (time()-start))

    if not len(gconf.emailnotify) == 0:
        msg = ["rsfMRI preprocessing", int(time()-start)]
        send_email_notification(msg, gconf, log)


def declare_inputs(conf):
    """Declare the inputs to the stage to the PipelineStatus object"""

    stage = conf.pipeline_status.GetStage(__name__)

    conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_preproc(), 'fMRI_mcf.nii.gz', 'fmri_mcf-nii-gz')
    conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_preproc(), 'fMRI_mcf.par', 'fmri_mcf-par')

    tracto_masks_path = conf.get_cmp_tracto_mask()
    p = conf.parcellation.keys()[0]
    conf.pipeline_status.AddStageInput(stage, op.join(tracto_masks_path, p), 'ROIv_HR_th.nii.gz', 'ROIv_HR_th_%s-nii-gz' % (p))

    conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri(), 'aseg-TO-fMRI.nii.gz', 'aseg-TO-fMRI-nii-gz')
    conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri(), 'fsmask_1mm-TO-fMRI.nii.gz', 'fsmask_1mm-TO-fMRI-nii-gz')


def declare_outputs(conf):
    """Declare the outputs to the stage to the PipelineStatus object"""

    stage = conf.pipeline_status.GetStage(__name__)

    if float(conf.rsfmri_smoothing) > 0:
        conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_preproc(), 'fMRI_smoothing.nii.gz', 'fmri_smoothing-nii-gz')

    if float(conf.rsfmri_discard) > 0:
        conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_preproc(), 'fMRI_discard.nii.gz', 'fmri_discard-nii-gz')

    if conf.rsfmri_nuisance_WM or conf.rsfmri_nuisance_CSF or conf.rsfmri_nuisance_motion:
        conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_preproc(), 'fMRI_nuisance.nii.gz', 'fmri_nuisance-nii-gz')
        conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_preproc(), 'averageCSF.npy', 'averageCSF-npy')
        conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_preproc(), 'averageWM.npy', 'averageWM-npy')

    if conf.rsfmri_detrending:
        conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_preproc(), 'fMRI_detrending.nii.gz', 'fmri_detrending-nii-gz')

    if float(conf.rsfmri_lowpass) > 0:
        conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_preproc(), 'fMRI_lowpass.nii.gz', 'fmri_lowpass-nii-gz')

    if conf.rsfmri_scrubbing_parameters:
        conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_preproc(), 'FD.npy', 'FD-npy')
        conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_preproc(), 'DVARS.npy', 'DVARS-npy')
        conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_preproc(), 'FD.mat', 'FD-mat')
        conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_preproc(), 'DVARS.mat', 'DVARS-mat')

    conf.pipeline_status.AddStageOutput(stage, conf.get_cmp_fmri_preproc(), 'fMRI_preprocessed.nii.gz', 'fmri_preprocessed-nii-gz')



