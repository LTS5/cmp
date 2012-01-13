# Copyright (C) 2009-2011, Ecole Polytechnique Federale de Lausanne (EPFL) and
# Hospital Center and University of Lausanne (UNIL-CHUV), Switzerland
# All rights reserved.
#
#  This software is distributed under the open-source license Modified BSD.

import os, os.path as op
from glob import glob
from time import time
from os import environ
import subprocess
import sys
from ...logme import *
import shutil 
from cmp.util import mymove

def lin_regT12b0():
    log.info("T1 -> b0: Linear registration")
    log.info("=============================")

    # Linear register "T1" onto "b0_resampled"
    log.info("Started FLIRT to find 'T1 --> b0' linear transformation")

    # XXX: rm -f "T1-TO-b0".*
    if not gconf.lin_reg_param == '':
        param = gconf.lin_reg_param
    else:
        param = '-usesqform -nosearch -dof 6 -cost mutualinfo'
        
    flirt_cmd = 'flirt -in %s -ref %s -out %s -omat %s %s' % (
            op.join(gconf.get_nifti(), 'T1.nii.gz'),
            op.join(gconf.get_nifti(), 'Diffusion_b0_resampled.nii.gz'),
            op.join(gconf.get_nifti(), 'T1-TO-b0.nii.gz'),
            op.join(gconf.get_nifti_trafo(), 'T1-TO-b0.mat'),
            param)
    runCmd(flirt_cmd, log)
    
    if not op.exists(op.join(gconf.get_nifti_trafo(), 'T1-TO-b0.mat')):
        msg = "An error occurred. Linear transformation file %s not generated." % op.join(gconf.get_nifti_trafo(), 'T1-TO-b0.mat')
        log.error(msg)
        raise Exception(msg)
    
    log.info("[ DONE ]")

    
def bb_regT12b0():
    log.info("T1 -> b0: BBREGISTER linear registration")
    log.info("========================================")

    # Linear register "T1" onto "b0_resampled"
    log.info("Started FreeSurfer bbregister to find 'T1 --> b0' linear transformation")

    if not gconf.bb_reg_param == '':
        param = gconf.bb_reg_param
    else:
        param = '--init-header --dti'

    environ['SUBJECTS_DIR'] = gconf.get_subj_dir()

    bbregister_cmd = 'bbregister --s %s --mov %s --reg %s --fslmat %s %s' % (
        'FREESURFER',
        op.join(gconf.get_nifti(), 'Diffusion_b0_resampled.nii.gz'),
        op.join(gconf.get_nifti_bbregister(), 'b0-TO-orig.dat'),
        op.join(gconf.get_nifti_bbregister(), 'b0-TO-orig.mat'),
        param)
    runCmd(bbregister_cmd, log)

    convert_xfm_command = 'convert_xfm -inverse %s -omat %s' % (
        op.join(gconf.get_nifti_bbregister(), 'b0-TO-orig.mat'),
        op.join(gconf.get_nifti_bbregister(), 'orig-TO-b0.mat'),
    )
    runCmd(convert_xfm_command, log)

    tkregister2_command = 'tkregister2 --regheader --mov %s --targ %s --regheader --reg %s --fslregout %s --noedit' % (
        op.join(gconf.get_fs(), 'mri', 'rawavg.mgz'),
        op.join(gconf.get_fs(), 'mri', 'orig.mgz'),
        op.join(gconf.get_nifti_bbregister(), 'T1-TO-orig.dat'),
        op.join(gconf.get_nifti_bbregister(), 'T1-TO-orig.mat'),
    )
    runCmd(tkregister2_command, log)

    convert_xfm_command = 'convert_xfm -omat %s -concat %s %s' % (
        op.join(gconf.get_nifti_trafo(), 'T1-TO-b0.mat'),
        op.join(gconf.get_nifti_bbregister(), 'orig-TO-b0.mat'),
        op.join(gconf.get_nifti_bbregister(), 'T1-TO-orig.mat'),
    )
    runCmd(convert_xfm_command, log)

    flirt_cmd = 'flirt -applyxfm -init %s -in %s -ref %s -out %s' % (
        op.join(gconf.get_nifti_trafo(), 'T1-TO-b0.mat'),
        op.join(gconf.get_nifti(), 'T1.nii.gz'),
        op.join(gconf.get_nifti(), 'Diffusion_b0_resampled.nii.gz'),
        op.join(gconf.get_nifti(), 'T1-TO-b0.nii.gz'),
    )
    runCmd(flirt_cmd, log)

    if not op.exists(op.join(gconf.get_nifti_trafo(), 'T1-TO-b0.mat')):
        msg = "An error occurred. Linear transformation file %s not generated." % op.join(gconf.get_nifti_trafo(), 'T1-TO-b0.mat')
        log.error(msg)
        raise Exception(msg)

    log.info("[ DONE ]")


