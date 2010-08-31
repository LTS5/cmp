
#1a) DICOM -> NIFTI conversion/reprientation as DSI (for this PATIENT and this TIME POINT)
if [  ]; then
    echo; LOG "STEP 1a: DICOM -> NIFTI conversion"

    "${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 1 "${MY_SUBJECT}" "${MY_TP}"        # [TODO] account for LINEAR/NONLINEAR MODE (T2 could be absent for LINEAR registration)

    LOG "[ DONE ]"
fi



#1b) Registration BETWEEN TIME-POINTS
if [  ]; then
    echo; LOG "STEP 1b: registration BETWEEN TIME-POINTS"

    # Create LESION MASKS (only if necessary, if there are big lesions, and perform it ON EACH TIME POINT)
    #"${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 2a "${MY_SUBJECT}" "${MY_TP}"

    # Find an affine TRANSFORMATION BETWEEN TIME POINTS using the T1s (generally TP3 -> TP2, TP3 -> TP1 etc)
    "${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 2b "${MY_SUBJECT}" "${MY_TP}" "${FROM_TP}"

    LOG "[ DONE ]"
fi


#1c) T1 -> b0 (LINEAR/NONLINEAR) registration in one time-point
if [  ]; then
    if [ ${REG_MODE} = 'N' ]; then
        echo; LOG "STEP 1c: T1 -> T2 -> b0 NONLINEAR registration"

        # LINEAR register T1 --> b0
        "${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 3a "${MY_SUBJECT}" "${MY_TP}" 1.1
        "${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 3a "${MY_SUBJECT}" "${MY_TP}" 1.2
        "${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 3a "${MY_SUBJECT}" "${MY_TP}" 1.3

        # Create BINARY MASKS needed for nonlinear registration
        "${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 3a "${MY_SUBJECT}" "${MY_TP}" 2.1 0.2 0.3        # T2 mask
        "${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 3a "${MY_SUBJECT}" "${MY_TP}" 2.2 0.2 0.2        # b0 mask

        # NONLINEAR register T1 --> b0
        "${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 3a "${MY_SUBJECT}" "${MY_TP}" 3

        LOG "[ DONE ]"
    else
        echo; LOG "STEP 1c: T1 -> b0 LINEAR registration"

        "${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 3b "${MY_SUBJECT}" "${MY_TP}"

        LOG "[ DONE ]"
    fi
fi
