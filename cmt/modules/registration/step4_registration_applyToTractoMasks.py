###############################################################################################
######  Apply the registration to the 'tracto masks' datasets from 'cmt' pipeline        ######
######  (i.e. fsmask_1mm.*, scale33/ROI_HR_th.* etc)                                     ######
######                                                                                   ######
######  These datasets MUST BE in the space/orientation of the 'T1' dataset, and after   ######
######  the script they'll be in the space/orientation of 'DSI_b0_resampled' dataset.    ######
###############################################################################################
#source "${CMT_HOME}/common_lib.sh"        # aux functions
#
## setup
#if [ $# != 5 ]; then
#    ERROR "SYNTAX:  $0 <PATIENT> <FROM time-point> <TO time-point> <gfa_GM_lb> <gfa_WM_lb>"
#fi

import sys

patient = sys.argv[1]
from_tp = sys.argv[2]
to_tp = sys.argv[3]
gfa_GM_lb = sys.argv[4]
gfa_WM_lb = sys.argv[5]

#PATIENT="$1"                    # name of the patient in the "REGISTRATION" subject folder
#FROM="$2"                        # the timepoint related to the FROM_SUBJECT_NAME subject in the "REGISTRATION" pipeline
#TO="$3"                            # the "destination" timepoint (where to move to) in the "REGISTRATION" pipeline (NB: FROM can be the same as TO, of course!)
#
#gfa_GM_lb="$4"                    # lower bound for GRAY MATTER tissue
#gfa_WM_lb="$5"                    # lower bound for WHITE MATTER tissue
#
## checking
#CHECK_DIR "${DATA_path}/${PATIENT}/${FROM}" "Missing '${FROM}' folder for patient '${PATIENT}' in '${DATA_path}'!"
#CHECK_DIR "${DATA_path}/${PATIENT}/${TO}" "Missing '${TO}' folder for patient '${PATIENT}' in '${DATA_path}'!"

#TRACTO_MASKS="${DATA_path}/${PATIENT}/${FROM}/4__CMT/fs_output/registred/HR"
#CHECK_DIR "${TRACTO_MASKS}" "Missing folder '${TRACTO_MASKS}'!"
#
#cd "${DATA_path}/${PATIENT}"
#
#
## create folder for the moving datasets (something like 'tracto_masks-FROM-tp3')
#rm -fR "${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0" > /dev/null
#
#mkdir -p "${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0"
#mkdir -p "${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0/scale33"
#mkdir -p "${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0/scale60"
#mkdir -p "${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0/scale125"
#mkdir -p "${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0/scale250"
#mkdir -p "${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0/scale500"
#
#LOG "'${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0' created"
#
#if [ ${REG_MODE} = 'N' ]; then
#    if [ $FROM == $TO ]; then
#        cp "${FROM}/2__NIFTI/T1-TO-T2.mat" "${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0/tmp_premat.mat"
#    else
#        convert_xfm \
#             -concat  "${TO}/2__NIFTI/T1-TO-T2.mat" "${FROM}-TO-${TO}.mat" \
#             -omat "${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0/tmp_premat.mat"
#    fi
#else
#    if [ $FROM == $TO ]; then
#        cp "${TO}/2__NIFTI/T1-TO-b0.mat" "${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0/tmp_premat.mat"
#    else
#        convert_xfm \
#             -concat  "${TO}/2__NIFTI/T1-TO-b0.mat" "${FROM}-TO-${TO}.mat" \
#             -omat "${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0/tmp_premat.mat"
#    fi
#fi
#
#
##########################################################################
## Apply the LINEAR/NONLINEAR registration to EACH OF THE NEXT datasets
##
#if [ ${REG_MODE} = 'N' ]; then
#    echo; LOG "Applying the NONLINEAR transformation '${FROM} --> ${TO}' to datasets in '${FROM}/4__CMT/fs_output/registred/HR'..."
#else
#    echo; LOG "Applying the LINEAR transformation '${FROM} --> ${TO}' to datasets in '${FROM}/4__CMT/fs_output/registred/HR'..."
#fi
#
#
#DATASETS=( 'fsmask_1mm' 'scale33/ROI_HR_th' 'scale60/ROI_HR_th' 'scale125/ROI_HR_th' 'scale250/ROI_HR_th' 'scale500/ROI_HR_th' )
#for D in ${DATASETS[@]}; do
#    LOG "   * Processing '${D}'..."
#
#    # apply the registration
#    if [ ${REG_MODE} = 'N' ]; then
#        applywarp \
#            --in="${TRACTO_MASKS}/${D}.nii" --premat="${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0/tmp_premat.mat" \
#            --ref="${TO}/2__NIFTI/DSI_b0_resampled.nii" --warp="${TO}/2__NIFTI/T2-TO-b0_warp.nii" \
#            --out="${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0/${D}.nii" --interp=nn
#    else
#        flirt -applyxfm \
#            -init "${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0/tmp_premat.mat" \
#            -in "${TRACTO_MASKS}/${D}.nii" \
#            -ref "${TO}/2__NIFTI/DSI_b0_resampled.nii" \
#            -out "${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0/${D}.nii" -interp nearestneighbour
#    fi
#    CHECK_FILE "${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0/${D}.nii" "Unable to apply the warp to '${D}'. There were some errors."
#
#    #if [ ${D} != 'fsmask_1mm' ]; then
#    #    cp "${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0/${D}.nii" "${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0/${D}__forRoiSizeCalc.nii"
#    #fi
#done
#
#rm -f "${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0/tmp_premat.mat"
#
#LOG "Chain of transformations succesfully applyed."
#
#
#####################################################################
## Fixing MISSING LABELS in transformed datasets...
##
#echo; LOG "Fixing MISSING LABELS in the transformed datasets..."
#
#CHECK_FILE "${DATA_path}/${PATIENT}/${TO}/4__CMT/raw_diffusion/odf_0/dsi_gfa.nii"
#CHECK_FILE "${DATA_path}/${PATIENT}/${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0/fsmask_1mm.nii"
#
#mri_convert \
#    -vs 1 1 1 \
#    "${DATA_path}/${PATIENT}/${TO}/4__CMT/raw_diffusion/odf_0/dsi_gfa.nii" \
#    "${DATA_path}/${PATIENT}/${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0/GFA_1x1x1.nii" &> /dev/null
#
#CHECK_FILE "${DATA_path}/${PATIENT}/${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0/GFA_1x1x1.nii"
#
#$MY_MATLAB "cd '${CMT_HOME}/registration'; fillHolesInLabels('${DATA_path}/${PATIENT}/${TO}/4__CMT/fs_output/registred/HR__registered-TO-b0',${gfa_GM_lb},${gfa_WM_lb}); exit;"
#
#LOG "Label datasets succesfully corrected."