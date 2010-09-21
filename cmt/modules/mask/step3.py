###############################################################################################################################################
###############################################  ROI_HR_th.nii / fsmask_1mm.nii CREATION  #####################################################
###############################################################################################################################################

# maybe use http://pypi.python.org/pypi/pymatlab/ to help conversion

# inputs:


# outputs:

echo; LOG "STEP 3a: Create the cortical labels necessary for our ROIs"
create_annot_label.sh &> /dev/null
LOG "[ DONE ]"

echo; LOG "STEP 3b: Create the ROIs"
$MY_MATLAB "roi_creation( '${MY_SUBJECT}','${MY_TP}' ); exit"
LOG "[ DONE ]"

echo; LOG "STEP 3c: Move datasets into 'fs_output/registred/HR' folder"
reorganize_stuff.sh
LOG "[ DONE ]"

 echo; LOG "STEP 3d: Create final ROI mask, cortex and deep gray structures"
 $MY_MATLAB "roi_merge( '${MY_SUBJECT}','${MY_TP}' ); exit"
 LOG "[ DONE ]"

echo; LOG "STEP 3e: Finalize WM mask"
$MY_MATLAB "mask_creation( '${MY_SUBJECT}','${MY_TP}' ); exit"
LOG "[ DONE ]"

 echo; LOG "STEP 3f: Finalize ROI mask"
 $MY_MATLAB "script_roi_finalize; exit"
 LOG "[ DONE ]"
