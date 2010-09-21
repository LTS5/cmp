import os, os.path as op
import sys
from time import time
from ...logme import *
from glob import glob
import subprocess
import shutil

# comment:
# skip: transformations from other time points
# skip: Fixing MISSING LABELS in transformed datasets...

def apply_registration():
    
    log.info("Apply the REGISTRATION TRANSFORM to the output of FreeSurfer (WM+GM)")
    log.info("====================================================================")
    log.info("(i.e. fsmask_1mm.*, scale33/ROI_HR_th.* etc)")

    tracto_masks_path = op.join(gconf.get_cmt_fsout4subject(sid),'registred', 'HR')
    tracto_masks_path_out = op.join(gconf.get_cmt_fsout4subject(sid), 'registred', 'HR__registered-TO-b0')
    
    if not op.exists(tracto_masks_path):
        msg = "Path does not exists but it should: %s" % tracto_masks_path
        log.error(msg)
        raise Exception(msg)
    
    # create folders
    
    #rm -fR "${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0" > /dev/null

    if not op.exists(tracto_masks_path_out):
        try:
            os.makedirs(tracto_masks_path_out)
        except os.error:
            log.info("%s was already existing" % str(tracto_masks_path_out))
        finally:
            log.info("%s created." % tracto_masks_path_out)

    for park, parv in gconf.parcellation.items():
        
        par_path = op.join(tracto_masks_path_out, park)

        if not op.exists(par_path):
            try:
                os.makedirs(par_path)
            except os.error:
                log.info("%s was already existing" % str(par_path))
            finally:
                log.info("Path created: %s" % par_path)
            
            
    if gconf.registration_mode == 'N':
        
        # XXX: is this correct?
        orig_mat = op.join(gconf.get_nifti4subject(sid), 'T1-TO-T2.mat')
        out_mat = op.join(tracto_masks_path_out, 'tmp_premat.mat')
        try:
            sh.copy(orig_mat, out_mat)
        finally:
            log.info("Copied file %s to %s." % (orig_mat, out_mat))

    else:
        
        orig_mat = op.join(gconf.get_nifti4subject(sid), 'T1-TO-b0.mat')
        out_mat = op.join(tracto_masks_path_out, 'tmp_premat.mat')
        try:
            shutil.copy(orig_mat, out_mat)
        finally:
            log.info("Copied file %s to %s." % (orig_mat, out_mat))

    if gconf.registration_mode == 'N':
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
                             op.join(gconf.get_nifti4subject(sid), 'DSI_b0_resampled.nii'),
                             op.join(gconf.get_nifti4subject(sid), 'T2-TO-b0_warp.nii'),
                             op.join(tracto_masks_path_out, infile)
                             )
            runCmd (apply_cmt, log )
            
            if not op.exists(op.join(tracto_masks_path_out, infile)):
                msg = "An error occurred. File %s not generated." % op.join(tracto_masks_path_out, infile)
                log.error(msg)
                raise Exception(msg)
            
            log.info("[ DONE ]")
    
        
    else:
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
                        op.join(gconf.get_nifti4subject(sid), 'DSI_b0_resampled.nii'),
                        op.join(tracto_masks_path_out, infile)
                        )
            
            runCmd( flirt_cmd, log )
            
            if not op.exists(op.join(tracto_masks_path_out, infile)):
                msg = "An error occurred. File %s not generated." % op.join(tracto_masks_path_out, infile)
                log.error(msg)
                raise Exception(msg)
            
            log.info("[ DONE ]")
            
    # XXX: what about this?
    #if [ ${D} != 'fsmask_1mm' ]; then
    #    cp "${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0/${D}.nii" "${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0/${D}__forRoiSizeCalc.nii"
    #fi

    # rm -f "${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0/tmp_premat.mat"

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
    
    apply_registration()
    
    log.info("Module took %s seconds to process." % (time()-start))