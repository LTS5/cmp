import os, os.path as op
from glob import glob
from time import time
import subprocess
import sys
from ...logme import *
import shutil 
from cmt.util import mymove

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
            op.join(gconf.get_nifti(), 'T1.nii'),
            op.join(gconf.get_nifti(), 'Diffusion_b0_resampled.nii'),
            op.join(gconf.get_nifti(), 'T1-TO-b0.nii'),
            op.join(gconf.get_nifti(), 'T1-TO-b0.mat'),
            param)
    runCmd(flirt_cmd, log)
    
    if not op.exists(op.join(gconf.get_nifti(), 'T1-TO-b0.mat')):
        msg = "An error occurred. Linear transformation file %s not generated." % op.join(gconf.get_nifti(), 'T1-TO-b0.mat')
        log.error(msg)
        raise Exception(msg)

    # check the results
    if gconf.inspect_registration:
        log.info("FLIRT has finished. Check the result with FSLVIEW.")        
        fsl_view_cmd = 'fslview %s %s -l Copper -t 0.5' % (op.join(gconf.get_nifti(), 'Diffusion_b0_resampled.nii'),
                                                           op.join(gconf.get_nifti(), 'T1-TO-b0.nii') )
        runCmd( fsl_view_cmd, log )
    
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
    
    fli_cmt = 'flirt -in "%s" -ref "%s" -nosearch -dof 6 -cost mutualinfo -out "%s" -omat "%s"' % (
            op.join(nifti_dir, "T1.nii"),
            op.join(nifti_dir, "T2.nii"),
            op.join(nifti_dir, "T1-TO-T2.nii"),
            op.join(gconf.get_nifti_trafo(), "T1-TO-T2.mat"),
            )
    runCmd( fli_cmt, log )
    
    if not op.exists(op.join(gconf.get_nifti_trafo(), "T1-TO-T2.mat")):
        log.error("T1-TO-T2.mat Problem with FLIRT. Unable to find linear transformation 'T1-TO-T2.mat'.")

    if gconf.inspect_registration:
        log.info("FLIRT has finished. Check the result with FSLVIEW.")        
        fsl_view_cmd = 'fslview %s %s -l Copper -t 0.5' % (op.join(gconf.get_nifti(), 'T2.nii'),
                                                           op.join(gconf.get_nifti(), 'T1-TO-T2.nii') )
        runCmd( fsl_view_cmd, log )
        
        
    ##############
    log.info('1.2] -> linear register "T2" onto "b0_resampled"')
    
    fli_cmt = 'flirt -in "%s" -ref "%s" -nosearch -dof 12 -cost normmi -out "%s" -omat "%s"' % (
            op.join(nifti_dir, "T2.nii"),
            op.join(nifti_dir, "Diffusion_b0_resampled.nii"),
            op.join(nifti_dir, "T2-TO-b0.nii"),
            op.join(gconf.get_nifti_trafo(), "T2-TO-b0.mat"),
            )
    runCmd( fli_cmt, log )
    
    if not op.exists(op.join(nifti_dir, "T2-TO-b0.nii")):
        log.error("T2-TO-b0.nii" "Problem with FLIRT. Unable to find linear transformation 'T2-TO-b0.mat'.")

    if gconf.inspect_registration:
        log.info("FLIRT has finished. Check the result with FSLVIEW.")        
        fsl_view_cmd = 'fslview %s %s -l Copper -t 0.5' % (op.join(gconf.get_nifti(), 'Diffusion_b0_resampled.nii'),
                                                           op.join(gconf.get_nifti(), 'T2-TO-b0.nii') )
        runCmd( fsl_view_cmd, log )
        
        
    ##############
    log.info('[1.3] -> apply the linear registration "T1" --> "b0" (for comparison)')
    
    con_cmt = 'convert_xfm -concat "%s" "%s" -omat "%s"' % (op.join(gconf.get_nifti_trafo(), "T2-TO-b0.mat"),
                                                            op.join(gconf.get_nifti_trafo(), "T1-TO-T2.mat"),
                                                            op.join(gconf.get_nifti_trafo(), "T1-TO-b0.mat"))
    runCmd( con_cmt, log )
    
    fli_cmt = 'flirt -in "%s" -ref "%s" -applyxfm -init "%s" -out "%s" -interp sinc' % (
            op.join(nifti_dir, "T1.nii"),
            op.join(nifti_dir, "Diffusion_b0_resampled.nii"),
            op.join(gconf.get_nifti_trafo(), "T1-TO-b0.mat"),
            op.join(nifti_dir, "T1-TO-b0.nii"),
            )
    runCmd( fli_cmt, log )
    
    if not op.exists(op.join(nifti_dir, "T1-TO-b0.nii")):
        log.error("T1-TO-b0.nii Problem with FLIRT. Unable to find linear transformation 'T1-TO-b0.mat'.")
    
    if gconf.inspect_registration:
        log.info("FLIRT has finished. Check the result with FSLVIEW.")        
        fsl_view_cmd = 'fslview %s %s -l Copper -t 0.5' % (op.join(gconf.get_nifti(), 'Diffusion_b0_resampled.nii'),
                                                           op.join(gconf.get_nifti(), 'T1-TO-b0.nii') )
        runCmd( fsl_view_cmd, log )
        
        
       
    #===========================================================================
    log.info("[SUB-STEP 2] Create BINARY MASKS for nonlinear registration")
    #===========================================================================

    log.info("[2.1] -> create a T2 brain mask")

    if not gconf.nlin_reg_bet_T2_param == '':
        param = gconf.nlin_reg_bet_T2_param
    else:
        param = '-f 0.35 -g 0.15'
        
    #rm -f "T2-brain-mask.nii" > /dev/null
    infile = op.join(nifti_dir, "T2.nii")
    outfile = op.join(nifti_dir, "T2-brain")
    bet_cmd = 'bet "%s" "%s" -m -n -R %s' % (infile, outfile, param)
    runCmd( bet_cmd, log ) 
    
    if not op.exists(op.join(nifti_dir, "T2-brain_mask.nii")):
        log.error("T2-brain_mask.nii Problem with BET. Unable to extract the skull.")
        
        
    src = op.join(nifti_dir, "T2-brain_mask.nii")
    dst = op.join(nifti_dir, "T2-brain-mask.nii")
    mymove(src,dst,log)

    log.info("BET has finished. Check the result with FSLVIEW.")
    
    if gconf.inspect_registration:
        log.info("FLIRT has finished. Check the result with FSLVIEW.")        
        fsl_view_cmd = 'fslview %s %s -l Red -b 0,1 -t 0.4' % (op.join(gconf.get_nifti(), 'T2.nii'),
                                                           op.join(gconf.get_nifti(), 'T2-brain-mask.nii') )
        runCmd( fsl_view_cmd, log )
         

    log.info("[2.2] -> create a DSI_b0 brain mask")
    
    if not gconf.nlin_reg_bet_b0_param == '':
        param = gconf.nlin_reg_bet_b0_param
    else:
        param = '-f 0.2 -g 0.2'
        
    #    rm -f "b0-brain-mask.nii"
    
    infile = op.join(nifti_dir, "Diffusion_b0_resampled.nii")
    outfile = op.join(nifti_dir, "b0-brain")
    bet_cmd = 'bet "%s" "%s" -m -n -R %s' % (infile, outfile, param)
    runCmd( bet_cmd, log ) 
    
    if not op.exists(op.join(nifti_dir, "b0-brain_mask.nii")):
        log.error("b0-brain_mask.nii Problem with BET. Unable to extract the skull.")
        
    
    src = op.join(nifti_dir, "b0-brain_mask.nii")
    dst = op.join(nifti_dir, "b0-brain-mask.nii")
    mymove(src,dst,log)

    log.info("BET has finished. Check the result with FSLVIEW.")
    
    if gconf.inspect_registration:
        log.info("FLIRT has finished. Check the result with FSLVIEW.")        
        fsl_view_cmd = 'fslview %s %s -l Red -b 0,1 -t 0.4' % (op.join(gconf.get_nifti(), "Diffusion_b0_resampled.nii"),
                                                           op.join(gconf.get_nifti(), "b0-brain-mask.nii") )
        runCmd( fsl_view_cmd, log )


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
    
    tup = (op.join(nifti_dir, "T2.nii"),
         op.join(gconf.get_nifti_trafo(), "T2-TO-b0.mat"),
         op.join(nifti_dir, "Diffusion_b0_resampled.nii"),
         op.join(nifti_dir, "T2-TO-b0_warped.nii"),
         op.join(nifti_dir, "T2-TO-b0_warp.nii"),
         op.join(nifti_dir, "T2-TO-b0_warp-field.nii"),
         op.join(nifti_dir, "T2-brain-mask.nii"),
         op.join(nifti_dir, "b0-brain-mask.nii"),
         param)

    fn_cmd = 'fnirt -v --in="%s" --aff="%s" --ref="%s" --iout="%s" --cout="%s" --fout="%s" --inmask="%s" --refmask="%s" %s' % tup
    runCmd( fn_cmd, log )
        
    if not op.exists(op.join(nifti_dir, "T2-TO-b0_warped.nii")):
        log.error("Problem with FNIRT. Unable to find nonlinear transformation 'T2-TO-b0_warp.nii'.")
        
    if gconf.inspect_registration:
        log.info("FNIRT has finished. Check the result with FSLVIEW.")        
        fsl_view_cmd = 'fslview "%s" -l Copper "%s" "%s" -t 0.5' % (op.join(nifti_dir, "Diffusion_b0_resampled.nii"),
                                                                    op.join(nifti_dir, "T2-TO-b0.nii"),
                                                                    op.join(nifti_dir, "T2-TO-b0_warped.nii") )
        runCmd( fsl_view_cmd, log )
        
    
    log.info('[3.2] -> apply the warp found for "T2" also onto "T1"')

    # rm -f "T1-TO-b0_warped".*
    tup = (op.join(nifti_dir, "T1.nii"),
           op.join(gconf.get_nifti_trafo(), "T1-TO-T2.mat"),
           op.join(nifti_dir, "Diffusion_b0_resampled.nii"),
           op.join(nifti_dir, "T2-TO-b0_warp.nii"),
           op.join(nifti_dir, "T1-TO-b0_warped.nii"))
    
    app_cmd = 'applywarp --in="%s" --premat="%s" --ref="%s" --warp="%s" --out="%s"' % tup
    runCmd( app_cmd, log )
        
    if not op.exists(op.join(nifti_dir, "T1-TO-b0_warped.nii")):
        log.error("T1-TO-b0_warped.nii" "Problems with APPLYWARP. Unable to apply nonlinear transformation 'T2-TO-b0_warp.nii'.")
            
    # check the results
    log.info('APPLYWARP finished. Check the result with FSLVIEW.')
    
    if gconf.inspect_registration:
        log.info("FNIRT has finished. Check the result with FSLVIEW.")        
        fsl_view_cmd = 'fslview "%s" -l Copper "%s" "%s"' % (op.join(nifti_dir, "Diffusion_b0_resampled.nii"),
                                                                    op.join(nifti_dir, "T1-TO-b0.nii"),
                                                                    op.join(nifti_dir, "T1-TO-b0_warped.nii") )
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
    
    if gconf.registration_mode == 'N':
        nlin_regT12b0()
    else:
        lin_regT12b0()
    
    log.info("Module took %s seconds to process." % (time()-start))

    if not len(gconf.emailnotify) == 0:
        msg = "Registration module finished!\nIt took %s seconds." % int(time()-start)
        send_email_notification(msg, gconf.emailnotify, log)
          
