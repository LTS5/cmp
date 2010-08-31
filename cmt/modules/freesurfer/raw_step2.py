
#########################################################################################################################################
#######################################################  FREESURFER  ####################################################################
#########################################################################################################################################

#2a) Copy the 'ORIGINAL T1' to FREESURFER
if [  ]; then
    echo; LOG "STEP 2a: copying '2__NIFTI/T1.nii' dataset to '3__FREESURFER/mri/orig/001.mgz'..."

    CHECK_FILE "${DATA_path}/${MY_SUBJECT}/${MY_TP}/2__NIFTI/T1.nii"
        rm -f "${DATA_path}/${MY_SUBJECT}/${MY_TP}/3__FREESURFER/mri/orig/001.mgz"
        mri_convert \
            "${DATA_path}/${MY_SUBJECT}/${MY_TP}/2__NIFTI/T1.nii" \
            "${DATA_path}/${MY_SUBJECT}/${MY_TP}/3__FREESURFER/mri/orig/001.mgz" &> /dev/null
    CHECK_FILE "${DATA_path}/${MY_SUBJECT}/${MY_TP}/3__FREESURFER/mri/orig/001.mgz"

    LOG "[ DONE ]"
fi


#2b) ---  ALL FREESURFER PIPELINE  ---
if [  ]; then
    echo; LOG "STEP 2b: running the whole FREESURFER pipeline"

    recon-all -s "3__FREESURFER" -all -no-isrunning &> "${LOGDIR}/freesurfer.log"

    LOG "[ DONE ]"
fi


#2c) ---  BEFORE 'wm mask' CORRECTION  ---
if [  ]; then
    echo; LOG "STEP 2c: copy stuff for correcting the 'wm mask' to '${WM_EXCHANGE_FOLDER}/${XXX_SUBJECT}'"

    CHECK_FILE "${DATA_path}/${MY_SUBJECT}/${MY_TP}/3__FREESURFER/mri/T1.mgz"
    CHECK_FILE "${DATA_path}/${MY_SUBJECT}/${MY_TP}/3__FREESURFER/mri/wm.mgz"

    mkdir -p "${WM_EXCHANGE_FOLDER}/${MY_SUBJECT}/${MY_TP}"

    rm -f "${WM_EXCHANGE_FOLDER}/${MY_SUBJECT}/${MY_TP}/T1.nii"
    rm -f "${WM_EXCHANGE_FOLDER}/${MY_SUBJECT}/${MY_TP}/wm.nii"
        mri_convert "${DATA_path}/${MY_SUBJECT}/${MY_TP}/3__FREESURFER/mri/T1.mgz" "${WM_EXCHANGE_FOLDER}/${MY_SUBJECT}/${MY_TP}/T1.nii"  > /dev/null
        mri_convert "${DATA_path}/${MY_SUBJECT}/${MY_TP}/3__FREESURFER/mri/wm.mgz" "${WM_EXCHANGE_FOLDER}/${MY_SUBJECT}/${MY_TP}/wm.nii"  > /dev/null
    CHECK_FILE "${WM_EXCHANGE_FOLDER}/${MY_SUBJECT}/${MY_TP}/T1.nii" "Unable to convert the file '${MY_SUBJECT}/${MY_TP}/mri/T1.mgz'!"
    CHECK_FILE "${WM_EXCHANGE_FOLDER}/${MY_SUBJECT}/${MY_TP}/wm.nii" "Unable to convert the file '${MY_SUBJECT}/${MY_TP}/mri/wm.mgz'!"

    LOG "[ DONE ]"
fi


#2d) ---  AFTER 'wm mask' CORRECTION  ---
if [  ]; then
    echo; LOG "STEP 2d: copying back the corrected 'wm mask' from '${WM_EXCHANGE_FOLDER}/${XXX_SUBJECT}'"
    CHECK_FILE "${WM_EXCHANGE_FOLDER}/${MY_SUBJECT}/${MY_TP}/wm_corrected.nii"

    rm -f "${DATA_path}/${MY_SUBJECT}/${MY_TP}/3__FREESURFER/mri/wm.mgz"
    mri_convert -odt uchar "${WM_EXCHANGE_FOLDER}/${MY_SUBJECT}/${MY_TP}/wm_corrected.nii" "${DATA_path}/${MY_SUBJECT}/${MY_TP}/3__FREESURFER/mri/wm.mgz" > /dev/null
    CHECK_FILE "${DATA_path}/${MY_SUBJECT}/${MY_TP}/3__FREESURFER/mri/wm.mgz" "Unable to convert the file '3__FREESURFER/mri/wm.mgz'!"

    LOG "[ DONE ]"

    echo; LOG "STEP 2d: running FREESURFER on the corrected 'wm.mgz' file"
    recon-all -s "3__FREESURFER" -autorecon2-wm -autorecon3 -no-isrunning &> "${LOGDIR}/freesurfer.log"
    LOG "[ DONE ]"
fi
