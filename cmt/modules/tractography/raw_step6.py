import os, os.path as op
import logging as log
from glob import glob
import subprocess

cmt_home = os.path.join(os.environ['CMT_HOME'])
cmt_bin = op.join(cmt_home, 'c++', 'bin')
raw_diffusion = op.join(subject_dir, '4__CMT', 'raw_diffusion')
fs_output_dir = op.join(subject_dir, '4__CMT', 'fs_output')
fs_mask_dir = op.join(fs_output_dir, 'registred', 'HR__registered-TO-b0')
fibers_path = os.mkdirs(op.join(subject_dir, '4__CMT', 'fibers'))


log("STEP 6a: run STREAMLINE tractography")

# convert WM MASK to 8 bit/pixel

proc = subprocess.Popen(['fslmaths','fsmask_1mm.nii', \
                                    'fsmask_1mm__8bit.nii', \
                                    '-odt char'],
                            cwd = fs_mask_dir,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

# perform fiber-tracking
# XXX: rm "fibers/streamline.trk" &> /dev/null

if len(sharpness) == 1:
    # normal streamline
    proc = subprocess.Popen(['DTB_streamline', \
                             "--odf %s" % op.join(raw_diffusion, 'odf_0', 'dsi_'),
                             "--angle 60",
                             "--wm %s" % op.join(fs_mask_dir, 'fsmask_1mm__8bit.nii'),
                             "--rSeed 4",
                             "--out %s" % op.join(fibers_path, 'streamline')],
                             cwd = fibers_path,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
else:
    # streamline with 2 ODFs
    for ele in sharpness:
        proc = subprocess.Popen(['DTB_streamline', \
                                 "--odf %s" % op.join(raw_diffusion, 'odf_%s' % str(ele), 'dsi_'),
                                 "--angle 45",
                                 "--odf2 %s" % op.join(raw_diffusion, 'odf_0', 'dsi_'),
                                 "--angle2 60",
                                 "--wm %s" % op.join(fs_mask_dir, 'fsmask_1mm__8bit.nii'),
                                 "--rSeed 4",
                                 "--out %s" % op.join(fibers_path, 'streamline')],
                                 cwd = fibers_path,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
    
if not os.exists(op.join(fibers_path, 'streamline.trk')):
    log.error('No streamline.trk created')    

# XXX: rm "${DATA_path}/${MY_SUBJECT}/${MY_TP}/4__CMT/fs_output/registred/HR__registered-TO-b0/fsmask_1mm__8bit.nii"
log.info("[ DONE ]")

# SPLINE filtering
log.info("STEP 6b: spline filtering the fibers")
proc = subprocess.Popen(['spline_filter','streamline.trk"', '1', "tmp.trk" ],
                            cwd = fibers_path,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)   
os.rename(op.join(fibers_path, "tmp.trk"), op.join(fibers_path, "streamline.trk"))
log.info("[ DONE ]")