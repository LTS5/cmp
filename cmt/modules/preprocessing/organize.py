import os, os.path as op
import sys
from time import time
from ...logme import *
    
def log_system_setup():
    
    uname_cmd = 'uname -a'
    runCmd( uname_cmd, log )
    
    # freesurfer version
    rec_cmd = 'recon-all --version'
    runCmd( rec_cmd, log )
    
    # fsl version
    fsl_cmd = 'flirt -version'
    runCmd( fsl_cmd, log )
    
    # dtk version
    odf_cmd = 'odf_recon -h'
#    runCmd( odf_cmd, log )
    
def create_folders():
    
    paths = [
        gconf.get_nifti4subject(sid),
        gconf.get_fs4subject(sid),
        gconf.get_cmt_tracto_mask(sid),
        gconf.get_cmt_tracto_mask_tob0(sid),
        gconf.get_cmt_fibers4subject(sid),  
        gconf.get_log4subject(sid),
        gconf.get_rawt14subject(sid),
        gconf.get_raw_diffusion4subject(sid),
        gconf.get_cmt_scalars4subject(sid),
        gconf.get_cmt_matrices4subject(sid),
        op.join(gconf.get_cmt_rawdiff4subject(sid), '2x2x2'),
        op.join(gconf.get_cmt_rawdiff4subject(sid), 'odf_0'),
        op.join(gconf.get_nifti4subject(sid), 'wm_correction'),
        op.join(gconf.get_fs4subject(sid), 'mri', 'orig')
        ]

    if gconf.registration_mode == 'N':
        paths.append(gconf.get_rawt24subject(sid))

    for p in gconf.parcellation.keys():
        paths.append(op.join(op.join(gconf.get_cmt_fsout4subject(sid), 'registred', 'HR'), p))
        
    for park, parv in gconf.parcellation.items():
        paths.append(op.join(op.join(gconf.get_cmt_fsout4subject(sid), 'registred', 'HR__registered-TO-b0'), park))

    for p in paths:
        if not op.exists(p):
            try:
                os.makedirs(p)
            except os.error:
                log.info("%s was already existing" % p)
            finally:
                log.info("Created directory %s" % p)
     
def set_env_vars():
    
    os.environ['FSLOUTPUTTYPE'] = 'NIFTI'
    
def log_paths():
    
    log.info("CMT path configuration:")

    log.info(gconf.freesurfer_home)
    log.info(gconf.fsl_home)
    log.info(gconf.dtk_home)
    log.info(gconf.dtk_matrices)
    log.info(gconf.matlab_home)
    log.info(gconf.matlab_bin)
    log.info(gconf.matlab_prompt)


def run(conf, subject_tuple):
    """ Run the first preprocessing step
    
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
    
    log.info("Preprocessing")
    log.info("=============")

    log_system_setup()
    create_folders()
    set_env_vars()
    log_paths()
    
    # consistency check the configuration
    gconf.consistency_check()
    
    log.info("Module took %s seconds to process." % (time()-start))
    
    if not len(gconf.emailnotify) == 0:
        msg = "Preprocessing module finished!\nIt took %s seconds." % int(time()-start)
        send_email_notification(msg, gconf.emailnotify, log)
    