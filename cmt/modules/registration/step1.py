import os, os.path as op
from glob import glob
from time import time
import subprocess
import sys
from ...logme import *

def nlin_regT12b0():
    log.info("T1 -> b0: Non-linear registration")
    log.info("=================================")
       
        # XXX: take result display
        
#            # LINEAR register T1 --> b0
#            "${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 3a "${MY_SUBJECT}" "${MY_TP}" 1.1
#            "${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 3a "${MY_SUBJECT}" "${MY_TP}" 1.2
#            "${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 3a "${MY_SUBJECT}" "${MY_TP}" 1.3
#    
#            # Create BINARY MASKS needed for nonlinear registration
#            "${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 3a "${MY_SUBJECT}" "${MY_TP}" 2.1 0.2 0.3        # T2 mask
#            "${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 3a "${MY_SUBJECT}" "${MY_TP}" 2.2 0.2 0.2        # b0 mask
#    
#            # NONLINEAR register T1 --> b0
#            "${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 3a "${MY_SUBJECT}" "${MY_TP}" 3
    

def lin_regT12b0():
    log.info("T1 -> b0: Linear registration")
    log.info("=============================")


    # Linear register "T1" onto "b0_resampled"
    log.info("Started FLIRT to find 'T1 --> b0' linear transformation")

    # rm -f "T1-TO-b0".*
    if not gconf.mode_parameters.has_key('lin_reg_para'):
        param = '-usesqform -nosearch -dof 6 -cost mutualinfo'
    else:
        param = gconf.mode_parameters['lin_reg_para']
        
    flirt_cmd = 'flirt -in %s -ref %s -out %s -omat %s %s' % (
            op.join(gconf.get_nifti4subject(sid), 'T1.nii'),
            op.join(gconf.get_nifti4subject(sid), 'DSI_b0_resampled.nii'),
            op.join(gconf.get_nifti4subject(sid), 'T1-TO-b0.nii'),
            op.join(gconf.get_nifti4subject(sid), 'T1-TO-b0.mat'),
            param)
    
    runCmd(flirt_cmd, log)
    
    if not op.exists(op.join(gconf.get_nifti4subject(sid), 'T1-TO-b0.mat')):
        msg = "An error occurred. Linear transformation file %s not generated." % op.join(gconf.get_nifti4subject(sid), 'T1-TO-b0.mat')
        log.error(msg)
        raise Exception(msg)

    # check the results
    if gconf.inspect_registration:
        log.info("FLIRT has finished. Check the result with FSLVIEW.")        
        fsl_view_cmd = 'fslview %s %s -l Copper -t 0.5' % (op.join(gconf.get_nifti4subject(sid), 'DSI_b0_resampled.nii'),
                                                           op.join(gconf.get_nifti4subject(sid), 'T1-TO-b0.nii') )
        runCmd( fsl_view_cmd, log )
    
    log.info("[ DONE ]")


def run(conf, subject_tuple):
    """ Run the first registration step
    
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
        nlin_regT12b0()
    else:
        lin_regT12b0()
    
    log.info("Module took %s seconds to process." % (time()-start))