import os, os.path as op
import logging
log = logging.getLogger()
from glob import glob
import subprocess
import sys

def regT12b0():
    log.info("T1 -> b0 (LINEAR/NONLINEAR) registration in one time-point")
    
    if gconf.reg_mode == 'N':
        log.info("STEP 1c: T1 -> T2 -> b0 NONLINEAR registration")
    
        # take result display
        
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
    
        log.info("[ DONE ]")
    else:
        log.info("STEP 1c: T1 -> b0 LINEAR registration")
    
        # "${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 3b "${MY_SUBJECT}" "${MY_TP}"
    
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
    
    regT12b0()
    