def nlin_regT12b0():
    log.info("T1 -> b0: Non-linear registration")
    log.info("=================================")
    
    nifti_dir = gconf.get_nifti()
    
    #===========================================================================
    log.info('[SUB-STEP 1] LINEAR register "T2" onto "b0_resampled"')
    #===========================================================================
    
    ##############
    log.info('[1.1] linear register "T1" onto "T2"')
    
    fli_cmp = 'flirt -in "%s" -ref "%s" -nosearch -dof 6 -cost mutualinfo -out "%s" -omat "%s"' % (
            op.join(nifti_dir, "T1.nii.gz"),
            op.join(nifti_dir, "T2.nii.gz"),
            op.join(nifti_dir, "T1-TO-T2.nii.gz"),
            op.join(gconf.get_nifti_trafo(), "T1-TO-T2.mat"),
            )
    runCmd( fli_cmp, log )
    
    if not op.exists(op.join(gconf.get_nifti_trafo(), "T1-TO-T2.mat")):
        log.error("T1-TO-T2.mat Problem with FLIRT. Unable to find linear transformation 'T1-TO-T2.mat'.")        
        
    ##############
    log.info('[1.2] -> linear register "T2" onto "b0_resampled"')
    
    fli_cmp = 'flirt -in "%s" -ref "%s" -nosearch -dof 12 -cost normmi -out "%s" -omat "%s"' % (
            op.join(nifti_dir, "T2.nii.gz"),
            op.join(nifti_dir, "Diffusion_b0_resampled.nii.gz"),
            op.join(nifti_dir, "T2-TO-b0.nii.gz"),
            op.join(gconf.get_nifti_trafo(), "T2-TO-b0.mat"),
            )
    runCmd( fli_cmp, log )
    
    if not op.exists(op.join(nifti_dir, "T2-TO-b0.nii.gz")):
        log.error("T2-TO-b0.nii.gz" "Problem with FLIRT. Unable to find linear transformation 'T2-TO-b0.mat'.")
       
    ##############
    log.info('[1.3] -> apply the linear registration "T1" --> "b0" (for comparison)')
    
    con_cmp = 'convert_xfm -concat "%s" "%s" -omat "%s"' % (op.join(gconf.get_nifti_trafo(), "T2-TO-b0.mat"),
                                                            op.join(gconf.get_nifti_trafo(), "T1-TO-T2.mat"),
                                                            op.join(gconf.get_nifti_trafo(), "T1-TO-b0.mat"))
    runCmd( con_cmp, log )
    
    fli_cmp = 'flirt -in "%s" -ref "%s" -applyxfm -init "%s" -out "%s" -interp sinc' % (
            op.join(nifti_dir, "T1.nii.gz"),
            op.join(nifti_dir, "Diffusion_b0_resampled.nii.gz"),
            op.join(gconf.get_nifti_trafo(), "T1-TO-b0.mat"),
            op.join(nifti_dir, "T1-TO-b0.nii.gz"),
            )
    runCmd( fli_cmp, log )
    
    if not op.exists(op.join(nifti_dir, "T1-TO-b0.nii.gz")):
        log.error("T1-TO-b0.nii.gz Problem with FLIRT. Unable to find linear transformation 'T1-TO-b0.mat'.")
    
    
       
    #===========================================================================
    log.info("[SUB-STEP 2] Create BINARY MASKS for nonlinear registration")
    #===========================================================================

    log.info("[2.1] -> create a T2 brain mask")

    if not gconf.nlin_reg_bet_T2_param == '':
        param = gconf.nlin_reg_bet_T2_param
    else:
        param = '-f 0.35 -g 0.15'
        
    #rm -f "T2-brain-mask.nii.gz" > /dev/null
    infile = op.join(nifti_dir, "T2.nii.gz")
    outfile = op.join(nifti_dir, "T2-brain")
    bet_cmd = 'bet "%s" "%s" -m -n -R %s' % (infile, outfile, param)
    runCmd( bet_cmd, log ) 
    
    if not op.exists(op.join(nifti_dir, "T2-brain_mask.nii.gz")):
        log.error("T2-brain_mask.nii.gz Problem with BET. Unable to extract the skull.")
        
        
    src = op.join(nifti_dir, "T2-brain_mask.nii.gz")
    dst = op.join(nifti_dir, "T2-brain-mask.nii.gz")
    mymove(src,dst,log)        

    log.info("[2.2] -> create a DSI_b0 brain mask")
    
    if not gconf.nlin_reg_bet_b0_param == '':
        param = gconf.nlin_reg_bet_b0_param
    else:
        param = '-f 0.2 -g 0.2'
        
    #    rm -f "b0-brain-mask.nii.gz"
    
    infile = op.join(nifti_dir, "Diffusion_b0_resampled.nii.gz")
    outfile = op.join(nifti_dir, "b0-brain")
    bet_cmd = 'bet "%s" "%s" -m -n -R %s' % (infile, outfile, param)
    runCmd( bet_cmd, log ) 
    
    if not op.exists(op.join(nifti_dir, "b0-brain_mask.nii.gz")):
        log.error("b0-brain_mask.nii.gz Problem with BET. Unable to extract the skull.")
        
    
    src = op.join(nifti_dir, "b0-brain_mask.nii.gz")
    dst = op.join(nifti_dir, "b0-brain-mask.nii.gz")
    mymove(src,dst,log)

    log.info("BET has finished. Check the result with FSLVIEW.")

    #===========================================================================
    log.info('[SUB-STEP 3] NONLINEAR register "T2" onto "b0_resampled"')
    #===========================================================================
    
    log.info('Start NONLINEAR registration with brain-masks')
    
    log.info("'Started FNIRT to find 'T2 --> b0' nonlinear transformation at ")

