import os, os.path as op
from time import time
from ...logme import *

# input: trackfile and grey matter mask

def find_clusters():
    try:
        import dipy.core
    except ImportError:
        log.info("Cannot import DiPy")
        
    log.info("DiPy clustering not included in the current release.")
        

def create_connectionbased_parcellation():
    pass
    # idea:
    # each bundle defines 2 ROIs
    # number of connection of fibers /ROIs
        # segment ROIs (according to number of connection fibers)
    # could find anatomical labeling using a standardized atlas

def run(conf, subject_tuple):
    """ Run the fiber clustering
    
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
    
    find_clusters()
    
    log.info("Module took %s seconds to process." % (time()-start))
    
    if not len(gconf.emailnotify) == 0:
        msg = "Fiber clustering module finished!\nIt took %s seconds." % int(time()-start)
        send_email_notification(msg, gconf.emailnotify, log)
        