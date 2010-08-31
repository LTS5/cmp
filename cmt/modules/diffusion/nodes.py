#########################################################################################################################################
#####################################################  DIFFUSION TOOLKIT  ###############################################################
#########################################################################################################################################

import nipype.interfaces.io as nio # Data i/o
import nipype.interfaces.fsl as fsl # fsl
import nipype.interfaces.diffusion_toolkit as dtk
import nipype.interfaces.utility as util # utility
import nipype.interfaces.freesurfer as fs
import nipype.pipeline.engine as pe # pypeline engine

# for the pipeline, we need more registration

diffusionWorkflow = pe.Workflow(name="diffusion")
diffusionWorkflow.base_dir()

# mkdir -p "${DATA_path}/${MY_SUBJECT}/${MY_TP}/4__CMT/raw_diffusion"
# -> the output directory

# "STEP 4a: Resample the DSI dataset to 2x2x2 mm^3"
# --------------

# resample the dataset to 2x2x2, using freesurfer 4.5 with mri_convert possible for 4th dimension as well?

# fslsplit "${DATA_path}/${MY_SUBJECT}/${MY_TP}/2__NIFTI/DSI.nii" "MR" -t
# See http://nipy.sourceforge.net/nipype/interfaces/generated/nipype.interfaces.fsl.utils.html

# the dataset is split in the t-dimension, yielding (e.g. 512) 3d images corresponding to
# different gradient directions

#for file in $( ls MR*.nii ); do

# for all gradient directions, the data is resampled

#        mri_convert -vs 2 2 2 $file tmp.nii &> /dev/null

resamp = fs.MRIConvert(in_file='XXX.nii', out_file='XXX.nii', vox_size = (2.0, 2.0, 2.0))

#        fslmaths tmp.nii $file -odt short

maths = fsl.ImageMaths(in_file='XXX.nii', op_string= '-odt short',
                       out_file='XXX.nii')


#"STEP 4b: Compute the ODFs field(s)"

#    for sharpness in ${SHARPs[@]}; do
#         mkdir -p "odf_${sharpness}"
#
#        # calculate ODF map
#         rm -f "odf_${sharpness}/dsi_"*
#         odf_recon \
#             "2x2x2/MR0000.nii" \
#             515 181 \
#             "odf_${sharpness}/dsi_" \
#             -b0 1 -mat "DSI_matrix_515x181.dat" -dsi -p 4 -sn 0 -ot nii -s ${sharpness}
#         CHECK_FILE "odf_${sharpness}/dsi_odf.nii" "Unable to reconstruct ODF!"

#        # calculate GFA map
#        rm -f "odf_${sharpness}/dsi_gfa.nii"
#        "${CMT_HOME}/c++/bin"/DTB_gfa --dsi "odf_${sharpness}/dsi_"
#        CHECK_FILE "odf_${sharpness}/dsi_gfa.nii" "Unable to calculate GFA map!"
#    done

odf_map = dtk.ODFRecon()

# see work from dan
# http://github.com/chrisfilo/nipype/blob/cdbf67ab90fabb2b1e0d325917d6a9f9dd42d34a/nipype/interfaces/diffusion_toolkit/preproc.py