#    rm -f "T2-TO-b0_warp"*.*
#    rm -f "T2_to_${TP}/T2_to_DSI_b0_resampled.log"

    
    if not gconf.nlin_reg_fnirt_param == '':
        param = gconf.nlin_reg_fnirt_param
    else:
        param = '--subsamp=8,4,2,2 --miter==5,5,5,5 --lambda=240,120,90,30 --splineorder=3 --applyinmask=0,0,1,1 --applyrefmask=0,0,1,1'
    
    tup = (op.join(nifti_dir, "T2.nii.gz"),
         op.join(gconf.get_nifti_trafo(), "T2-TO-b0.mat"),
         op.join(nifti_dir, "Diffusion_b0_resampled.nii.gz"),
         op.join(nifti_dir, "T2-TO-b0_warped.nii.gz"),
         op.join(nifti_dir, "T2-TO-b0_warp.nii.gz"),
         op.join(nifti_dir, "T2-TO-b0_warp-field.nii.gz"),
         op.join(nifti_dir, "T2-brain-mask.nii.gz"),
         op.join(nifti_dir, "b0-brain-mask.nii.gz"),
         param)

    fn_cmd = 'fnirt -v --in="%s" --aff="%s" --ref="%s" --iout="%s" --cout="%s" --fout="%s" --inmask="%s" --refmask="%s" %s' % tup
    runCmd( fn_cmd, log )
        
    if not op.exists(op.join(nifti_dir, "T2-TO-b0_warped.nii.gz")):
        log.error("Problem with FNIRT. Unable to find nonlinear transformation 'T2-TO-b0_warp.nii.gz'.")
        
    
    log.info('[3.2] -> apply the warp found for "T2" also onto "T1"')

    # rm -f "T1-TO-b0_warped".*
    tup = (op.join(nifti_dir, "T1.nii.gz"),
           op.join(gconf.get_nifti_trafo(), "T1-TO-T2.mat"),
           op.join(nifti_dir, "Diffusion_b0_resampled.nii.gz"),
           op.join(nifti_dir, "T2-TO-b0_warp.nii.gz"),
           op.join(nifti_dir, "T1-TO-b0_warped.nii.gz"))
    
    app_cmd = 'applywarp --in="%s" --premat="%s" --ref="%s" --warp="%s" --out="%s"' % tup
    runCmd( app_cmd, log )
        
    if not op.exists(op.join(nifti_dir, "T1-TO-b0_warped.nii.gz")):
        log.error("T1-TO-b0_warped.nii.gz" "Problems with APPLYWARP. Unable to apply nonlinear transformation 'T2-TO-b0_warp.nii.gz'.")
            
    # check the results
    log.info('APPLYWARP finished. Check the result with FSLVIEW.')

    

