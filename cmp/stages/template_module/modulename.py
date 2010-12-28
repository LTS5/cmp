""" This is a template module to describe the basic scaffold for new modules """

import os, os.path as op
import sys
from time import time
from ...logme import *

def process_function():
    
    print "Here you define your processing ..."

def run(conf):
    """ Run the NONAME module
    
    Parameters
    ----------
    conf : PipelineConfiguration object
        
    """
    # setting the global configuration variable
    globals()['gconf'] = conf
    globals()['log'] = gconf.get_logger() 
    start = time()
    
    log.info("NONAME MODULE")
    log.info("=============")

    process_function()
    
    log.info("Module took %s seconds to process." % (time()-start))
    
    if not len(gconf.emailnotify) == 0:
        msg = ["NONAME", int(time()-start)]
        send_email_notification(msg, gconf, log)
