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
    pass

    nifti_dir = op.join(gconf.get_nifti4subject(sid))
    if not op.exists(nifti_dir):
        try:
            os.makedirs(nifti_dir)
        except os.error:
            log.info("%s was already existing" % str(nifti_dir))

    res_dsi_dir = op.join(gconf.get_cmt_rawdiff4subject(sid), '2x2x2') 
    if not op.exists(res_dsi_dir):
        try:
            os.makedirs(res_dsi_dir)
        finally:
            log.info("Created directory %s" % res_dsi_dir)
            
    odf_out_path = op.join(gconf.get_cmt_rawdiff4subject(sid), 'odf_0')
    try:
        os.makedirs(odf_out_path)
    except os.error:
        log.info("%s was already existing" % str(odf_out_path))
        
    fs_4subj_mri = op.join(gconf.get_fs4subject(sid), 'mri', 'orig')
    try:
        os.makedirs(fs_4subj_mri)
    except os.error:
        log.info("%s was already existing" % str(fs_4subj_mri))
        
    wm_exchange_folder = op.join(gconf.get_nifti4subject(sid), 'wm_correction')
    if not op.exists(wm_exchange_folder):
        try:
            wm_exchange_folder = os.makedirs(wm_exchange_folder)
        except os.error:
            log.info("%s was already existing" % str(wm_exchange_folder))

    reg_path = op.join(gconf.get_cmt_fsout4subject(sid), 'registred', 'HR')
    try:
        os.makedirs(reg_path)
    except:
        pass
    
    for p in gconf.parcellation.keys():
        log.info("Create path %s" % p )
        try:
            os.makedirs(op.join(reg_path, p))
        except:
            pass
        
    tracto_masks_path_out = op.join(gconf.get_cmt_fsout4subject(sid), 'registred', 'HR__registered-TO-b0')
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
        
    fibers_path = gconf.get_cmt_fibers4subject(sid)        
    if not op.exists(fibers_path):
        os.makedirs(fibers_path)
        
    if not op.exists(gconf.get_log4subject(sid)):
        os.makedirs(gconf.get_log4subject(sid))
        
    
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
                