def inspect(gconf):
    """ Inspect the results of this stage """
    log = gconf.get_logger()
    if gconf.registration_mode == 'Nonlinear':

        log.info("Check T1 registration to T2")        
        fsl_view_cmd = 'fslview %s %s -l Copper -t 0.5' % (op.join(gconf.get_nifti(), 'T2.nii.gz'),
                                                           op.join(gconf.get_nifti(), 'T1-TO-T2.nii.gz') )
        runCmd( fsl_view_cmd, log )

        log.info("Check T2 registration to b0")        
        fsl_view_cmd = 'fslview %s %s -l Copper -t 0.5' % (op.join(gconf.get_nifti(), 'Diffusion_b0_resampled.nii.gz'),
                                                           op.join(gconf.get_nifti(), 'T2-TO-b0.nii.gz') )
        runCmd( fsl_view_cmd, log )

        log.info("Check T1 registration to b0")        
        fsl_view_cmd = 'fslview %s %s -l Copper -t 0.5' % (op.join(gconf.get_nifti(), 'Diffusion_b0_resampled.nii.gz'),
                                                           op.join(gconf.get_nifti(), 'T1-TO-b0.nii.gz') )
        runCmd( fsl_view_cmd, log )

        log.info("Check T2 brain mask")        
        fsl_view_cmd = 'fslview %s %s -l Red -b 0,1 -t 0.4' % (op.join(gconf.get_nifti(), 'T2.nii.gz'),
                                                           op.join(gconf.get_nifti(), 'T2-brain-mask.nii.gz') )
        runCmd( fsl_view_cmd, log )
        
        log.info("Check b0 brain mask")        
        fsl_view_cmd = 'fslview %s %s -l Red -b 0,1 -t 0.4' % (op.join(gconf.get_nifti(), "Diffusion_b0_resampled.nii.gz"),
                                                               op.join(gconf.get_nifti(), "b0-brain-mask.nii.gz") )
        runCmd( fsl_view_cmd, log )
        
        log.info("Check FNIRT result. T2 registration to b0 and to b0_warped")        
        fsl_view_cmd = 'fslview "%s" -l Copper "%s" "%s" -t 0.5' % (op.join(gconf.get_nifti(), "Diffusion_b0_resampled.nii.gz"),
                                                                    op.join(gconf.get_nifti(), "T2-TO-b0.nii.gz"),
                                                                    op.join(gconf.get_nifti(), "T2-TO-b0_warped.nii.gz") )
        runCmd( fsl_view_cmd, log )

        log.info("Check FNIRT result. T1 registration to b0 and to b0_warped")        
        fsl_view_cmd = 'fslview "%s" -l Copper "%s" "%s"' % (op.join(gconf.get_nifti(), "Diffusion_b0_resampled.nii.gz"),
                                                                    op.join(gconf.get_nifti(), "T1-TO-b0.nii.gz"),
                                                                    op.join(gconf.get_nifti(), "T1-TO-b0_warped.nii.gz") )
        runCmd( fsl_view_cmd, log )

    else:
        log.info("FLIRT has finished. Check the result with FSLVIEW.")        
        fsl_view_cmd = 'fslview %s %s -l Copper -t 0.5' % (op.join(gconf.get_nifti(), 'Diffusion_b0_resampled.nii.gz'),
                                                           op.join(gconf.get_nifti(), 'T1-TO-b0.nii.gz') )
        runCmd( fsl_view_cmd, log )

