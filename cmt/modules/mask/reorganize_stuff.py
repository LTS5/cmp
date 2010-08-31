#!/bin/bash
source "${CMT_HOME}/common_lib.sh"    # include my functions


cd "${DATA_path}/${MY_SUBJECT}/${MY_TP}/3__FREESURFER"
CHECK_FILE "mri/orig/001.mgz" "Unable to locate 'mri/orig/001.mgz' dataset REQUIRED for retrieving T1's original geometry!"


# crop to the "space of original T1"
echo; LOG " * Cropping datasets to ORIGINAL GEOMETRY of T1..."
DATASETS=( \
     'mri/aseg' 'mri/ribbon' 'label/cc_unknown' \
     'label/regenerated_lh_35/ROI_lh'  'label/regenerated_rh_35/ROI_rh' \
     'label/regenerated_rh_60/ROI_rh'  'label/regenerated_lh_60/ROI_lh'  \
    'label/regenerated_rh_125/ROI_rh' 'label/regenerated_lh_125/ROI_lh' \
    'label/regenerated_rh_250/ROI_rh' 'label/regenerated_lh_250/ROI_lh' \
    'label/regenerated_rh_500/ROI_rh' 'label/regenerated_lh_500/ROI_lh' \
)
for D in ${DATASETS[@]}; do
    echo; LOG " * '${D}'..."

    mri_convert -rl "mri/orig/001.mgz" -rt nearest "${D}.nii" -nc "${D}_tmp.nii"
    mv "${D}_tmp.nii" "${D}.nii"
done



# create subfolders in '4__CMT' folder
cd "${DATA_path}/${MY_SUBJECT}/${MY_TP}/4__CMT"
rm -fR "fs_output/registred/HR"
mkdir -p "fs_output/registred/HR"

cd "fs_output/registred/HR"
mkdir -p scale33
mkdir -p scale60
mkdir -p scale125
mkdir -p scale250
mkdir -p scale500


# copy datasets from '3__FREESURFER' folder
SOURCE_path="${DATA_path}/${MY_SUBJECT}/${MY_TP}/3__FREESURFER"
mv ${SOURCE_path}/mri/aseg.nii         .
mv ${SOURCE_path}/mri/ribbon.nii       .
mv ${SOURCE_path}/label/cc_unknown.nii .

mv ${SOURCE_path}/label/regenerated_lh_35/ROI_lh.nii  scale33/.
mv ${SOURCE_path}/label/regenerated_lh_60/ROI_lh.nii  scale60/.
mv ${SOURCE_path}/label/regenerated_lh_125/ROI_lh.nii scale125/.
mv ${SOURCE_path}/label/regenerated_lh_250/ROI_lh.nii scale250/.
mv ${SOURCE_path}/label/regenerated_lh_500/ROI_lh.nii scale500/.

mv ${SOURCE_path}/label/regenerated_rh_35/ROI_rh.nii  scale33/.
mv ${SOURCE_path}/label/regenerated_rh_60/ROI_rh.nii  scale60/.
mv ${SOURCE_path}/label/regenerated_rh_125/ROI_rh.nii scale125/.
mv ${SOURCE_path}/label/regenerated_rh_250/ROI_rh.nii scale250/.
mv ${SOURCE_path}/label/regenerated_rh_500/ROI_rh.nii scale500/.