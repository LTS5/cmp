import os, os.path as op
import shutil

def mymove(src, dst, log):
    """ Custom move function with target checking and logging """
    
    if not op.exists(src):
        log.error("Source does not exist: %s" % src)
        return
    
    if op.exists(dst):
        ndst = dst + '_OLD'
        log.debug("Target file already exists. Rename it to %s" % ndst)
        if op.exists(dst):
            if op.isfile(dst):
                shutil.move(dst,ndst)
    
    log.info("Copy file %s to %s" % (src, dst))
    shutil.copy(src, dst)