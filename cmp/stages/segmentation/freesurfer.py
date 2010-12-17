import os, os.path as op
from os import environ
from glob import glob
import subprocess
from time import time

from ...logme import *

def copy_orig_to_fs():
    
    log.info("Copying 'NIFTI/T1.nii.gz' dataset to 'FREESURFER/mri/orig/001.mgz'...")

    fs_4subj_mri = op.join(gconf.get_fs(), 'mri', 'orig')

    if not op.exists(op.join(gconf.get_nifti(), 'T1.nii.gz')):
        log.error("File T1.nii.gz does not exists in subject directory")
        
    mri_cmd = 'mri_convert %s %s' % ( 
                             op.join(gconf.get_nifti(), 'T1.nii.gz'),
                             op.join(gconf.get_fs(), 'mri', 'orig', '001.mgz') )
    runCmd(mri_cmd, log)
            
    if not op.exists(op.join(gconf.get_fs(), 'mri', 'orig', '001.mgz')):
        log.error("File 001.mgz has to been generated.")

    log.info("[ DONE ]")


def recon_all():
    log.info("Running the whole FREESURFER pipeline")
    log.info("=====================================")

    environ['SUBJECTS_DIR'] = gconf.get_subj_dir()
    
    log.info("Starting recon-all ...")
    fs_cmd = 'recon-all -s %s -all -no-isrunning' % 'FREESURFER'
    runCmd( fs_cmd, log )

    log.info("[ DONE ]")
    

def before_wm_corr():
    log.info("Copy stuff for correcting the 'wm mask' ");
    log.info("========================================")

    if not op.exists(op.join(gconf.get_fs(), 'mri', 'T1.mgz')):
        log.error('/mir/T1.mgz does not exists in subject folder')
    if not op.exists(op.join(gconf.get_fs(), 'mri', 'wm.mgz')):
        log.error('/mir/wm.mgz does not exists in subject folder')

    wm_exchange_folder = gconf.get_nifti_wm_correction()
    
    mri_cmd = 'mri_convert %s %s' % ( 
                             op.join(gconf.get_fs(), 'mri', 'T1.mgz'),
                             op.join(wm_exchange_folder, 'T1.nii.gz') )
    runCmd( mri_cmd, log )
    
    mri_cmd = 'mri_convert %s %s' % ( 
                             op.join(gconf.get_fs(), 'mri', 'wm.mgz'),
                             op.join(wm_exchange_folder, 'wm.nii.gz') )
    runCmd( mri_cmd, log )
    
    log.info("You can now correct the white matter mask stored in %s " % op.join(wm_exchange_folder, 'wm.nii.gz'))
    log.info("After correction, store it in the same folder with the name wm_corrected.nii.gz")    
        
    if not op.exists(op.join(wm_exchange_folder, 'T1.nii.gz')):
        log.error("Unable to convert the file '/mri/T1.mgz' for subject!")

    if not op.exists(op.join(wm_exchange_folder, 'wm.nii.gz')):
        log.error("Unable to convert the file '/mri/wm.mgz' for subject!")

    log.info("[ DONE ]")

def after_wm_corr():

    log.info("Copying back the corrected 'wm mask' " );
    
    wm_exchange_folder = gconf.get_nifti_wm_correction()
    
    if not op.exists(op.join(wm_exchange_folder, 'wm_corrected.nii.gz')):
        log.error('Need to provide a corrected white matter mask wm_corrected.nii.gz in %s' % wm_exchange_folder)
    
    mri_cmd = 'mri_convert -odt uchar %s %s' % (
                             op.join(wm_exchange_folder, 'wm_corrected.nii.gz'),
                             op.join(gconf.get_fs(), 'mri', 'wm.mgz') ) 
    runCmd( mri_cmd, log )
    
    if not op.exists(op.join(gconf.get_fs(), 'mri', 'wm.mgz')):
        log.error("Unable to convert wm_corrected.nii.gz to the file '/mri/wm.mgz' for this subject!")

    log.info("[ DONE ]")

def run_fs_on_corrected_wm():
    log.info("Running FREESURFER on the corrected 'wm.mgz' file")
    log.info("=================================================")
        
    environ['SUBJECTS_DIR'] = gconf.get_subj_dir()
    
    fs_cmd = 'recon-all -s %s -autorecon2-wm -autorecon3 -no-isrunning' % 'FREESURFER'
    runCmd( fs_cmd, log )
    
    log.info("[ DONE ]")

def cleanup_symlinks():
    """ Cleans up created symlinks by the recon-all commands """
    
    log.info("Remove symbolic links that were created by recon-all")

    subjdir = gconf.get_subj_dir()
    
    paths = ['fsaverage', 'lh.EC_average', 'rh.EC_average']
    
    for f in paths:
        pa = op.join(subjdir, f)
        if op.exists(pa):
            # remove the symlinks
            os.remove(pa)

def inspect(gconf):
    """ Inspect the results of this stage """
    log = gconf.get_logger()
    # updating the environment
    environ['SUBJECTS_DIR'] = gconf.get_subj_dir()

    fscmd = 'tkmedit FREESURFER brainmask.mgz -aux T1.mgz -surfs'
    runCmd( fscmd, log )

    fscmd = 'tkmedit FREESURFER norm.mgz -segmentation aseg.mgz %s/FreeSurferColorLUT.txt' % gconf.freesurfer_home
    runCmd( fscmd, log )

def run(conf):
    """ Run the freesurfer step
    
    Parameters
    ----------
    conf : PipelineConfiguration object
        
    """
    # setting the global configuration variable
    globals()['gconf'] = conf
    globals()['log'] = gconf.get_logger() 
    start = time()
    
    log.info("Running the FREESURFER module")
    log.info("=============================")
    
    if gconf.wm_handling == 1:
        copy_orig_to_fs()
        recon_all()
    elif gconf.wm_handling == 2:
        before_wm_corr()
        msg = 'You can now correct the white matter for subject '
        raise Exception(msg)
    elif gconf.wm_handling == 3:
        after_wm_corr()
        run_fs_on_corrected_wm()
        
    cleanup_symlinks()

    if not len(gconf.emailnotify) == 0:        
        msg = "Freesurfer module finished!\nIt took %s seconds." % int(time()-start)
        send_email_notification(msg, gconf, log)
          
def declare_inputs(conf):
    """Declare the inputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)
    nifti_dir = conf.get_nifti()    

    conf.pipeline_status.AddStageInput(stage, nifti_dir, 'T1.nii.gz', 't1-nii-gz')
    
def declare_outputs(conf):
    """Declare the outputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)
    nifti_dir = conf.get_nifti()
    fs_dir = conf.get_fs()

    # Freesurfer outputs a lot of files, declaring some key outputs here that are used
    # by subsequent stages.  Others could be added...
    hemispheres = [ 'rh', 'lh' ]
    for hemi in hemispheres:
        conf.pipeline_status.AddStageOutput(stage, op.join(fs_dir, 'surf'), '%s.sphere.reg' % (hemi), '%s.sphere-reg' % (hemi))
        
    conf.pipeline_status.AddStageOutput(stage, op.join(fs_dir, 'mri'), 'aseg.mgz', 'aseg-mgz')
            
