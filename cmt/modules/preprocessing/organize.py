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
        op.join(gconf.get_nifti4subject(sid)),
        op.join(gconf.get_cmt_rawdiff4subject(sid), '2x2x2'),
        op.join(gconf.get_cmt_rawdiff4subject(sid), 'odf_0'),
        gconf.get_fs4subject(sid),
        op.join(gconf.get_nifti4subject(sid), 'wm_correction'),
        op.join(gconf.get_cmt_fsout4subject(sid), 'registred', 'HR__registered-TO-b0'),
        gconf.get_cmt_fibers4subject(sid),  
        gconf.get_log4subject(sid),
        gconf.get_rawt14subject(sid),
        gconf.get_raw_diffusion4subject(sid),
        gconf.get_cmt_scalars4subject(sid),
        op.join(gconf.get_cmt_fsout4subject(sid), 'registred', 'HR')]

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

    log.info("Module took %s seconds to process." % (time()-start))
                