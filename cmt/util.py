import os, os.path as op
import shutil
import subprocess
import numpy as np
from logme import *
from enthought.traits.api import HasStrictTraits, Str
    
class KeyValue(HasStrictTraits):
    key = Str
    value = Str
    
def mymove(src, dst, log, copy = False):
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
    
    if copy:
        log.info("Copy file %s to %s" % (src, dst))
        shutil.copy(src, dst)
    else:
        log.info("Move file %s to %s" % (src, dst))
        shutil.move(src, dst)

def myrename(src, dst, log):
    log.info("Rename %s to %s" % (src, dst))
    os.rename(src, dst)

def get_orient(path, fsl = False):
    
    if fsl:
        cmd = 'fslorient -getorient "%s"' % path
        proc = subprocess.Popen(cmd,
                           shell=True,
                           stdout=subprocess.PIPE,
                           )
        stdout_value = proc.communicate()[0].strip()        
    else:        
        cmd = 'mri_info --orientation "%s"' % path
        proc = subprocess.Popen(cmd,
                           shell=True,
                           stdout=subprocess.PIPE,
                           )
        stdout_value = proc.communicate()[0].strip()
    return stdout_value
    
    
def reorient(src, ref, log):
    """ Reorients the src to match the ref orientation """
    
    # read orientations of all datasets
    log.info("Changing orientation %s to match %s" % (src, ref) )

    src_orient = get_orient(src)
    ref_orient = get_orient(ref)
    src_conv = get_orient(src, True)
    ref_conv = get_orient(ref, True)
    
    log.info("Input dataset has %s orientation" % src_orient)
    log.info("Reference dataset has %s orientation" % ref_orient)
    
    # if needed, match orientation to reference
    if src_orient == ref_orient:
        log.info("No reorientation needed")
        return
    else:
        log.info("src has conv %s and ref has conv %s" % (src_conv, ref_conv))
        if src_conv != ref_conv:
            # if needed, match convention (radiological/neurological) to reference
            # copy src
            csrc = op.join(op.dirname(src),'orig-orient-' +  op.basename(src))
            tmpsrc = op.join(op.dirname(src), 'temp-' + op.basename(src))
            shutil.move(src, csrc)
            log.info("Backup file written to %s" % csrc)
        
            fsl_cmd = 'fslswapdim "%s" -x y z "%s"' % (csrc, tmpsrc)
            runCmd( fsl_cmd, log )
        
            fsl_cmd = 'fslorient -swaporient "%s"' % tmpsrc
            runCmd( fsl_cmd, log )
        else:
            # If conventions match, just use the original source
            tmpsrc = src
            
    tmp2 = op.join(op.dirname(src), 'tmp.nii')
    
    if ref_orient == 'LPS':
        fsl_cmd = 'fslswapdim "%s" RL AP IS "%s"' % (tmpsrc, tmp2)
        runCmd( fsl_cmd, log )
    elif ref_orient == 'LPI':
        fsl_cmd = 'fslswapdim "%s" RL AP SI "%s"' % (tmpsrc, tmp2)
        runCmd( fsl_cmd, log )        
    else:
        log.error('%s orientation %s not yet supported. Please orient source images by yourself.' % (tmpsrc, ref_orient))
        return
    
    shutil.move(tmp2, src)
    
    log.info("File %s written" % src)    

def DTB_viewer():
    """ Run the DTB Viewer """
    #XXX
    pass

# The function length is kindly contributed from the Diffusion in Python Project
# http://www.nipy.org/dipy
# 2010, Eleftherios Garyfallidis

def length(xyz, along=False):
    ''' Euclidean length of track line

    Parameters
    ----------
    xyz : array-like shape (N,3)
       array representing x,y,z of N points in a track
    along : bool, optional
       If True, return array giving cumulative length along track,
       otherwise (default) return scalar giving total length.

    Returns
    -------
    L : scalar or array shape (N-1,)
       scalar in case of `along` == False, giving total length, array if
       `along` == True, giving cumulative lengths.

    Examples
    --------
    >>> xyz = np.array([[1,1,1],[2,3,4],[0,0,0]])
    >>> expected_lens = np.sqrt([1+2**2+3**2, 2**2+3**2+4**2])
    >>> length(xyz) == expected_lens.sum()
    True
    >>> len_along = length(xyz, along=True)
    >>> np.allclose(len_along, expected_lens.cumsum())
    True
    >>> length([])
    0
    >>> length([[1, 2, 3]])
    0
    >>> length([], along=True)
    array([0])
    '''
    xyz = np.asarray(xyz)
    if xyz.shape[0] < 2:
        if along:
            return np.array([0])
        return 0
    dists = np.sqrt((np.diff(xyz, axis=0)**2).sum(axis=1))
    if along:
        return np.cumsum(dists)
    return np.sum(dists)
