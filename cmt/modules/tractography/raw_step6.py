import os, os.path as op
import logging as log
from glob import glob
import subprocess

global gconf
global sid

def convert_wm_mask():
    log("convert WM MASK to 8 bit/pixel")
    
    proc = subprocess.Popen(['fslmaths','fsmask_1mm.nii', \
                                        'fsmask_1mm__8bit.nii', \
                                        '-odt char'],
                                cwd = gconf.get_cmt_fsmask4subject(sid),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    log.info("[ DONE ]")
    

def fiber_tracking():
    
    log("STEP 6a: run STREAMLINE tractography")
    # XXX: rm "fibers/streamline.trk" &> /dev/null
    
    fibers_path = os.makedirs(gconf.get_cmt_fibers4subject(sid))
    
    if len(gconf.sharpness) == 1:
        # normal streamline
        proc = subprocess.Popen(['DTB_streamline', \
                                 "--odf %s" % op.join(gconf.get_cmt_rawdiff4subject(sid), 'odf_0', 'dsi_'),
                                 "--angle 60",
                                 "--wm %s" % op.join(gconf.get_cmt_fsmask4subject(sid), 'fsmask_1mm__8bit.nii'),
                                 "--rSeed 4",
                                 "--out %s" % op.join(gconf.get_cmt_fibers4subject(sid), 'streamline')],
                                 cwd = gconf.get_cmt_fibers4subject(sid),
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
    else:
        # streamline with 2 ODFs
        for ele in gconf.sharpness:
            proc = subprocess.Popen(['DTB_streamline', \
                                     "--odf %s" % op.join(gconf.get_cmt_rawdiff4subject(sid), 'odf_%s' % str(ele), 'dsi_'),
                                     "--angle 45",
                                     "--odf2 %s" % op.join(gconf.get_cmt_rawdiff4subject(sid), 'odf_0', 'dsi_'),
                                     "--angle2 60",
                                     "--wm %s" % op.join(gconf.get_cmt_fsmask4subject(sid), 'fsmask_1mm__8bit.nii'),
                                     "--rSeed 4",
                                     "--out %s" % op.join(gconf.get_cmt_fibers4subject(sid), 'streamline')],
                                     cwd = gconf.get_cmt_fibers4subject(sid),
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        
    if not os.exists(op.join(gconf.get_cmt_fibers4subject(sid), 'streamline.trk')):
        log.error('No streamline.trk created')    
    
    # XXX: rm "${DATA_path}/${MY_SUBJECT}/${MY_TP}/4__CMT/fs_output/registred/HR__registered-TO-b0/fsmask_1mm__8bit.nii"
    log.info("[ DONE ]")


def spline_filtering():
    log.info("STEP 6b: spline filtering the fibers")
    proc = subprocess.Popen(['spline_filter','streamline.trk"', '1', "tmp.trk" ],
                                cwd = gconf.get_cmt_fibers4subject(sid),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)   
    os.rename(op.join(gconf.get_cmt_fibers4subject(sid), "tmp.trk"), op.join(gconf.get_cmt_fibers4subject(sid), "streamline.trk"))
    log.info("[ DONE ]")


def run(conf, subject_tuple):
    """ Run the tractography step
    
    Parameters
    ----------
    conf : PipelineConfiguration object
    subject_tuple : tuple, (subject_id, timepoint)
        Process the given subject
        
    """
    # setting the global configuration variable
    gconf = conf
    sid = subject_tuple
    
    convert_wm_mask()
    fiber_tracking()
    spline_filtering()
    