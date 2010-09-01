import os, os.path as op
import logging as log
from glob import glob
import subprocess

global gconf
global sid

def copy_orig_to_fs():
    
    log.info("STEP 2a: copying '2__NIFTI/T1.nii' dataset to '3__FREESURFER/mri/orig/001.mgz'...")

    if not os.exists(op.join(gconf.get_nifti4subject(sid), 'T1.nii')):
        log.error("File T1.nii does not exists in subject directory")
        
    
    # XXX rm -f "${DATA_path}/${MY_SUBJECT}/${MY_TP}/3__FREESURFER/mri/orig/001.mgz"
    proc = subprocess.Popen(['mri_convert', 
                             op.join(gconf.get_nifti4subject(sid), 'T1.nii'),
                             op.join(gconf.get_fs4subject(sid), 'mri', 'orig', '001.mgz')],
                            cwd = gconf.subject_list[sid],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
                        
    if not os.exists(op.join(gconf.get_fs4subject(sid), 'mri', 'orig', '001.mgz')):
        log.error("File 001.mgz has to been generated.")

    log.info("[ DONE ]")


def recon_all():
    log.info("STEP 2b: running the whole FREESURFER pipeline")

    proc = subprocess.Popen(['recon-all',
                             '-s %s' % gconf.get_fs4subject(sid),
                             '-all',
                             '-no-isrunning'],
                            cwd = gconf.get_fs4subject(sid),
                            stdout=subprocess.PIPE, # XXX &> "${LOGDIR}/freesurfer.log"
                            stderr=subprocess.PIPE)
    
    log.info("[ DONE ]")
    

def before_wm_corr():
    log.info("STEP 2c: copy stuff for correcting the 'wm mask' to %s" % gconf.wm_exchange_folder);

    if not os.exists(op.join(gconf.get_fs4subject(sid), 'mri', 'T1.mgz')):
        log.error('/mir/T1.mgz does not exists in subject folder')
    if not os.exists(op.join(gconf.get_fs4subject(sid), 'mri', 'wm.mgz')):
        log.error('/mir/wm.mgz does not exists in subject folder')

    try:
        wm_exchange_folder = os.makedirs(op.join(gconf.wm_exchange_folder, sid))
    except os.error:
        log.info("%s was already existing" % str(wm_exchange_folder))
    
    # XXX rm -f "${WM_EXCHANGE_FOLDER}/${MY_SUBJECT}/${MY_TP}/T1.nii"
    # XXX rm -f "${WM_EXCHANGE_FOLDER}/${MY_SUBJECT}/${MY_TP}/wm.nii"

    proc = subprocess.Popen(['mri_convert', 
                             op.join(gconf.get_fs4subject(sid), 'mri', 'T1.mgz'),
                             op.join(wm_exchange_folder, sid, 'T1.nii')],
                            cwd = gconf.subject_list[sid],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    proc = subprocess.Popen(['mri_convert', 
                             op.join(gconf.get_fs4subject(sid), 'mri', 'wm.mgz'),
                             op.join(wm_exchange_folder, sid, 'wm.nii')],
                            cwd = gconf.subject_list[sid],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
        
    if not os.exists(op.join(wm_exchange_folder, sid, 'T1.nii')):
        log.error("Unable to convert the file '/mri/T1.mgz' for subject!")

    if not os.exists(op.join(wm_exchange_folder, sid, 'wm.nii')):
        log.error("Unable to convert the file '/mri/wm.mgz' for subject!")

    log.info("[ DONE ]")

def after_wm_corr():

    log.info("STEP 2d: copying back the corrected 'wm mask' from %s" % gconf.wm_exchange_folder);
    
    wm_exchange_folder = op.join(gconf.wm_exchange_folder, sid)
    
    if not os.exists(op.join(wm_exchange_folder, 'wm_corrected.nii')):
        log.error('Need to provide a corrected white matter mask wm_corrected.nii in %s' % (wm_exchange_folder))

    # XXX rm -f "${DATA_path}/${MY_SUBJECT}/${MY_TP}/3__FREESURFER/mri/wm.mgz"

    proc = subprocess.Popen(['mri_convert', 
                             '-odt uchar',
                             op.join(wm_exchange_folder, 'wm_corrected.nii'),
                             op.join(gconf.get_fs4subject(sid), 'mri', 'wm.mgz')],
                            cwd = gconf.subject_list[sid],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    
    if not os.exists(op.join(wm_exchange_folder, sid, 'wm.nii')):
        log.error("Unable to convert wm_corrected.nii to the file '/mri/wm.mgz' for subject!")

    log.info("[ DONE ]")

def run_fs_on_corrected_wm():
    log.info("STEP 2d: running FREESURFER on the corrected 'wm.mgz' file")
    
    proc = subprocess.Popen(['recon-all',
                             '-s %s' % gconf.get_fs4subject(sid),
                             '-autorecon2-wm',
                             '-autorecon3'
                             '-no-isrunning'],
                            cwd = gconf.get_fs4subject(sid),
                            stdout=subprocess.PIPE, # XXX &> "${LOGDIR}/freesurfer.log"
                            stderr=subprocess.PIPE)
    
    log.info("[ DONE ]")


def run(conf, subject_tuple):
    """ Run the freesurfer step
    
    Parameters
    ----------
    conf : PipelineConfiguration object
    subject_tuple : tuple, (subject_id, timepoint)
        Process the given subject
        
    """
    # setting the global configuration variable
    gconf = conf
    sid = subject_tuple

    if gconf.do_manual_wm_correction:
        before_wm_corr()
        after_wm_corr()
        run_fs_on_corrected_wm()
        