# See http://www.mit.edu/~satra/nipype-nightly/interfaces/generated/nipype.interfaces.freesurfer.preprocess.html
#########################################################################################################################################
#######################################################  FREESURFER  ####################################################################
#########################################################################################################################################


# Copy the 'ORIGINAL T1' to FREESURFER
############
# this is a file move operation, how to adapt it sensibly so that
# freesurfer uses the original t1.nii file in its .mgz format ?
# we can use T1_files below?

# ---  ALL FREESURFER PIPELINE  ---
############
# http://www.mit.edu/~satra/nipype-nightly/interfaces/generated/nipype.interfaces.freesurfer.preprocess.html#reconall
# recon-all -s "3__FREESURFER" -all -no-isrunning &> "${LOGDIR}/freesurfer.log"

# export SUBJECTS_DIR="${DATA_path}/${MY_SUBJECT}/${MY_TP}"        # force FREESURFER to work in a different folder (leave unchanged)

from nipype.interfaces.freesurfer import ReconAll

reconall = ReconAll()

reconall.inputs.subjects_dir = '.'
# could be pjoin(cmt_home, data_dir, project, subject_dir, timepoint_dir)
reconall.inputs.subject_id = 'foo'
# and subject_id = '3__FREESURFER'
# what about workingdir?

reconall.inputs.directive = 'all'
reconall.inputs.args = '-no-isrunning'
# what does reconall nodes to with this?
reconall.inputs.T1_files = 'T1.nii'


# How to deal with manual wm mask corrections?
# this goes in principle against automation, but it is necessary, is it?

# ---  BEFORE 'wm mask' CORRECTION  ---
# copy from freesurfer dir to modification dir

# ---  AFTER 'wm mask' CORRECTION  ---
# copy the modificated back
# apply freesurfer with the corrected