def run(conf):
    """ Run the first registration step
    
    Parameters
    ----------
    conf : PipelineConfiguration object
        
    """
    # setting the global configuration variable
    globals()['gconf'] = conf
    globals()['log'] = gconf.get_logger() 
    start = time()
    
    if gconf.registration_mode == 'Nonlinear':
        nlin_regT12b0()
    elif gconf.registration_mode == 'BBregister':
        bb_regT12b0()
    else:
        lin_regT12b0()
    
    log.info("Module took %s seconds to process." % (time()-start))

    if not len(gconf.emailnotify) == 0:
        msg = ["Registration module", int(time()-start)]
        send_email_notification(msg, gconf, log)


def declare_inputs(conf):
    """Declare the inputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)
    nifti_dir = conf.get_nifti()
    fs_dir_mri = op.join(conf.get_fs(), 'mri')

    conf.pipeline_status.AddStageInput(stage, nifti_dir, 'Diffusion_b0_resampled.nii.gz', 'diffusion-resampled-nii.-gz')
    conf.pipeline_status.AddStageInput(stage, nifti_dir, 'T1.nii.gz', 't1-nii-gz')
    
    if conf.registration_mode == 'Nonlinear':
        conf.pipeline_status.AddStageInput(stage, nifti_dir, 'T2.nii.gz', 't2-nii-gz')

    if conf.registration_mode == 'BBregister':
        conf.pipeline_status.AddStageInput(stage, fs_dir_mri, 'rawavg.mgz', 'rawavg-mgz')
        conf.pipeline_status.AddStageInput(stage, fs_dir_mri, 'orig.mgz', 'orig-mgz')
        
                
def declare_outputs(conf):
    """Declare the outputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)
    nifti_dir = conf.get_nifti()
    nifti_trafo_dir = conf.get_nifti_trafo()
    nifti_bbregister_dir = conf.get_nifti_bbregister()

    conf.pipeline_status.AddStageOutput(stage, nifti_dir, 'T1-TO-b0.nii.gz', 'T1-TO-B0-nii-gz')
    conf.pipeline_status.AddStageOutput(stage, nifti_trafo_dir, 'T1-TO-b0.mat', 'T1-TO-b0-mat')
    
    if conf.registration_mode == 'Nonlinear':
        conf.pipeline_status.AddStageOutput(stage, nifti_dir, 'T1-TO-T2.nii.gz', 'T1-TO-T2-nii-gz')
        conf.pipeline_status.AddStageOutput(stage, nifti_trafo_dir, 'T1-TO-T2.mat', 'T1-TO-T2-mat')
        conf.pipeline_status.AddStageOutput(stage, nifti_dir, 'T2-TO-b0.nii.gz', 'T2-TO-b0-nii-gz')
        conf.pipeline_status.AddStageOutput(stage, nifti_trafo_dir, 'T2-TO-b0.mat', 'T2-TO-b0-mat')
        conf.pipeline_status.AddStageOutput(stage, nifti_dir, 'T2-brain-mask.nii.gz', 'T2-brain-mask-nii-gz')
        conf.pipeline_status.AddStageOutput(stage, nifti_dir, 'b0-brain-mask.nii.gz', 'b0-brain-mask-nii-gz')
        conf.pipeline_status.AddStageOutput(stage, nifti_dir, 'T2-TO-b0_warped.nii.gz', 'T2-TO-b0_warped-nii-gz')
        conf.pipeline_status.AddStageOutput(stage, nifti_dir, 'T1-TO-b0_warped.nii.gz', 'T1-TO-b0_warped-nii-gz')

    if conf.registration_mode == 'BBregister':
        conf.pipeline_status.AddStageOutput(stage, nifti_bbregister_dir, 'b0-TO-orig.dat', 'b0-TO-orig-dat')
        conf.pipeline_status.AddStageOutput(stage, nifti_bbregister_dir, 'b0-TO-orig.mat', 'b0-TO-orig-mat')
        conf.pipeline_status.AddStageOutput(stage, nifti_bbregister_dir, 'orig-TO-b0.mat', 'orig-TO-b0-mat')
        conf.pipeline_status.AddStageOutput(stage, nifti_bbregister_dir, 'T1-TO-orig.dat', 'T1-TO-orig-dat')
        conf.pipeline_status.AddStageOutput(stage, nifti_bbregister_dir, 'T1-TO-orig.mat', 'T1-TO-orig-mat')

