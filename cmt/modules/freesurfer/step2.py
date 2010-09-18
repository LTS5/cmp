import os, os.path as op
import logging
log = logging.getLogger()
from glob import glob
import subprocess

def copy_orig_to_fs():
    
    log.info("STEP 2a: copying '2__NIFTI/T1.nii' dataset to '3__FREESURFER/mri/orig/001.mgz'...")

    if not op.exists(op.join(gconf.get_nifti4subject(sid), 'T1.nii')):
        log.error("File T1.nii does not exists in subject directory")
    
    fs_4subj_mri = op.join(gconf.get_fs4subject(sid), 'mri', 'orig')
    try:
        os.makedirs(fs_4subj_mri)
    except os.error:
        log.info("%s was already existing" % str(fs_4subj_mri))

        
    # XXX rm -f "${DATA_path}/${MY_SUBJECT}/${MY_TP}/3__FREESURFER/mri/orig/001.mgz"
    log.info("Starting mri_convert ...")
    proc = subprocess.Popen(['mri_convert %s %s' % ( 
                             op.join(gconf.get_nifti4subject(sid), 'T1.nii'),
                             op.join(gconf.get_fs4subject(sid), 'mri', 'orig', '001.mgz') )],
                            cwd = gconf.get_subj_dir(sid),
                            shell = True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    
    out, err = proc.communicate()
    log.info(out)
        
    if not op.exists(op.join(gconf.get_fs4subject(sid), 'mri', 'orig', '001.mgz')):
        log.error("File 001.mgz has to been generated.")

    log.info("[ DONE ]")


def recon_all():
    log.info("STEP 2b: running the whole FREESURFER pipeline")

    from os import environ
    env = environ
    env['SUBJECTS_DIR'] = gconf.get_subj_dir(sid)
    
    log.info("Starting recon-all ...")
    proc = subprocess.Popen(['recon-all -s %s -all -no-isrunning' % '3__FREESURFER'],
                            cwd = gconf.get_fs4subject(sid),
                            shell = True,
                            stdout=subprocess.PIPE, # XXX &> "${LOGDIR}/freesurfer.log"
                            stderr=subprocess.PIPE,
                            env = env)
    
    out, err = proc.communicate()
    log.info(out)
    
    log.info("[ DONE ]")
    

def before_wm_corr():
    log.info("STEP 2c: copy stuff for correcting the 'wm mask' ");

    if not op.exists(op.join(gconf.get_fs4subject(sid), 'mri', 'T1.mgz')):
        log.error('/mir/T1.mgz does not exists in subject folder')
    if not op.exists(op.join(gconf.get_fs4subject(sid), 'mri', 'wm.mgz')):
        log.error('/mir/wm.mgz does not exists in subject folder')

    wm_exchange_folder = op.join(gconf.get_nifti4subject(sid), 'wm_correction')
    if not op.exists(wm_exchange_folder):
        try:
            wm_exchange_folder = os.makedirs(wm_exchange_folder)
        except os.error:
            log.info("%s was already existing" % str(wm_exchange_folder))
    
    # XXX rm -f "${WM_EXCHANGE_FOLDER}/${MY_SUBJECT}/${MY_TP}/T1.nii"
    # XXX rm -f "${WM_EXCHANGE_FOLDER}/${MY_SUBJECT}/${MY_TP}/wm.nii"

    log.info("Starting mri_convert ...")
    proc = subprocess.Popen(['mri_convert %s %s' % ( 
                             op.join(gconf.get_fs4subject(sid), 'mri', 'T1.mgz'),
                             op.join(wm_exchange_folder, 'T1.nii') )],
                            cwd = gconf.get_subj_dir(sid),
                            shell = True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    
    out, err = proc.communicate()
    log.info(out)
    
    log.info("Starting mri_convert ...")
    proc = subprocess.Popen(['mri_convert %s %s' % ( 
                             op.join(gconf.get_fs4subject(sid), 'mri', 'wm.mgz'),
                             op.join(wm_exchange_folder, 'wm.nii') )],
                            cwd = gconf.get_subj_dir(sid),
                            shell = True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
        
    out, err = proc.communicate()
    log.info(out)
    
    log.info("You can now correct the white matter mask stored in %s " % op.join(wm_exchange_folder, 'wm.nii'))
    log.info("After correction, store it in the same folder with the name wm_corrected.nii")    
        
    if not op.exists(op.join(wm_exchange_folder, 'T1.nii')):
        log.error("Unable to convert the file '/mri/T1.mgz' for subject!")

    if not op.exists(op.join(wm_exchange_folder, 'wm.nii')):
        log.error("Unable to convert the file '/mri/wm.mgz' for subject!")

    log.info("[ DONE ]")

def after_wm_corr():

    log.info("STEP 2d: copying back the corrected 'wm mask' " );
    
    wm_exchange_folder = op.join(gconf.get_nifti4subject(sid), 'wm_correction')
    
    if not op.exists(op.join(wm_exchange_folder, 'wm_corrected.nii')):
        log.error('Need to provide a corrected white matter mask wm_corrected.nii in %s' % wm_exchange_folder)

    # XXX rm -f "${DATA_path}/${MY_SUBJECT}/${MY_TP}/3__FREESURFER/mri/wm.mgz"
    
    log.info("Starting mri_convert ...")
    proc = subprocess.Popen(['mri_convert -odt uchar %s %s' % (
                             op.join(wm_exchange_folder, 'wm_corrected.nii'),
                             op.join(gconf.get_fs4subject(sid), 'mri', 'wm.mgz') ) ],
                            cwd = gconf.get_subj_dir(sid),
                            shell = True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    
    out, err = proc.communicate()
    log.info(out)
    
    if not op.exists(op.join(gconf.get_fs4subject(sid), 'mri', 'wm.mgz')):
        log.error("Unable to convert wm_corrected.nii to the file '/mri/wm.mgz' for this subject!")

    log.info("[ DONE ]")

def run_fs_on_corrected_wm():
    log.info("STEP 2d: running FREESURFER on the corrected 'wm.mgz' file")
        
    from os import environ
    env = environ
    env['SUBJECTS_DIR'] = gconf.get_subj_dir(sid)
    
    log.info("Starting recon-all ... (last part)")
    proc = subprocess.Popen(['recon-all -s %s -autorecon2-wm -autorecon3 -no-isrunning' % '3__FREESURFER'],
                            cwd = gconf.get_fs4subject(sid),
                            shell = True,
                            stdout=subprocess.PIPE, # XXX &> "${LOGDIR}/freesurfer.log"
                            stderr=subprocess.PIPE)

    out, err = proc.communicate()
    log.info(out)
    
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
    globals()['gconf'] = conf
    globals()['sid'] = subject_tuple

    if gconf.wm_handling == 1:
        copy_orig_to_fs()
        recon_all()
    elif gconf.wm_handling == 2:
        before_wm_corr()
    elif gconf.wm_handling == 3:
        after_wm_corr()
        run_fs_on_corrected_wm()
        