# See http://nipy.sourceforge.net/nipype/interfaces/generated/nipype.interfaces.fsl.preprocess.html
# See http://www.mit.edu/~satra/nipype-nightly/interfaces/generated/nipype.interfaces.freesurfer.preprocess.html

# Converts 'T1/T2/DSI' datasets from DICOM to NIFTI
#####################
# preprocessing steps

# use diff_unpack or nibabel for DSI/T1?

# resample "b0" to 1x1x1 mm^3 pixdim
#mri_convert \
#    -vs 1 1 1 \
#   "DSI.nii" \
#    "DSI_b0_resampled.nii"

from nipype.interfaces.freesurfer import MRIConvert
mc = MRIConvert()
mc.inputs.in_file = 'DSI.nii'
mc.inputs.out_file = 'DSI_b0_resampled.nii'
mc.inputs.vox_size = (1.0, 1.0, 1.0)

# change orientation of "T1" to fit "b0"
# "${CMT_HOME}/registration"/nifti_reorient_like.sh "T1.nii" "DSI.nii"
# what to use here?
# there are first checking of the orientations, then do them accordingly
# where to put this logic? i guess not inside a node
# i think we should seperate this as a preprocessing step?

# uses fslswapdim, fslorient

# case distinction when T2 is available!
# do diff_unpack and reorient

# Started FLIRT to find 'T1 --> b0' linear transformation
#####################
# Node already implemented for 
 #flirt \
#    -in "T1.nii" -ref "DSI_b0_resampled.nii" \
#    -usesqform -nosearch -dof 6 -cost mutualinfo \
#    -out "T1-TO-b0.nii" -omat "T1-TO-b0.mat"
    
import nipype.interfaces.fsl as fsl

applyxfm = fsl.ApplyXfm()
applyxfm.inputs.in_file = example_data('T1.nii')
applyxfm.inputs.out_file = 'T1-TO-b0.nii'
applyxfm.input.out_matrix_file = 'T1-TO-b0.mat'
applyxfm.inputs.reference = 'DSI_b0_resampled.nii'
applyxfm.inputs.cost = 'mutualinfo'
applyxfm.inputs.dof = 6
applyxfm.inputs.no_search = True
applyxfm.inputs.uses_qform = True
result = applyxfm.run() 

# check results
# -> this needs to go in a DataSink for inspection after the registration pipeline 
#fslview \
#    "DSI_b0_resampled.nii" \
#    "T1-TO-b0.nii" -l Copper -t 0.5


#####################################################################################################################################
##############################################  Apply registration ROI/WM --> b0  ###################################################
#####################################################################################################################################
