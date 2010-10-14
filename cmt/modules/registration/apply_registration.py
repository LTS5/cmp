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

    tracto_masks_path = gconf.get_cmt_tracto_mask()
    tracto_masks_path_out = gconf.get_cmt_tracto_mask_tob0()
    
    if not op.exists(tracto_masks_path):
        msg = "Path does not exists but it should after the mask creation module: %s" % tracto_masks_path
        log.error(msg)
        raise Exception(msg)  

    # XXX: is this correct?
    orig_mat = op.join(gconf.get_nifti(), 'T1-TO-T2.mat')
    out_mat = op.join(tracto_masks_path_out, 'tmp_premat.mat')
    try:
        shutil.copy(orig_mat, out_mat)
    finally:
        log.info("Copied file %s to %s." % (orig_mat, out_mat))


    log.info("Apply non-linear registration...")
    # warp fsmask_1mm and parcellations    
    warp_files = ['fsmask_1mm.nii']
    for park in gconf.parcellation.keys():
        warp_files.append(op.join(park, 'ROI_HR_th.nii'))
    
    for infile in warp_files:
        log.info("Warp file: %s" % infile)
        applywarp_cmt = 'applywarp --in="%s" --premat="%s" --ref="%s" --warp="%s" --out="%s" --interp=nn' % \
                        (op.join(tracto_masks_path, infile),
                         out_mat,
                         op.join(gconf.get_nifti(), 'DSI_b0_resampled.nii'),
                         op.join(gconf.get_nifti(), 'T2-TO-b0_warp.nii'),
                         op.join(tracto_masks_path_out, infile)
                         )
        runCmd (applywarp_cmt, log )
        
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

    tracto_masks_path = gconf.get_cmt_tracto_mask()
    tracto_masks_path_out = gconf.get_cmt_tracto_mask_tob0()
    
    if not op.exists(tracto_masks_path):
        msg = "Path does not exists but it should after the mask creation module: %s" % tracto_masks_path
        log.error(msg)
        raise Exception(msg)  

    orig_mat = op.join(gconf.get_nifti(), 'T1-TO-b0.mat')
    out_mat = op.join(tracto_masks_path_out, 'tmp_premat.mat')
    try:
        shutil.copy(orig_mat, out_mat)
    finally:
        log.info("Copied file %s to %s." % (orig_mat, out_mat))

    log.info("Apply linear registration...")

    # warp fsmask_1mm and parcellations
    
    warp_files = ['fsmask_1mm.nii']
    for park in gconf.parcellation.keys():
        warp_files.append(op.join(park, 'ROI_HR_th.nii'))
    
    for infile in warp_files:
        log.info("Warp file: %s" % infile)
        flirt_cmd = 'flirt -applyxfm -init %s -in %s -ref %s -out %s -interp nearestneighbour' % (
                    out_mat,
                    op.join(tracto_masks_path, infile),
                    op.join(gconf.get_nifti(), 'DSI_b0_resampled.nii'),
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
    

def run(conf, subject_tuple):
    """ Run the apply registration step
    
    Parameters
    ----------
    conf : PipelineConfiguration object
    subject_tuple : tuple, (subject_id, timepoint)
        Process the given subject
        
    """
    # setting the global configuration variable
    globals()['gconf'] = conf
    globals()['sid'] = subject_tuple
    globals()['log'] = gconf.get_logger4subject(sid) 
    
    start = time()
    
    if gconf.registration_mode == 'N':
        apply_nlin_registration()
    elif gconf.registration_mode == 'L':
        apply_lin_registration()
    
    log.info("Module took %s seconds to process." % (time()-start))

    if not len(gconf.emailnotify) == 0:
        msg = "Apply registration module finished!\nIt took %s seconds." % int(time()-start)
        send_email_notification(msg, gconf.emailnotify, log)  
    
